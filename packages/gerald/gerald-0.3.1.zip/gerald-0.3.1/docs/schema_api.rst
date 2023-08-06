=================
Gerald Schema API
=================

Introduction
============

Gerald is a general purpose database schema toolkit written in Python_. It can be used for cataloguing, managing and deploying schemas in relational databases.

Gerald can read, store and manipulate information about collections of database objects. These collections of objects are call schemas. This document describes the format that Gerlad uses to store information about these objects and is valid for version 0.3 of Gerald and above.

The top level of a specific implementation of the API should provide a method which returns a Schema_ object.

.. _Schema:

Schema Objects
==============

Attributes
----------

Schemas must have the following attributes:

+-------------+------------------------------------------------+------------+
| Key         | Description                                    | Data Type  |
+=============+================================================+============+
| name        | A name for the schema, usually the same as the | Text       |
|             | database (or schema owner)                     |            |
+-------------+------------------------------------------------+------------+
| api_version | schema api version                             | Integer    |
+-------------+------------------------------------------------+------------+
| schema      | A collection of objects which form this schema | Collection |
|             | made of Table_, View_, Sequence_, and          |            |
|             | Code_Object_ objects.                          |            |
+-------------+------------------------------------------------+------------+

Methods
-------

+---------------------------+------------------------------------------------+
| Name                      | Description                                    |
+===========================+================================================+
| ``dump(file_name, sort)`` | Output this schema to ``file_name`` in a nice  |
|                           | to read format. If ``sort`` is specified the   |
|                           | objects will be sorted by their ``name``       |
|                           | attributes.                                    |
+---------------------------+------------------------------------------------+
| ``to_xml(file_name)``     | Output this schema to ``file_name`` in XML     |
|                           | format. If ``file_name`` is omitted then the   |
|                           | XML is sent to standard output.                |
+---------------------------+------------------------------------------------+
| ``get_ddl(file_name)``    | Output the DDL necessary to recreate this      |
|                           | schema to ``file_name``. If ``file_name`` is   |
|                           | ommitted then the DDL is output to standard    |
|                           | output.                                        |
+---------------------------+------------------------------------------------+
| ``compare(other_schema)`` | Utility method to compare two schemas.         |
+---------------------------+------------------------------------------------+

.. _Table:

Table Objects
=============

A table is made up of columns and will also have indexes, triggers, constraints, primary and foreign keys.

Attributes
----------

Tables must have the following attributes:
 
+-------------+------------------------------------------------+------------+
| Key         | Description                                    | Data Type  |
+=============+================================================+============+
| name        | the name of the table                          | Text       |
+-------------+------------------------------------------------+------------+
| columns     | A dictionary (keyed on column name) of Column_ | Dictionary |
|             | dictionaries that make up this table           |            |
+-------------+------------------------------------------------+------------+
| indexes     | A dictionary (keyed on index name) of Index_   | Dictionary |
|             | dictionaries                                   |            |
+-------------+------------------------------------------------+------------+
| constraints | A dictionary (keyed on constraint name) of     | Dictionary |
|             | Constraint_ dictionaries                       |            |
+-------------+------------------------------------------------+------------+
| triggers    | A dictionary (keyed on trigger name) of        | Dictionary |
|             | Trigger_ dictionaries                          |            |
+-------------+------------------------------------------------+------------+

Tables may optionally have one or more of the following attributes:

+-----------------+------------------------------------------------+------------+
| Key             | Description                                    | Data Type  |
+=================+================================================+============+
| tablespace_name | The tablespace this table is stored in         | Text       |
+-----------------+------------------------------------------------+------------+
| table_type      | The type of storage engine used for this table | Text       |
|                 | Only populated for MySQL tables                |            |
+-----------------+------------------------------------------------+------------+
| comments        | A comment on the table                         | Text       |
+-----------------+------------------------------------------------+------------+
| schema          | The name of the schema this table belongs to.  | Text       |
|                 | Used by ``get_ddl`` methods                    |            |
+-----------------+------------------------------------------------+------------+

Methods
-------

