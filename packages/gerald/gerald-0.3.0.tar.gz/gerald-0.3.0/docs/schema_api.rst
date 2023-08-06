=================
Gerald Schema API
=================

Introduction
============

This document is valid for version 0.2.3 of Gerald.

The top level of a specific implementation of the API should provide a method which returns a Schema_ object.

.. _Schema:

Schema Objects
==============

Attributes
----------

 * ``name`` - a name for the schema, usually the same as the database (or schema owner)
 * ``schema_api_version`` - integer schema api version
 * ``schema`` - a collection of objects which form this schema, made of Table_, View_, Sequence_, and Code_Object_ objects. 

Methods
-------

 * ``dump(file_name, sort)`` - Output this schema to ``file_name`` in a nice to read format. If ``sort`` is specified the objects will be sorted by their ``name`` attributes.
 * ``to_xml(file_name)`` - Output this schema to ``file_name`` in XML format. If ``file_name`` is omitted then the XML is output to standard output.
 * ``get_ddl(file_name)`` - Output the DDL necessary to recreate this schema to ``file_name``. If ``file_name`` is ommitted then the DDL is output to standard output.
 * ``compare(other_schema)`` - Utility method to compare two schemas.

.. _Table:

Table Objects
=============

A table is made up of columns and will also have indexes, triggers, constraints, primary and foreign keys.

Attributes
----------
 
 * ``name`` - the name of the table
 * ``tablespace_name`` - Optional. The tablespace this table is stored in.
 * ``table_type`` - Optional, only populated for MySQL tables. The type of storage engine used for this table.
 * ``columns`` - Collection of column objects that make up this table.
 * ``indexes`` - Collection of index objects associated with this table.
 * ``constraints`` - Collection of constraints operating on this table.
 * ``triggers`` - Collection of triggers defined on this table.
   The exact type of this collection is an implementation detail, but as a minimum should be a dictionary keyed on trigger name.

Methods
-------

 * ``dump()`` - Return a description of this table in a nice to read format.
 * ``to_xml()`` - Return a description of this table in XML format.
 * ``get_ddl()`` - Return the DDL necessary to create this table.
 * ``compare(other_table)`` - Utility method to compare two tables.

.. _View:

View Objects
============

Attributes
----------

 * ``name`` - the name of the view

Methods
-------

.. _Sequence:

Sequence Objects
================

.. _Code_Object:

Code Objects
============
