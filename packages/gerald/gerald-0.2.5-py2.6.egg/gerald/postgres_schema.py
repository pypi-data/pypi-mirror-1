#!/usr/bin/python
"""
Introduction
============
  Capture, document and manage PostgreSQL database schemas.

  This is the PostgreSQL Schema module, every class is subclassed from the ones 
  in schema. 

  A schema is comprised of collections of tables, views, stored code objects, 
  triggers, sequences, and other assorted 'objects'

  to create a new schema object from an existing database schema you will need 
  to do something like;

  >>> from gerald import PostgresSchema
  >>> my_schema = PostgresSchema('my_schema', 'postgres:/user:passwd@host/db')

  N.B. the name you specify (e.g. 'my_schema') will be used in all database
  introspection operations. The default PostgreSQL schema name is 'public'.

  If you don't specify a connection string you'll get an empty schema object.

  >>> from gerald import PostgresSchema
  >>> my_schema = PostgresSchema('my_schema')

  With many grateful thanks to 
  http://www.alberton.info/postgresql_meta_info.html for most of the 
  introspection SQL

Meta-Data
=========
  Module  : postgres_schema.py

  License : BSD License (see LICENSE.txt)

Known limitations
=================
  Currently only a skeleton implementation
"""
__author__ = "Andy Todd <andy47@halfcooked.com>"
__date__ = (2009, 1, 3)
__version__ = (0, 2, 4)

import sys

import schema

LOG = schema.LOG

DATE_DATATYPES = ['date', 'timestamp', 'time', 'interval']
TEXT_DATATYPES = ['char', 'character', 'varchar', 'text', ]
NUMERIC_DATATYPES = ['integer', 'int', 'number', 'real', 'smallint', 
                     'numeric', 'decimal', ]
DEFAULT_NUM_LENGTH = '38'

class Schema(schema.Schema):
    """
    A representation of a PostgreSQL database schema

    A PostgreSQL schema is all of the objects owned by a particular user
    """
    def _get_schema(self, cursor):
        """
        Get definitions for the objects in the current schema
        
        We query the data dictionary for (in order);
          - Tables, Views, Sequences, Code objects, DB links
        We should also get;
          - Grants and synonyms

        @param cursor: The cursor to use to query the data dictionary
        @type cursor: Database cursor object
        @return: All of the objects in this schema
        @rtype: Dictionary
        """
        schema = {}
        # Tables
        stmt = """SELECT table_name
                  FROM   information_schema.tables
                  WHERE  table_schema = %(schema)s
                  AND    table_type = 'BASE TABLE'"""
        cursor.execute(stmt, {'schema': self.name})
        for table in cursor.fetchall():
            LOG.debug("Getting details for table %s" % table[0])
            schema[table[0]] = Table(table[0], cursor)
        # Views
        stmt = """SELECT table_name 
                  FROM   information_schema.views
                  WHERE  table_schema = %(schema)s"""
        cursor.execute(stmt, {'schema': self.name})
        for view in cursor.fetchall():
            LOG.debug("Getting details for view %s" % view[0])
            schema[view[0]] = View(view[0], cursor)
        # Sequences - not currently supported for PostgreSQL
        stmt = """SELECT relname 
                  FROM pg_class 
                  WHERE relkind = 'S' 
                  AND relnamespace IN ( SELECT oid 
                                        FROM   pg_namespace 
                                        WHERE  nspname = %(schema)s )"""
        #cursor.execute(stmt, {'schema': self.name})
        #for sequence in cursor.fetchall():
        #    log.debug("Getting details for sequence %s" % sequence[0])
        #    schema[sequence[0]] = Sequence(sequence[0], cursor)
        # Code objects (packages, procedures and functions)
        # Currently not implemented for PostgreSQL
        # Database links. You know, I don't think PostgreSQL has db links
        # All done, return the fruit of our labours
        return schema


class PostgresCalcPrecisionMixin(object):
    """Class to contain the calc_precision static method to be used as a 
    mixin by other classes in this module.
    """

    def calc_precision(data_type, data_length, data_precision, data_scale):
        """
        Calculate and then return the precision of this column
        
        This is a bit of a hack and will be replaced when columns become 
        first class objects.

        @param data_type: The data type of the column
        @type data_type: String
        @param data_length: The length of the column, if this is present its 
        usually the only numeric value provided
        @type data_length: Integer
        @param data_precision: The total number of digits in the column
        @type data_precision: Integer
        @param data_scale: The number of digits after the decimal point
        @type data_scale: Integer
        @return: The appropriate precision values for this column
        @rtype: String
        """
        if data_type:
            data_type = data_type.lower()
            if data_type.lower() in TEXT_DATATYPES:
                if data_length > 0:
                    precision = '(%d)' % int(data_length)
                else:
                    raise ValueError, 'data length must be greater than 0'
            elif data_type.lower() in NUMERIC_DATATYPES:
                if data_precision:
                    precision = '(%d' % int(data_precision)
                    if data_scale:
                        precision += ',%d' % int(data_scale)
                    precision += ')'
                else:
                    precision = '(%d)' % DEFAULT_NUM_LENGTH
            elif data_type.lower() in DATE_DATATYPES:
                precision = ""
            else:
                raise ValueError, '%s is not a valid data type' % data_type
        else:
            raise ValueError, 'No data type supplied'
        return precision

    calc_precision = staticmethod(calc_precision)


