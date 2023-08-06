.. -*-rst-*-

Introduction
============

CluePyPi is an implementation of the PyPi server backend as provided
by http://pypi.python.org.  It uses SQLAlchemy (on top of sqlite by default)
to store all project metadata and the filesystem for storing project files.

Requirements
------------

  * Python 2.5
  * setuptools
  * WebOb 0.9.4 or higher
  * SQLAlchemy 0.5rc4 or higher
  * repoze.who 1.0.8 or higher

Installation
------------

Install using the ``easy_install`` tool such as::

  $ easy_install ClueReleaseManager

Usage
-----

Once ClueReleaseManager is installed, the script cluerelmgr-server will
be created to launch the server.  See ``cluerelmgr-server --help`` for
further usage details.

Credits
-------

Created and maintained by Rocky Burt <rocky@serverzen.com>.
