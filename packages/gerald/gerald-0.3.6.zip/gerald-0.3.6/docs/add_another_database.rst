====================================
Adding Support for a Database Engine
====================================

Introduction
============

Gerald currently supports a number of popular relational databases_. The code has been developed in a way that makes it possible to add support for different relational databases.

Adding support for a new database to Gerald is possible, it isn't as simple as I would like, but is possible. The code is organised in a hierarchy of modules;::

    schema.py
      |
      |- mySQLSchema.py
      |
      |- oracleSchema.py
      |
      |- postgresSchema.py

With each database catered for by a separate module. To support a new database you simply need to create a new module and add the appropriate classes and methods to it. 

Creating a New Module
=====================

To add support for a different type of database follow these steps;

1. Check out the latest code from Subversion using;::

    $ svn checkout http://halfcooked.svn.sourceforge.net/projects/halfcooked halfcooked

2. cd to the code directory (halfcooked/gerald)

3. Take a copy of either ``mySQLSchema.py`` or ``oracleSchema.py`` (``postgresSchema.py`` is not as polished at the moment) and call it ``<new db name>Schema.py`` (e.g. ``db2Schema.py``).

4. Open up ``<new db name>Schema.py`` in your favourite editor and take a look to familiarise yourself with the code. The modules, classes and methods are all described in the `reference documentation`_ on the `web site`_.

   There should be a number of classes in this module that each inherit from a class with the same name in ``schema.py``. Keeping the names consistent is just a convention in the code, it isn't enforced in any way.

   At the very least you will need implementations of the ``Schema`` and ``Table`` classes. Most modern databases will also need ``View``, ``Trigger`` and ``CodeObject``.

5. Before you make any code changes modify the doc string at the top of the module as well as the ``__author__``, ``__date__`` and ``__version__`` attributes just below it.

6. Replace the _getXxx methods of any classes in the module. You'll notice that ``mySQLSchema.py`` has fairly rudimentary support for the different types of objects you will find in a database whereas ``oracleSchema.py`` covers more possibilities. Its probably best to start with the MySQL sample as this will be easier to adapt, you can then implement other object types as and when you need them. I've documented the attributes each class should have (which should be populated in the _getXxx method) in the class super types in ``schema.py``. Until I've generated the online documentation for gerald it is probably easiest just to have this open in another window as you work on your new module

.. _databases:

Supported Databases
===================

Gerald currently supports Oracle_, MySQL_, PostgreSQL_ and Sqlite_.

.. _Oracle: http://www.oracle.com/
.. _MySQL: http://www.mysql.com/
.. _PostgreSQL: http://www.postgresql.org/
.. _Sqlite: http://www.sqlite.org/

Further Reading
===============

The home of Gerald on the web is the `web site`_ and the API is documented (using Epydoc_) in the `reference documentation`_.

.. _`web site`: http://halfcooked.com/code/gerald/api
.. _`reference documentation`: http://halfcooked.com/code/gerald
.. _Epydoc: http://epydoc.sourceforge.net/