class Table(schema.Table, PostgresCalcPrecisionMixin):
    """
    A representation of a database table.
    
    A table is made up of columns and will have indexes, triggers, primary keys 
    and foreign keys.
    """
    def _get_table(self, cursor):
        """
        Query the data dictionary for this table
        
        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        # Tablespace information
        stmt = """SELECT tablespace FROM pg_tables WHERE tablename=%(table)s"""
        table = self.name
        cursor.execute(stmt, locals())
        result = cursor.fetchone()
        if result is None:
            raise AttributeError, "Can't get DDL for table %s" % self.name
        self.tablespace_name = result[0]
        # Columns
        stmt = """SELECT ordinal_position, column_name, data_type, 
                         character_maximum_length, numeric_precision, 
                         numeric_scale, 
                         CASE is_nullable
                            WHEN 'YES' THEN 'Y'
                            WHEN 'NO' THEN 'N'
                         END,
                         column_default 
                  FROM   information_schema.columns 
                  WHERE  table_name=%(table)s"""
        cursor.execute(stmt, locals())
        for row in cursor.fetchall():
            # Varchar columns are returned as 'character varying'
            new_row = list(row)
            if new_row[2] == 'character varying':
                new_row[2] = 'varchar'
            self.columns[new_row[1]] = new_row
        # Constraints
        stmt = """SELECT constraint_name, 
                         CASE constraint_type
                            WHEN 'PRIMARY KEY' THEN 'Primary'
                            WHEN 'FOREIGN KEY' THEN 'Foreign'
                            WHEN 'CHECK' THEN 'Check'
                            WHEN 'UNIQUE' THEN 'Unique'
                         END AS constraint_type
                  FROM   information_schema.table_constraints
                  WHERE  table_name=%(table)s
                  AND    constraint_name NOT LIKE '%%not_null'"""
        cursor.execute(stmt, locals())
        cons_details_stmt = """
              SELECT tc.constraint_name, tc.constraint_type,
                     kcu.column_name, ccu.table_name AS references_table,
                     ccu.column_name AS references_field
              FROM   information_schema.table_constraints tc
                     LEFT JOIN information_schema.key_column_usage kcu
                       ON  tc.constraint_catalog = kcu.constraint_catalog
                       AND tc.constraint_schema = kcu.constraint_schema
                       AND tc.constraint_name = kcu.constraint_name
                     LEFT JOIN information_schema.referential_constraints rc
                       ON tc.constraint_catalog = rc.constraint_catalog
                       AND tc.constraint_schema = rc.constraint_schema
                       AND tc.constraint_name = rc.constraint_name
                     LEFT JOIN information_schema.constraint_column_usage ccu
                       ON rc.unique_constraint_catalog = ccu.constraint_catalog
                       AND rc.unique_constraint_schema = ccu.constraint_schema
                       AND rc.unique_constraint_name = ccu.constraint_name
              WHERE  tc.table_name = %(table)s
              AND    tc.constraint_name = %(constraint_name)s
        """
        for constraint in cursor.fetchall():
            constraint_name, constraint_type = constraint
            # First element is constraint type
            # Note that Postgres doesn't have the concept of enabled or disabled
            # constraints so we hard code the second value to 'Y' for enabled
            self.constraints[constraint_name] = [constraint_type, 'Y']
            cursor.execute(cons_details_stmt, locals())
            cons_details = cursor.fetchall()
            if constraint_type in ('Primary', 'Foreign'):
                cons_columns = [x[0] for x in cons_details]
                # Second element is list of columns
                self.constraints[constraint_name].append(cons_columns)
                if constraint_type == 'Foreign':
                    # Third element is reference constraint name
                    self.constraints[constraint_name].append('')
                    # Fourth element is reference table
                    ref_table = cons_details[0][3]
                    self.constraints[constraint_name].append(ref_table)
                    # Fourth element is reference columns
                    ref_columns = [x[4] for x in cons_details]
                    self.constraints[constraint_name].append(ref_columns)
        # Indexes
        stmt = """SELECT oid, relname
                  FROM pg_class
                  WHERE oid IN (SELECT indexrelid
                                FROM pg_index, pg_class
                                WHERE pg_class.relname=%(table)s
                                AND pg_class.oid=pg_index.indrelid
                                AND indisunique != 't' AND indisprimary != 't' )
        """
        # Columns for an index
        index_ddl_stmt = """SELECT pg_get_indexdef(%(oid)s)"""
        # Get the information
        cursor.execute(stmt, locals())
        for index in cursor.fetchall():
            oid, index_name = index
            index_defn = cursor.execute(index_ddl_stmt, {'oid': oid})
            self.indexes[index_name] = index_defn
        # Triggers

    def get_ddl(self):
        """
        Generate the DDL necessary to create this table in a PostgreSQL database
        
        @return: DDL to create this table 
        @rtype: String
        """
        ddl_strings = [self.get_table_ddl()]
        ddl_strings.append(self.get_constraints_ddl())
        ddl_strings.append(self.get_index_ddl())
        ddl_strings.append(self.get_trigger_ddl())
        return ''.join(ddl_strings)

    def get_table_ddl(self):
        """
        Generate the DDL necessary to create the table and its columns in a
        PostgreSQL database.

        @return: Table DDL
        @rtype: String
        """
        if not hasattr(self, 'name') or self.name == None:
            raise AttributeError, "Table does not have a name"
        ddl_strings = ["CREATE TABLE " + self.name]
        in_columns = False
        cols = self.columns.values()
        cols.sort()
        for column in cols:
            if in_columns:
                ddl_strings.append("\n  ,")
            else:
                ddl_strings.append("\n ( ")
                in_columns = True
            ddl_strings.append(column[1] + " " + column[2])
            ddl_strings.append(self.calc_precision(column[2], column[3], column[4], column[5]))
            # Nullable?
            if column[6] == "N":
                ddl_strings.append(" NOT NULL")
        if len(ddl_strings) > 1:
            ddl_strings.append(" )")
        return "".join(ddl_strings)

    def get_named_constraint_ddl(self, constraint_name):
        """
        Generate the DDL for the constraint named constraint_name

        @parameter constraint_name: The name of a constraint
        @type constraint_name: String
        @return: DDL to create a constraint
        @rtype: String
        """
        ddl_strings = []
        if constraint_name in self.constraints:
            cons_details = self.constraints[constraint_name]
            cons_type = cons_details[0]
            ddl_strings.append('ALTER TABLE %s ADD ' % self.name)
            ddl_strings.append('CONSTRAINT %s' % constraint_name)
            if cons_type == 'Check':
                ddl_strings.append(' CHECK ( %s )' % cons_details[2])
            elif cons_type == 'Primary':
                ddl_strings.append(' PRIMARY KEY (')
            elif cons_type == 'Foreign':
                ddl_strings.append(' FOREIGN KEY (')
            if cons_type in ('Primary', 'Foreign'):
                ddl_strings.append(', '.join(cons_details[2]))
                ddl_strings.append(')')
            if cons_type == 'Foreign':
                ddl_strings.append(" REFERENCES %s (" % cons_details [4])
                # Add the columns separated by commas
                ddl_strings.append(', '.join(cons_details [5]))
                ddl_strings.append(")")
            ddl_strings.append(';\n')
        return ''.join(ddl_strings)

    def get_constraints_ddl(self):
        """
        Generate the DDL for all of the constraints defined against this table
        in PostgreSQL database syntax.

        @return: DDL to create zero, one or more constraints
        @rtype: String
        """
        ddl_strings = [' ']
        for constraint in self.constraints:
            ddl_strings.append(self.get_named_constraint_ddl(constraint))
        return ''.join(ddl_strings)

    def get_index_ddl(self):
        """
        Generate the DDL necessary to create indexes defined against this table 
        in a PostgreSQL database
        
        @return: DDL to create the indexes for this table 
        @rtype: String
        """
        ddl_strings = []
        for index in self.indexes:
            ddl_strings.append('CREATE')
            # Only put the uniqueness if the index is actually unique
            # if index[1] != 'NONUNIQUE':
            #     ddl_strings.append(' %s' % index[1])
            ddl_strings.append(' INDEX %s ON %s' % (index, self.name))
            ddl_strings.append(' ( %s );\n' % ','.join(index[2]))
        return "".join(ddl_strings)

    def get_trigger_ddl(self):
        """
        Generate the DDL necessary to create any triggers defined against this
        table in a PostgreSQL database.

        @return: DDL to create zero, one or more triggers
        @rtype: String
        """
        ddl_strings = []
        for trigger in self.triggers:
            ddl_strings.append('\n')
            ddl_strings.append(self.triggers[trigger].get_ddl())
        return "".join(ddl_strings)


class View(schema.View, PostgresCalcPrecisionMixin):
    """
    A representation of a database view.

    A View is made up of columns and also has an associated SQL statement.
    
    Most of the methods for this class are inherited from schema.View
    """
    view_sql = {
      'text': """SELECT view_definition 
                 FROM information_schema.views 
                 WHERE table_name=%(name)s""",
      'columns': """SELECT 0, cols.column_name,
                           (CASE WHEN cols.data_type='character varying' 
                                 THEN 'varchar'
                                 ELSE cols.data_type END) AS data_type,
                           cols.character_maximum_length, cols.numeric_precision, 
                           cols.numeric_scale, 
                           CASE cols.is_nullable
                             WHEN 'YES' THEN 'Y'
                             WHEN 'NO' THEN 'N'
                           END
                    FROM   information_schema.view_column_usage vcu
                           JOIN information_schema.columns cols ON 
                             (vcu.table_name=cols.table_name AND 
                              vcu.column_name=cols.column_name)
                    WHERE  view_name=%(name)s""",
      'triggers': """SELECT trigger_name 
                     FROM information_schema.triggers 
                     WHERE table_name=%(name)s""",
    }


    def _get_view(self, cursor):
        """
        Query the data dictionary for this view

        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        arguments = { 'name': self.name, }
        LOG.debug("Getting definition of view %s" % self.name)
        cursor.execute(self.view_sql['text'], arguments)
        self.sql = cursor.fetchone()[0]
        # Columns
        cursor.execute(self.view_sql['columns'], arguments)
        self.columns = cursor.fetchall()
        # Triggers - to be implemented, something like;
        """
        ::

          cursor.execute(self.view_sql['triggers'], arguments)
          for trigger in cursor.fetchall():
              trigger_name = trigger[0]
              self.triggers[trigger_name] = Trigger(trigger_name, cursor)
        """

    def get_ddl(self):
        """
        Generate the DDL necessary to create this view

        @return: DDL to create this view
        @rtype: String
        """
        if not hasattr(self, 'name') or self.name == None:
            raise AttributeError, "Can't generate DDL for a view without a name"
        ddl_strings = ["CREATE VIEW "+self.name]
        in_columns = False
        # The columns may not necessarily be in the correct order. So we make a 
        # copy and sort by the first element of the tuple - the column number
        sorted_columns = self.columns[:]
        sorted_columns.sort()
        for column in sorted_columns:
            if in_columns:
                ddl_strings.append("\n ,")
            else:
                ddl_strings.append(" ( ")
                in_columns = True
            ddl_strings.append(column[1]+" ")
        # Only close the columns clause if we've actually got any columns
        if in_columns:
            ddl_strings.append(") AS\n  ")
        # Should strip excessive white space from self.sql before appending it 
        ddl_strings.append(self.sql)
        return "".join(ddl_strings)
        

