Installation
============

This package allows you to install Zine and its dependencies in a sandbox with
buildout, then serve it with any WSGI server while using the Paste facilities
for WSGI stack configuration.

Install Zine:
-------------
Download and extract the zinebuildout archive from PyPI,
(or clone it with: hg clone https://cody.gorfou.fr/hg/zinebuildout )
then run: ::

  $ python bootstrap.py
  $ ./bin/buildout

Configure Zine:
---------------
Then create an empty dir for your instance and edit "deploy.ini" to change
the ``instance_folder``, ``host`` and ``port``.

Start Zine:
-----------

In foreground: ::

  $ ./bin/paster serve deploy.ini

Or in background: ::

  $ ./bin/paster serve --daemon deploy.ini

Versions
========

0.2 2009-01-27
--------------
- move to zine 0.1.2
- no more need to configure the instance folder
- Added pygments and docutils (for the rst parser)

0.1 2009-01-14
--------------

initial buildout for Zine 0.1.1
