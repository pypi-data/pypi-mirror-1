========================
Gerald the half a schema
========================

A Python Schema Comparison Tool
===============================

Gerald is a general purpose database schema toolkit written in Python_. It can be used for cataloguing, managing and deploying database schemas. 
Its major current use is to identify the differences between various versions of a schema. A schema is a single logical grouping of database objects usually made up of tables, views and stored code objects (functions and procedures).

You can use Gerald to determine the differences between your development and test environments, or to integrate changes from a number of different developers into your integration database.

Gerald is designed to be used in an Agile_ environment, but is useful regardless of your development methodology.

Gerald is designed from the ground up to support as many popular relational database systems as possible.  
Currently it will document and compare schemas from databases implemented in MySQL_, Oracle_ and PostgreSQL_.
Other databases will be supported in future releases.

Why?
====

I wrote this module because I was looking for a cheap, alright - free, tool with similar functionality to ERWin_ and other commercially available database modelling and management tools.
I didn't find anything so I ended up keeping my data model in an Excel spreadsheet and wrote some scripts to generate my Data Definition Language (DDL) into files. 
The one thing that they didn't do, though, was enable me to easily discover the differences between my model and what was deployed in the various databases we were using. 
So I started writing the code that became this module. 

Of course, by the time it was usable the project was long finished. 
I carried on though, because I'll need the same functionality on my next project and undoubtedly the one after that as well.
As it's fun to share, I'm putting this code up on the internet for anyone to use as they see fit. It is licensed under the 
`BSD License`_ (see LICENSE.txt in the distribution).

Gerald can currently extract and compare schemas, and in future I'm hoping that it will expand to store them as well, taking over from my Excel spreadsheet. 
Given infinite time, I'd hope to expand its capabilities to the level of tools like ERwin_ and `Oracle Designer`_.

Links
=====

Everything you need to get and run Gerald is at these links;

- Download the package from the PyPI_ `package page`_
- Download the code from the SourceForge_ `download page`_
- Read the `API documentation`_ courtesy of Epydoc_.
- The project issue tracker is at the `trac page`_
- The source code is in the `code repository`_ courtesy of Subversion_. Check out a copy with;

::

    svn checkout http://halfcooked.svn.sourceforge.net/svnroot/halfcooked/tags/release-0.3.1/gerald/ gerald/

Installation
============

There are two ways to install Gerald. 

If you are comfortable with source code tools and the command line you can install from the source package (available from the `download page`_ or the `package page_`). Once you have copied the downloaded file to a suitable location on your machine and unzipped it start up a command line, navigate to the package directory and type; ::

      python setup.py install

The other option is to use `easy_install`_. You will need to start a command line session but all you have to do is type ::

      easy_install gerald

Technical Information
=====================

Gerald is written in Python_ and requires a DB-API_ module to interact with your database.
In the current release we support Oracle_, MySQL_ and PostgreSQL_ databases. 
Because the code is designed to be modular and extensible adding support for different databases is quite simple.
All it requires is new sub-classes of the generic classes in ``schema.py``. They will need to be adapted for the data dictionary provided by the database. 

How to use Gerald
=================

To compare the same schema in two Oracle databases start an interactive session and type; ::

    >>> import gerald
    >>> first_schema = gerald.OracleSchema('first_schema', 'oracle:/[username]:[password]@[tns connection]')
    >>> second_schema = gerald.OracleSchema('second_schema', 'oracle:/[2nd username]:[2nd password]@[2nd tns connection]')
    >>> print first_schema.compare(second_schema)

You can display a reader friendly version of your schema like this; ::

    >>> import gerald
    >>> my_schema = gerald.MySQLSchema('schema_name', 'mysql:/[username]:[password]@[hostname]/[catalog name]')
    >>> print my_schema.dump()

You can display an XML representation of your schema like this; ::

    >>> import gerald
    >>> my_schema = gerald.OracleSchema('schema_name', 'oracle:/[username]:[password]@[tns entry]')
    >>> print my_schema.to_xml()

For more information on the available objects and methods, look at the module `API documentation`_.
 
Future Plans 
============

This is release 0.3.1 of Gerald. It's still alpha code, but it is in use on and does provide some value.
Having said that, I'm fairly happy with the current functionality so I will only change it if I absolutely have to, and then usually to extend the features available.
This is a minor release fixing some bugs and issues introduced with the release of version 0.3. Full details can be found in the CHANGELOG.txt file provided with the code.

The core function is fairly solid and will support a number of enhancements.
I'm specifically thinking about, but in no particular order;

- SQLite_ support
- Improvements to the comparison algorithms
- Make columns first class objects
- `SQL Server`_ support
- `DB2 UDB`_ support
- A proper persistence mechanism for schema models
- Support the input, storage and retrieval of notes against any object
- A diagramming front end

If anyone has suggestions I'm happy to hear your thoughts. Send an email to `andy47@halfcooked.com <mailto:andy47@halfcooked.com>`_

----

:Author: `andy47@halfcooked.com <mailto:andy47@halfcooked.com>`_
:Last Updated: Wednesday the 25th of November, 2009.

.. _Python: http://www.python.org/
.. _Agile: http://www.agiledata.org/
.. _MySQL: http://www.mysql.com/
.. _Oracle: http://www.oracle.com/
.. _PostgreSQL: http://www.postgresql.org/
.. _`SQL Server`: http://www.microsoft.com/
.. _`DB2 UDB`: http://www.ibm.com/software/data/DB2/
.. _ERWin: http://www3.ca.com/Solutions/Product.asp?ID=260
.. _`BSD License`: http://www.opensource.org/licenses/bsd-license.php
.. _`Oracle Designer`: http://otn.oracle.com/products/designer/index.html
.. _SourceForge: http://sourceforge.net/
.. _`download page`: http://sourceforge.net/projects/halfcooked/files
.. _PyPI: http://pypi.python.org/pypi/
.. _`package page`: http://pypi.python.org/pypi/gerald/0.2.6
.. _Epydoc: http://epydoc.sourceforge.net/"
.. _`API documentation`: http://www.halfcooked.com/code/gerald/doc
.. _API: http://sourceforge.net/apps/trac/halfcooked/wiki/GeraldApi
.. _Subversion: http://subversion.tigris.org/
.. _`code repository`: http://halfcooked.svn.sourceforge.net/viewvc/halfcooked/tags/release-0.3.1/gerald/
.. _DB-API: http://www.python.org/peps/pep-0249.html
.. _distutils: http://www.python.org/doc/current/dist/dist.html
.. _`PEP 8`: http://www.python.org/dev/peps/pep-0008/
.. _`easy_install`: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _SQLite: http://www.sqlite.org/
.. _`trac page`: http://sourceforge.net/apps/trac/halfcooked/
