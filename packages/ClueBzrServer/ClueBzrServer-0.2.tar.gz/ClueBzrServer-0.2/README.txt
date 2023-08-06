.. -*-rst-*-

=============
ClueBzrServer
=============

Introduction
============

ClueBzrServer is a http server designed to serve up arbitrary bzr directories
in configurable way.  Authentication and authorization can be configured
via config files.

Installation
============

The preferred manner of setup is to install ClueBzrServer within a
virtualenv_.  Older instructions for setting up virtualenv can be found
at `Setting up virtualenv`_.  Once the virtualenv is setup just use
``easy_install`` in the traditional way.  For example::

  $ easy_install ClueBzrServer


Usage
=====

Running the Server
------------------

Once ClueBzrServer is installed, running ``clue-bzrserver`` the first time
will generate a standard config file with all access turned off (for
security reasons).

This will serve the currect directory as a bzr source::

  $ clue-bzrserver

To specify an alternate port to the default 8080, try::

  $ clue-bzrserver -p 9339

Display the ``--help`` arg for usage info::

  $ clue-bzrserver --help

The default configuration will be generated at ``clue-bzrserver.ini`` in the
same directory.  It is configured to use htpasswd based access by looking
at the file ``clue-bzrserver.passwd`` in the same directory.  Use the
standard apache2 ``htpasswd`` tool to update username/password entries.

At this point you should setup your first user account by doing something
like follows (assumes apache2 ``htpasswd`` utility is available somewhere
on the path)::

  $ htpasswd clue-bzrserver.passwd testuser1

The complete format of ``clue-bzrserver.ini`` for allowing access
such as SQL or LDAP is dictated by the repoze.who_ project.  See
`repoze.who security`_ for details.


ACL Security
------------

Security can be defined on a per branch basis.  It gets defined inside
the ``clue-bzrserver.ini`` file.  Here's an example::

  [authz:MyProject/trunk]
  anonymous = r
  testuser1 = rw


Connecting to the Server
------------------------

After you have launched the server for the first time the simplest way
to get started is as follows::

  $ bzr init-repo --no-trees --1.9 bzr+http://testuser1:mypassword@localhost:8080/MyProject

Now go ahead and start your new project (or work within an existing
non-versioned directory).  Lets assume you're working on a project called
"MyProject" and now want to turn what you have into the trunk::

  $ cd MyProject
  $ bzr init
  $ bzr push --create-prefix bzr+http://testuser1:mypassword@localhost:8080/MyProject/trunk

Once you make some changes, you commit then as you normally would::

  $ bzr commit

And then you have to make sure to push your local commits to the parent
branch which in this case is the remote trunk::

  $ bzr push


License
=======

ClueBzrServer is covered under a BSD license.  See ``LICENSE.txt`` for
further details.


Credits
=======

Written and maintained by Rocky Burt (rocky AT serverzen DOT com).

.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _repoze.who: http://pypi.python.org/pypi/repoze.who/
.. _`repoze.who security`: http://static.repoze.org/whodocs/narr.html#middleware-configuration-via-config-file
.. _`Setting up virtualenv`: http://neuroimaging.scipy.org/site/doc/manual/html/devel/tools/virtualenv-tutor.html
