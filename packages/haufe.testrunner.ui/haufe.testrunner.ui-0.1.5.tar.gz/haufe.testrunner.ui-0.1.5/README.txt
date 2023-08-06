haufe.testrunner.ui
===================

``haufe.testrunner.ui`` is a Grok-based web-frontend for
accessing the results of haufe.testrunner runs

Installation
------------

- check out the code from SVN
- run ``buildout``
- run ``bin/zopectl fg|start|stop``

To do
-----

- The code contains a bunch of redundancies and must be refactored.
- The SQLAlchemy related code must be cleaned-up (select() is deprecated)


Author
------
Andreas Jung
