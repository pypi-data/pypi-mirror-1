from __future__ import with_statement
import os
import ConfigParser
import StringIO
from paste import urlparser
from bzrlib import errors
from bzrlib.transport import chroot
from bzrlib.transport.http import wsgi
from repoze.who import config as whoconfig
from repoze.who.plugins import htpasswd
from clue.bzrserver import utils
import threading


DEFAULT_INI = """[plugin:basicauth]
use = repoze.who.plugins.basicauth:make_plugin
realm = 'clue-bzrserver'

[plugin:htpasswd]
use = repoze.who.plugins.htpasswd:make_plugin
filename = %(here)s/clue-bzrserver.passwd
check_fn = repoze.who.plugins.htpasswd:crypt_check

[general]
request_classifier = repoze.who.classifiers:default_request_classifier
challenge_decider = repoze.who.classifiers:default_challenge_decider
remote_user_key = REMOTE_USER

[identifiers]
plugins =
      basicauth

[authenticators]
plugins =
      htpasswd

[challengers]
plugins =
      basicauth
"""

_request_info = threading.local()
_request_info.username = 'anonymous'
_request_info.error = None


def parse_ini_security(f):
    parser = ConfigParser.SafeConfigParser()
    if hasattr(f, 'read'):
        parser.readfp(f)
    else:
        parser.readfp(StringIO.StringIO(f))

    security = SecurityChecker()
    for section in parser.sections():
        if section.startswith('authz:'):
            security.add_rule(section[6:], parser.items(section))

    return security


class SecurityChecker(object):

    def __init__(self):
        self._rules = {}

    def add_rule(self, branchpath, users):
        userdict = {}
        for k, v in users:
            userdict[k] = v

        self._rules[branchpath] = userdict

    def _uval(self, path):
        global _request_info
        user = _request_info.username
        rule = self._rules.get(path, None)
        if not rule:
            return ''
        return rule.get(_request_info.username, '')

    def can_read(self, path):
        return 'r' in self._uval(path)

    def can_write(self, path):
        return 'w' in self._uval(path)


class SecuredBzrApp(object):
    default_ini = DEFAULT_INI

    def __init__(self, sourcedir, passwdfile=None, configfile=None,
                 logger=utils.logger):
        self.logger = logger

        parser = whoconfig.WhoConfig(os.getcwd())
        parser.parse(StringIO.StringIO(self.default_ini))

        self.security = None
        if configfile:
            if os.path.exists(configfile):
                self.logger.info('Config file: %s' % configfile)
                with open(configfile) as f:
                    parser.parse(f)
                with open(configfile) as f:
                    self.security = parse_ini_security(f)

        if self.security is None:
            if configfile:
                self.logger.info('Config file at "%s" does not exist, skipping'
                                 % configfile)
            self.logger.info('No extra configuration loaded')
            self.security = SecurityChecker()

        pwdplugin = None
        for x in parser.plugins.values():
            if isinstance(x, htpasswd.HTPasswdPlugin):
                pwdplugin = x
                break

        if passwdfile:
            if os.path.exists(passwdfile):
                if pwdplugin is not None:
                    pwdplugin.filename = passwdfile
                else:
                    self.logger.warn('No authenticator plugin has been '
                                     'configured to accept the passwd '
                                     'argument')
            else:
                self.logger.warn('Could not find passwd file, %r' % passwdfile)

        if pwdplugin is not None:
            self.logger.info('Config passwd file: %s' % pwdplugin.filename)

        self.app = whoconfig.PluggableAuthenticationMiddleware(
            BzrServerApp(sourcedir, logger, security=self.security),
            parser.identifiers,
            parser.authenticators,
            parser.challengers,
            parser.mdproviders,
            parser.request_classifier,
            parser.challenge_decider,
            utils.security_logger, None,
            parser.remote_user_key,
           )

    def __call__(self, environ, start_req):
        return self.app(environ, start_req)


class BzrServerApp(object):

    def __init__(self, sourcedir, logger, security=None):
        self.security = security
        self.bzrapp = make_bzrlib_app(security=security,
                                      root=sourcedir,
                                      prefix='',
                                      path_var='PATH_INFO',
                                      readonly=False,
                                      load_plugins=True,
                                      enable_logging=False)
        self.staticapp = urlparser.make_url_parser({}, sourcedir, '')
        self.logger = logger

    def __call__(self, environ, start_req):
        global _request_info
        username = environ.get('REMOTE_USER', 'anonymous').strip().lower()
        _request_info.username = username
        _request_info.error = None

        p = environ.get('PATH_INFO', '')
        m = environ['REQUEST_METHOD']
        suffix = '/.bzr/smart'

        if p.endswith(suffix) and m.lower() == 'post':
            res = self.bzrapp(environ, start_req)
            if isinstance(_request_info.error, errors.PermissionDenied):
                if not environ.get('REMOTE_USER', None):
                    start_req('401 User must be authenticated', [])
                    return []

            return res

        return self.staticapp(environ, start_req)


def make_secured_app(global_conf,
                     sourcedir,
                     passwdfile=None,
                     configfile=None,
                     logger=utils.logger):

    return SecuredBzrApp(sourcedir, passwdfile, configfile,
                         logger)


class ACLTransport(chroot.ChrootTransport):

    read = ['get', 'has', 'stat']
    write = ['mkdir', 'put_file', 'delete', 'rename', 'rmdir']

    def __init__(self, security, backing_transport):
        self.security = security
        self.backing_transport = backing_transport

    def _call(self, methodname, relpath, *args):
        print methodname, relpath
        if methodname not in self.read \
               and methodname not in self.write:
            raise errors.BzrError(
                'Operation not supported: %s' % methodname)
        if relpath.find('/.bzr/branch/') > -1:
            branch = relpath[:relpath.find('/.bzr')]
            global _request_info
            print 'User: %s;  branch: %s' % (_request_info.username, branch)
            if self.backing_transport.has(
                os.path.join(branch, '.bzr', 'branch')):

                if methodname in self.read \
                       and not self.security.can_read(branch):
                    _request_info.error = errors.PermissionDenied(
                        'No read access to branch: %s' % branch)
                    raise _request_info.error
                if methodname in self.write \
                       and not self.security.can_write(branch):
                    _request_info.error = errors.PermissionDenied(
                        'No write access to branch: %s' % branch)
                    raise _request_info.error

        method = getattr(self.backing_transport, methodname)
        return method(relpath, *args)

    def _safe_relpath(self, relpath):
        return relpath


def make_bzrlib_app(security, root, prefix,
                    path_var='REQUEST_URI', readonly=True,
                    load_plugins=True, enable_logging=True):
    """Convenience function to construct a WSGI bzr smart server.

    :param root: a local path that requests will be relative to.
    :param prefix: See RelpathSetter.
    :param path_var: See RelpathSetter.
    """
    local_url = wsgi.local_path_to_url(root)
    if readonly:
        base_transport = wsgi.get_transport('readonly+' + local_url)
    else:
        base_transport = wsgi.get_transport(local_url)
    base_transport = ACLTransport(security, base_transport)
    if load_plugins:
        from bzrlib.plugin import load_plugins
        load_plugins()
    if enable_logging:
        import bzrlib.trace
        bzrlib.trace.enable_default_logging()
    app = wsgi.SmartWSGIApp(base_transport, prefix)
    app = wsgi.RelpathSetter(app, '', path_var)
    return app
