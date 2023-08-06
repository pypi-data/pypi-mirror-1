.. -*-rst-*-

=======
ClueBin
=======


Overview
========

ClueBin is a pastebin application with colour-syntax support for most major
text formats.  It is implemented as a WSGI application and easily integrates with
WSGI stacks.  The data backend is configurable and currently there are datastores
for Google App Engine (BigTable) and SQLAlchemy (SQLite by default).

Test the live version at http://cluebin.appspot.com


Dependencies
============

  * (required) Python 2.5+

  * (required) Pygments 0.9+

  * (required) WebOb 0.9.1+

  * (optional) SQLAlchemy: only required if you want SQL-based datastore support

  * (optional) Google Apps SDK: only required if deployed on the Google App
    Engine


Installation
============

ClueBin was designed to be installed using standard easy_install methods.  A
simple "easy_install ClueBin" should suffice.  This should generate a new
script called ``cluebin``.


Usage
=====

ClueBin was designed to be a pluggable WSGI app.  The factory for this app is
``cluebin.pastebin.make_app``.

To setup ClueBin within it's own constrained directory try using virtualenv
from http://pypi.python.org/pypi/virtualenv/1.0  Once virtualenv is installed
do this::

  $ virtualenv cluebinenv
  $ cd cluebinenv
  $ ./bin/easy_install SQLAlchemy
  $ ./bin/easy_install ClueBin

To use ClueBin in stand-alone mode, run the ``cluebin`` script.  See the help
usage for standard information.
::

  $ ./bin/cluebin -h

Here is an example of running ClueBin against a local ``foo.db`` sqlite db.
Make sure your local PYTHONPATH includes both SQLAlchemy and python SQLite
bindings.
::

  $ ./bin/cluebin -s cluebin.sqldata.SqlPasteDataStore sqlite:///foo.db True

The ``-s`` option takes some random datastore factory name.  All extra arguments
are passed as arguments to the factory call.  For the sql based datastore
the current arguments are "db-uri" and an optional second argument to determine
if the base schema should be auto-created.


Credits
=======

  * Rocky Burt (maintainer) - rocky AT serverzen DOT com

  * Nate Aune - natea AT jazkarta DOT com