+--------------------------+------------------------------------------------+
| Name                     | Description                                    |
+==========================+================================================+
| ``dump()``               | Return a description of this table in a nice   |
|                          | to read format                                 |
+--------------------------+------------------------------------------------+
| ``to_xml()``             | Return a description of this table as an XML   |
|                          | fragment                                       |
+--------------------------+------------------------------------------------+
| ``get_ddl()``            | Return the DDL necessary to create this table  |
+--------------------------+------------------------------------------------+
| ``compare(other_table)`` | Utility method to compare two tables           |
+--------------------------+------------------------------------------------+

.. _View:

View Objects
============

Attributes
----------

+-------------+------------------------------------------------+------------+
| Key         | Description                                    | Data Type  |
+=============+================================================+============+
| name        | Name of this view                              | Text       |
+-------------+------------------------------------------------+------------+
| columns     | A dictionary (keyed on column name) of Column_ | Dictionary |
|             | dictionaries that make up this view            |            |
+-------------+------------------------------------------------+------------+
| sql         | The SQL statement that will create the view    | Text       |
+-------------+------------------------------------------------+------------+
| triggers    | A dictionary (keyed on name) of Trigger_       | Dictionary |
|             | objects that are associated with this view     |            |
+-------------+------------------------------------------------+------------+

Methods
-------

+--------------------------+------------------------------------------------+
| Name                     | Description                                    |
+==========================+================================================+
| ``dump()``               | Return a description of this view in a nice to |
|                          | read format                                    |
+--------------------------+------------------------------------------------+
| ``to_xml()``             | Return a description of this view as an XML    |
|                          | fragment                                       |
+--------------------------+------------------------------------------------+
| ``get_ddl()``            | Return the DDL necessary to create this view   |
+--------------------------+------------------------------------------------+
| ``compare(other_table)`` | Utility method to compare two views            |
+--------------------------+------------------------------------------------+

.. _Sequence:

Sequence Objects
================

Attributes
----------

+-------------+------------------------------------------------+------------+
| Key         | Description                                    | Data Type  |
+=============+================================================+============+
| name        | Sequence name                                  | Text       |
+-------------+------------------------------------------------+------------+
| min_value   | Minimum value                                  | Integer    |
+-------------+------------------------------------------------+------------+
| max_value   | Maximum value                                  | Integer    |
+-------------+------------------------------------------------+------------+
| increment_by| Interval to use when incrementing the sequence | Integer    |
+-------------+------------------------------------------------+------------+
| curr_value  | Current value of this sequence. Only used for  | Integer    |
|             | informational reasons.                         |            |
+-------------+------------------------------------------------+------------+

Methods
-------

+--------------------------+------------------------------------------------+
| Name                     | Description                                    |
+==========================+================================================+
| ``dump()``               | Return a description of this sequence in a     |
|                          | nice to read format                            |
+--------------------------+------------------------------------------------+
| ``to_xml()``             | Return a description of this sequence as an    |
|                          | XML fragment                                   |
+--------------------------+------------------------------------------------+
| ``get_ddl()``            | Return the DDL to create this sequence         |
+--------------------------+------------------------------------------------+
| ``compare(other_seq)``   | Utility method to compare two sequences        |
+--------------------------+------------------------------------------------+

.. _Code_Object:

Code Objects
============

Attributes
----------

Methods
-------

.. _Trigger:

Triggers
========

Attributes
----------

+-------------+------------------------------------------------+------------+
| Key         | Description                                    | Data Type  |
+=============+================================================+============+
| name        | Trigger name                                   | Text       |
+-------------+------------------------------------------------+------------+
| scope       | Scope of this trigger (before, after, instead  | Text       |
|             | of)                                            |            |
+-------------+------------------------------------------------+------------+
| events      | A list of the events that cause this trigger   | Text       |
|             | to fire (insert, update, delete)               |            |
+-------------+------------------------------------------------+------------+
| level       | Is this a row or statement level trigger?      | Text       | 
+-------------+------------------------------------------------+------------+
| sql         | The SQL executed when this trigger fires       | Text       |
+-------------+------------------------------------------------+------------+

Methods
-------

