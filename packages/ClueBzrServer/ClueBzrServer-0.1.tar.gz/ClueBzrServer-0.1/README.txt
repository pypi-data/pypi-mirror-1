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
virtualenv_.  At this point simply use ``easy_install`` in the traditional
way.  For example::

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

This will serve ``/tmp/foo`` as a bzr source::

  $ clue-bzrserver /tmp/foo

To specify an alternate port to the default 8080, try::

  $ clue-bzrserver /tmp/foo 9339

The default configuration will be generated at ``clue-bzrserver.ini`` in the
same directory.  It is configured to use htpasswd based access by looking
at the file ``clue-bzrserver.passwd`` in the same directory.  Use the
standard apache2 ``htpasswd`` tool to update username/password entries.

At this point you should setup your first user account by doing something
like follows (assumes apache2 ``htpasswd`` utility is available somewhere
on the path)::

  $ htpasswd clue-bzrserver.passwd testuser1


Connecting to the Server
------------------------

After you have launched the server for the first time the simplest way
to get started is as follows::

  $ bzr init-repo --no-trees --1.9 bzr+http://testuser1:mypassword@localhost:8080/

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


Credits
=======

Written and maintained by Rocky Burt (rocky AT serverzen DOT com).

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

