=============
Gerald README
=============

Introduction
============

Gerald is a general purpose toolkit for managing and deploying database schemas. Its major current use is to identify the differences between various versions of a schema.

In addition to Gerald you will need to have one or more relational databases and appropriate Python DB-API modules to access them.

Gerald currently supports the following relational database management systems;

 * MySQL - 4.1 and above
 * PostgreSQL - 8.1 and above
 * Oracle - 9i and above

For more information see the project web site at http://halfcooked.com/code/gerald/

Bugs, patches and feature requests should be submitted to andy47@halfcooked.com

The source code for this project is held in a subversion repository. To get a copy of the latest release try::

$ svn checkout https://halfcooked.svn.sourceforge.net/svnroot/halfcooked/tags/release-0.2.4/ <target>

This code has only been tested with Python 2.5 and above. Version 0.2 and above have been developed with Python 2.5, they may not work on earlier versions. The unit tests will definitely not work in versions before 2.5

The unit tests are written to work with py.test. For details see http://codespeak.net/py/dist/test.html

Known Bugs
==========

There has been a reported bug with Gerald accessing MySQL databases that a ``'KeyError'`` exception is raised during schema comparison. I have not been able to replicate this bug but note that it still may exist.