class Trigger(schema.Trigger):
    """
    A representation of a database trigger.

    A trigger has triggering events and a SQL statement. A trigger can only
    exist within the context of a table or view and thus doesn't need any table 
    references as you can get those from its parent. Apart from the table or 
    view name, of course, which we need for the get_ddl method.

    Most of the methods for this class are inherited from schema.Trigger
    """
    def _get_trigger(self, cursor):
        """
        Query the data dictionary for this trigger
        
        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        stmt = """SELECT action_orientation, event_manipulation, 
                         action_statment, event_object_table
                  FROM   information_schema.triggers 
                  WHERE  trigger_name = %(trigger_name)s""" 
        cursor.execute(stmt, {'trigger_name': self.name})
        results = cursor.fetchone()
        self.type, self.events, self.sql, self.table_name = results
        self.level = self.type

    def get_ddl(self):
        """
        Generate the DDL necessary to create this trigger

        @return: DDL to create this trigger
        @rtype: String
        """
        ddl_strings = ['CREATE OR REPLACE TRIGGER %s' % self.name]
        ddl_strings.append(' %s %s ' % (self.type, self.events))
        ddl_strings.append('ON %s\n' % self.table_name)
        if self.level:
            ddl_strings.append(' FOR %s\n' % self.level)
        ddl_strings.append(self.sql)
        ddl_strings.append('\n/\n')
        return "".join(ddl_strings)


if __name__ == "__main__":
    print "This module should not be invoked from the command line"
    sys.exit(1)
