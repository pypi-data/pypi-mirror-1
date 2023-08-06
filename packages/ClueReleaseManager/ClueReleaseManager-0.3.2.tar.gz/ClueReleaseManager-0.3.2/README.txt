.. -*-rst-*-

============
Introduction
============

ClueReleaseManager is an implementation of the PyPi server backend as provided
by http://pypi.python.org.  It uses SQLAlchemy (on top of sqlite by default)
to store all project metadata and the filesystem for storing project files.

Current Features
================

  * User registration via setuptools
  * File upload (ie eggs) via setuptools
  * Basic authentication based security
  * Simple index browsing

Upcoming Features
=================

  * Full http://pypi.python.org PyPi server compatibility

Requirements
============

  * Python 2.5
  * setuptools
  * SQLAlchemy 0.5rc4 or higher
  * repoze.who 1.0.8 or higher
  * Werkzeug 0.4 or higher (less than 0.5 which has issues)

Installation
============

Install using the ``easy_install`` tool such as::

  $ easy_install ClueReleaseManager

Usage
=====

Once ClueReleaseManager is installed, the script cluerelmgr-server will
be created to launch the server.  See ``cluerelmgr-server --help`` for
further usage details.

By default ClueReleaseManager will create a ``cluerelmgr.db`` sqlite3 db
file in the current directory (where the server is running from).  It
will also create a ``files`` directory in the same place which is used
to store all uploaded files.

Use the ``cluerelmgr-admin`` script to setup initial configuration.  The
following example configures a new user, adds them to a managers group,
and gives the manager group all access to all distros::

  $ cluerelmgr-admin updateuser user1 somepass someemail
  $ cluerelmgr-admin updategroup managers adddistro reader
  $ cluerelmgr-admin updateusersgroups user1 managers

Want to give anonymous users access to everything?  (The anonymous user
is a special user that cannot have a password named ``anonymous``) You
can now just add them to the newly created ``managers`` group::

  $ cluerelmgr-admin updateusersgroups anonymous managers

User registration can occur through the standard
``python setup.py register <someproject>`` command (which gives you an option
for registration) or by manually inserting a user record into the
``cluerelmgr.db`` file.

Server Command-Line Options
---------------------------

::

    Usage: cluerelmgr-server [options]

    Options:
      -h, --help            show this help message and exit
      -p PORT, --port=PORT  Port to listen on, defaults to 8080
      -i HOST, --interface=HOST
                            Host to listen on, defaults to 0.0.0.0
      -b BASEFILEDIR, --basefiledir=BASEFILEDIR
                            Base directory to store uploaded files,
                            defaults to files
      -d, --debug           Activate debug mode
      -s, --self-register   Allow self-registration
      -u BASEURL, --baseurl=BASEURL
                            The base url used in case of proxying
      --security-config=SECURITY_CONFIG
                            Use a separate configuration file to declare
                            the repoze.who config. See
                            http://static.repoze.org/whodocs
                            /#middleware-configuration-via-config-file
                            for details.
      --backup-pypi=BACKUP_PYPIS
                            Python indexes to fall back to.  When backup
                            index servers are configured they will be
                            queried if the user browsing this server has
                            the adddistro role and the this server will
                            be updated with all metadata and files.

Credits
=======

Created and maintained by Rocky Burt <rocky@serverzen.com>.

