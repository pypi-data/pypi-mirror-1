import os
import sys
import logging
from wsgiref import simple_server
from bzrlib.transport.http import wsgi
from repoze.who import config as whoconfig

_logger = logging.getLogger('clue.bzrserver')
_logger.setLevel(level=logging.DEBUG)


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


class BzrServerApp(object):

    def __init__(self, sourcedir, prefix, configfile, logger):
        self.inner = BzrInnerApp(sourcedir, prefix, logger)
        self.app = whoconfig.make_middleware_with_config(
            self.inner, {'here': os.getcwd()}, configfile)
        self.logger = logger

    def __call__(self, environ, start_req):
        return self.app(environ, start_req)


class BzrInnerApp(object):

    def __init__(self, sourcedir, prefix, logger):
        self.bzrapp = wsgi.make_app(root=sourcedir,
                                    prefix=prefix,
                                    path_var='PATH_INFO',
                                    readonly=False,
                                    load_plugins=True,
                                    enable_logging=False)
        self.logger = logger

    def __call__(self, environ, start_req):
        p = environ.get('PATH_INFO', '')
        suffix = '/.bzr/smart'
        if p.endswith(suffix):
            p = p[:-len(suffix)]
            self.logger.info('access - %s' % p)
        if not environ.get('REMOTE_USER', None):
            start_req('401 User must be authenticated', [])
            return []
        return self.bzrapp(environ, start_req)


def make_app(global_conf, sourcedir, prefix, configfile, logger=_logger):
    return BzrServerApp(sourcedir, prefix, configfile, logger)


class Server(object):
    default_ini = DEFAULT_INI
    logger = _logger
    info = logger.info

    def run_server(self, args=[]):
        root = os.getcwd()
        if len(args) > 0:
            root = args[0]
        root = os.path.abspath(root)
        parts = [x for x in os.path.split(root) if x]
        configfile = 'clue-bzrserver.ini'
        passwdfile = 'clue-bzrserver.passwd'
        if not os.path.exists(configfile):
            self.info('Creating file %s' % configfile)
            f = open(configfile, 'w')
            f.write(self.default_ini)
            f.close()
            self.info('Creating file %s' % passwdfile)
            f = open(passwdfile, 'w')
            f.write('')
            f.close()

        self.info('Serving path: %s' % root)
        self.info('Config: %s' % configfile)
        self.info('Passwd: %s' % passwdfile)

        app = make_app({}, root, '', configfile, self.logger)
        port = 8080
        if len(args) > 1:
            port = int(args[1])

        class RequestHandler(simple_server.WSGIRequestHandler):

            def log_request(self, *args, **kw):
                # hide the standard http access messages
                pass

        httpd = simple_server.make_server('', port, app,
                                          handler_class=RequestHandler)

        self.info('Now listening on port %i' % port)
        httpd.serve_forever()


def main(args=None, extraargs=None):
    logging.basicConfig()
    if args is None:
        args = []
    if extraargs is None:
        extraargs = sys.argv[1:]
    Server().run_server(args + extraargs)


if __name__ == '__main__':
    main()