+--------------------------+------------------------------------------------+
| Name                     | Description                                    |
+==========================+================================================+
| ``dump()``               | Return a description of this trigger in a nice |
|                          | to read format                                 |
+--------------------------+------------------------------------------------+
| ``to_xml()``             | Return a description of this trigger as an XML |
|                          | fragment                                       |
+--------------------------+------------------------------------------------+
| ``get_ddl()``            | Return the DDL to create this trigger          |
+--------------------------+------------------------------------------------+
| ``compare(other_trig)``  | Utility method to compare two triggers         |
+--------------------------+------------------------------------------------+


.. _Column:

Columns
=======

A column is not a stand alone class, just a simple dictionary. They must have the following elements:

+-----------+-----------------------------------------+-----------+
| Key	    | Description                             | Data Type | 
+===========+=========================================+===========+
| sequence  | The order of this column in the table   | Integer   |
+-----------+-----------------------------------------+-----------+
| name      | Column name                             | Text      |
+-----------+-----------------------------------------+-----------+
| type      | Native data type, will vary by database | Text      |
+-----------+-----------------------------------------+-----------+
| nullable  | Can this column contain NULL values?    | Boolean   |
+-----------+-----------------------------------------+-----------+

Columns may optionally have one or more of the following elements:

+-----------+---------------------------------------------------+-----------+
| Key	    | Description                                       | Data Type | 
+===========+===================================================+===========+
| length    | Maximum length of column                          | Integer   |
+-----------+---------------------------------------------------+-----------+
| precision | Maximum number of digits before the decimal point | Integer   |
|           | only valid for numeric columns                    |           |
+-----------+---------------------------------------------------+-----------+
| scale     | Maximum number of digits after the decimal point  | Integer   |
+-----------+---------------------------------------------------+-----------+
| default   | Default value to be inserted if this column is    | Any       |
|           | NULL on insert                                    |           |
+-----------+---------------------------------------------------+-----------+
| special   | Only used by MySQL to indicate if a column has    | Boolean   |
|           | auto_increment set                                |           |
+-----------+---------------------------------------------------+-----------+
| comment   | Column comment                                    | Text      |
+-----------+---------------------------------------------------+-----------+

.. _Index:

Indexes
=======

Like a column an index is just a simple dictionary. They must have the following elements:

+-----------+---------------------------------------------------+-----------+
| Key	    | Description                                       | Data Type | 
+===========+===================================================+===========+
| name      | Index name                                        | Text      |
+-----------+---------------------------------------------------+-----------+
| type      | Index type. Database specific                     | Text      |
+-----------+---------------------------------------------------+-----------+
| unique    | Flag to indicate if index elements must be unique | Boolean   |
+-----------+---------------------------------------------------+-----------+
| columns   | A sequence of column names in the index           | Sequence  |
+-----------+---------------------------------------------------+-----------+


.. _Constraint

Constraints
===========

Constraints are represented by simple dictionaries with the following elements:

+-----------+---------------------------------------------------+-----------+
| Key	    | Description                                       | Data Type | 
+===========+===================================================+===========+
| name      | Constraint name                                   | Text      |
+-----------+---------------------------------------------------+-----------+
| type      | One of 'Primary', 'Foreign', 'Check' or 'Unique'  | Text      |
+-----------+---------------------------------------------------+-----------+
| enabled   | Is the constraint enabled?                        | Boolean   |
+-----------+---------------------------------------------------+-----------+

They may optionally have the following elements:

+------------+--------------------------------------------------+-----------+
| Key	     | Description                                      | Data Type | 
+============+==================================================+===========+
| columns    | Column names in this constraint                  | Sequence  |
+------------+--------------------------------------------------+-----------+
| reftable   | Reference table (only used for Foreign keys)     | Text      |
+------------+--------------------------------------------------+-----------+
| refpk	     | Reference primary key this foreign key is        | Text      |
|            | checked against (only used for Foreign keys)     |           |
+------------+--------------------------------------------------+-----------+
| refcolumns | List of reference columns (Foreign keys only)    | Sequence  |
+------------+--------------------------------------------------+-----------+
| condition  | Search condition (Check constraints only)        | Text      |
+------------+--------------------------------------------------+-----------+

