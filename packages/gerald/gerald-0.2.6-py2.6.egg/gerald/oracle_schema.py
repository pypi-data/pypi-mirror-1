"""
Introduction
============
  Capture, document and manage Oracle database schemas.

  This is the Oracle Schema module, every class is subclassed from the ones in
  schema. 

  A schema is comprised of collections of tables, views, stored code objects, 
  triggers, sequences (Oracle only), and other assorted 'objects'

  to create a new schema object from an existing database schema you will need 
  to do something like;

  >>> from gerald import OracleSchema
  >>> my_schema = OracleSchema('my_schema', 'oracle:/scott:tiger')

  If you don't specify a connection string you'll get an empty schema object.

  >>> from gerald import OracleSchema
  >>> my_schema = OracleSchema('my_schema')

Meta-Data
=========
  Module  : oracle_schema.py

  License : BSD License (see LICENSE.txt)

Known limitations
=================
  References to objects in other schemas are noted but are not properly 
  re-created e.g. if a table has a foreign key to another schema (indicated 
  by a value in R_OWNER on the USER_CONSTRAINTS table) this is not properly 
  generated.
  Will only work with the Oracle DB-API modules available in the dburi module,
  this is currently limited to cx_Oracle.
"""
__author__ = "Andy Todd <andy47@halfcooked.com>"
__date__ = (2009, 4, 14)
__version__ = (0, 2, 5)

import schema
import sys

LOG = schema.LOG

TEXT_DATATYPES = ['CHAR', 'NCHAR', 'NVARCHAR2', 'VARCHAR2']
NUMERIC_DATATYPES = ['FLOAT', 'NUMBER']
DATE_DATATYPES = ['DATE', 'TIMESTAMP']
DEFAULT_NUM_LENGTH = '38'


class Schema(schema.Schema):
    """
    A representation of an Oracle database schema

    An Oracle schema is all of the objects owned by a particular user
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
                  FROM user_tables 
                  WHERE table_name NOT LIKE 'DR%%'"""
        cursor.execute(stmt)
        for table in cursor.fetchall():
            LOG.debug("Getting details for table %s" % table[0])
            schema[table[0]] = Table(table[0], cursor)
        # Views
        stmt = """SELECT view_name
                  FROM   user_views"""
        cursor.execute(stmt)
        for view in cursor.fetchall():
            LOG.debug("Getting details for view %s" % view[0])
            schema[view[0]] = View(view[0], cursor)
        # Sequences
        stmt = """SELECT sequence_name
                  FROM   user_sequences"""
        cursor.execute(stmt)
        for sequence in cursor.fetchall():
            LOG.debug("Getting details for sequence %s" % sequence[0])
            schema[sequence[0]] = Sequence(sequence[0], cursor)
        # Code objects (packages, procedures and functions)
        # Note that we exclude package bodies, even though they are separate
        # objects they are stored under the package header in gerald
        stmt = """SELECT object_name, object_type
                  FROM   user_objects
                  WHERE  object_name IN (SELECT object_name FROM user_procedures)
                  AND    object_type NOT IN ('PACKAGE BODY')
                  """
        cursor.execute(stmt)
        for code_object in cursor.fetchall():
            object_name, object_type = code_object
            LOG.debug("Getting details for code object %s" % object_name)
            if object_type == 'PACKAGE':
                schema[object_name] = Package(object_name, object_type, cursor)
            else:
                schema[object_name] = CodeObject(object_name, object_type, cursor)
        # Database links
        stmt = """SELECT db_link
                  FROM   user_db_links
                  WHERE  password IS NOT NULL
                  """
        cursor.execute(stmt)
        for db_link in cursor.fetchall():
            link_name = db_link[0]
            LOG.debug("Getting details for db link %s" % link_name)
            schema[link_name] = DatabaseLink(link_name, cursor)
        # All done, return the fruit of our labours
        return schema


class OracleCalcPrecisionMixin(object):
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
        if data_type in DATE_DATATYPES:
            precision = ''
        elif data_type in TEXT_DATATYPES:
            if data_length > 0:
                precision = '(' + str(int(data_length)) + ')'
            else:
                raise ValueError, 'Data length must be greater than zero'
        elif data_type in NUMERIC_DATATYPES:
            if data_precision:
                precision = '(' + str(int(data_precision))
                if data_scale:
                    precision += ',' + str(int(data_scale))
                precision += ')'
            else:
                precision = '(' + DEFAULT_NUM_LENGTH + ')' 
        else:
            raise ValueError, 'Unknown data type'
        return precision

    calc_precision = staticmethod(calc_precision)


class Table(schema.Table, OracleCalcPrecisionMixin):
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
        # A trivial operation but it may speed up nine subsequent operations
        # uc_table_name = self.name.upper()
        if self.name.find('"') != -1:
            # If the table name contains a " it is case sensitive
            # But when querying data dictionary tables we don't need the "
            uc_table_name = self.name.strip('"')
        else:
            uc_table_name = self.name.upper()
        # Table information
        stmt = """SELECT tablespace_name
                  FROM   user_tables
                  WHERE  table_name = :table_name""" 
        cursor.execute(stmt, (uc_table_name, ))
        result = cursor.fetchone()
        if result is None:
            raise AttributeError, "Can't get DDL for table %s" % uc_table_name
        self.tablespace_name = result[0]
        # Table Comment(s) - Note that Oracle only allows 1 per table
        stmt = """SELECT comments
                  FROM   user_tab_comments
                  WHERE  table_name = :table_name
                  AND    comments IS NOT NULL"""
        cursor.execute(stmt, (uc_table_name, ))
        results = cursor.fetchall()
        if len(results) > 0: # Has the query returned at least 1 row?
            LOG.debug('Getting comments for table %s' % uc_table_name)
            self.comments = results[0][0]
        # Columns
        stmt = """SELECT utc.column_id, utc.column_name, utc.data_type, 
                         utc.data_length, utc.data_precision, utc.data_scale,
                         utc.nullable, utc.data_default, '' special, 
                         ucc.comments
                  FROM   user_tab_columns utc
                         LEFT OUTER JOIN user_col_comments ucc ON 
                           (utc.table_name = ucc.table_name AND
                            utc.column_name = ucc.column_name)
                  WHERE  utc.table_name = :table_name""" 
        cursor.execute(stmt, (uc_table_name, ))
        for row in cursor.fetchall():
            # Column name is in the second element
            self.columns[row[1]] = row
        # Constraints
        stmt = """SELECT constraint_name, 
                         decode(constraint_type, 'C', 'Check', 'P', 'Primary',
                                  'U', 'Unique', 'R', 'Foreign', 
                                  'V', 'View Check', 'O', 'View Read Only') 
                                  constraint_type,
                         r_constraint_name, search_condition,
                         decode(status, 'ENABLED', 'Y', 'DISABLED', 'N') status
                  FROM   user_constraints
                  WHERE  table_name = :table_name""" 
        cursor.execute(stmt, (uc_table_name, ))
        for key in cursor.fetchall():
            key_name, key_type, foreign_key = key[0], key[1], key[2]
            search_condition, enabled = key[3], key[4]
            self.constraints[key_name] = [key_type, enabled]
            if key_type == 'Foreign' or key_type == 'Primary':
                stmt = """SELECT column_name
                          FROM   user_cons_columns
                          WHERE  table_name = :table_name
                          AND    constraint_name = :constraint_name
                          ORDER BY position""" 
                cursor.execute(stmt, (uc_table_name, key_name))
                columns = []
                for column in cursor.fetchall():
                    columns.append(column[0])
                self.constraints[key_name].append(columns)
                if key_type == 'Foreign':
                    self.constraints[key_name].append(foreign_key)
                    stmt = """SELECT table_name
                              FROM   user_constraints
                              WHERE  constraint_name = :constraint_name""" 
                    cursor.execute(stmt, (foreign_key, ))
                    foreign_table = cursor.fetchone()[0]
                    self.constraints[key_name].append(foreign_table)
                    stmt = """SELECT column_name
                              FROM   user_cons_columns
                              WHERE  table_name = :table_name
                              AND    constraint_name = :constraint_name
                              ORDER BY position""" 
                    cursor.execute(stmt, (foreign_table, foreign_key))
                    columns = []
                    for column in cursor.fetchall():
                        columns.append(column[0])
                    self.constraints[key_name].append(columns)
            elif key_type == 'Check':
                if not key_name.startswith("SYS_C"):
                    self.constraints[key_name].append(search_condition)
        # Indexes
        stmt = """SELECT index_name, index_type, uniqueness
                  FROM   user_indexes
                  WHERE  table_name = :table_name""" 
        cursor.execute(stmt, (uc_table_name, ))
        for index in cursor.fetchall():
            index_name = index[0]
            # If this index is already recorded as a constraint, skip it
            if index_name in self.constraints.keys():
                continue
            self.indexes[index_name] = [index[1], index[2]]
            stmt = """SELECT column_name
                      FROM   user_ind_columns
                      WHERE  table_name = :table_name
                      AND    index_name = :index_name
                      ORDER BY column_position""" 
            cursor.execute(stmt, (uc_table_name, index_name))
            columns = []
            for column in cursor.fetchall():
                columns.append(column[0])
            self.indexes[index_name].append(columns)
        # Triggers
        stmt = """SELECT trigger_name
                  FROM   user_triggers
                  WHERE  table_name = :table_name""" 
        cursor.execute(stmt, (uc_table_name, ))
        for trigger in cursor.fetchall():
            # Trigger name is the first element 
            self.triggers[trigger[0]] = Trigger(trigger[0], cursor)

    def get_ddl(self):
        """
        Generate the DDL necessary to create this table in an Oracle database
        
        @return: DDL to create this table 
        @rtype: String
        """
        ddl_strings = [self._get_table_ddl()]
        ddl_strings.append(self._get_comments_ddl())
        ddl_strings.append(self._get_constraint_ddl())
        ddl_strings.append(self._get_index_ddl())
        ddl_strings.append(self._get_trigger_ddl())
        return ''.join(ddl_strings)

    def _get_table_ddl(self):
        """
        Generate the DDL necessary to create the table and its columns in an
        Oracle database.

        @return: Table DDL
        @rtype: String
        """
        if not hasattr(self, 'name') or self.name == None:
            raise AttributeError, "Can't generate DDL for a table without a name"
        ddl_strings = ['CREATE TABLE ' + self.name]
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
            if column[7]:
                ddl_strings.append(" DEFAULT %s" % column[7])
            # Nullable?
            if column[6] == "N":
                ddl_strings.append(" NOT NULL")
        if len(ddl_strings) > 1:
            ddl_strings.append(" )")
        if self.tablespace_name:
            ddl_strings.append("\n TABLESPACE %s" % self.tablespace_name)
        ddl_strings.append(';\n')
        return "".join(ddl_strings)

    def _get_comments_ddl(self):
        """
        Return the DDL for all of the comments defined against the table and its columns

        @return: DDL to create table and column comments
        @rtype: String
        """
        ddl_strings = []
        # Table comments first
        if hasattr(self, 'comments'):
            LOG.debug('Generating comment DDL for %s' % self.name)
            ddl_strings.append("COMMENT ON TABLE %s IS '%s';\n" % (self.name, self.comments))
        else:
            LOG.debug('Not generating comment DDL for %s' % self.name)
        # Column comments next
        cols = self.columns.values()
        cols.sort()
        for column in cols:
            if column[9]:
                ddl_strings.append("COMMENT ON COLUMN %s.%s IS '%s';\n" % (self.name, column[1], column[9]))
        return "".join(ddl_strings)

    def _get_named_constraint_ddl(self, constraint_name):
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
            if cons_type != 'Check' or not constraint_name.startswith("SYS_C"):
                ddl_strings.append('ALTER TABLE %s ADD' % self.name)
                ddl_strings.append(" CONSTRAINT %s" % constraint_name)
                if cons_type == 'Check':
                    ddl_strings.append(" CHECK (%s) " % cons_details[2])
            if cons_type == 'Primary':
                ddl_strings.append(" PRIMARY KEY (")
            elif cons_type == 'Foreign':
                ddl_strings.append(" FOREIGN KEY (")
            if cons_type == 'Primary' or cons_type == 'Foreign':
                # Add the columns separated by commas
                ddl_strings.append(', '.join(cons_details[2]))
                ddl_strings.append(')')
            if cons_type == 'Foreign':
                ddl_strings.append(" REFERENCES %s (" % cons_details [4])
                # Add the columns separated by commas
                ddl_strings.append(', '.join(cons_details [5]))
                ddl_strings.append(")")
            if cons_type != 'Check' or not constraint_name.startswith("SYS_C"):
                ddl_strings.append(';\n')
        return ''.join(ddl_strings)

    def _get_constraint_ddl(self):
        """
        Generate the DDL for all of the constraints defined against this table
        in Oracle database syntax.

        @return: DDL to create zero, one or more constraints
        @rtype: String
        """
        ddl_strings = []
        for constraint in self.constraints:
            ddl_strings.append(self._get_named_constraint_ddl(constraint))
        return ''.join(ddl_strings)

    def _get_index_ddl(self):
        """
        Generate the DDL necessary to create indexes defined against this table 
        in an Oracle database
        
        @return: DDL to create the indexes for this table 
        @rtype: String
        """
        ddl_strings = []
        for index in self.indexes:
            # SYS_ indexes are generally used to implement constraints and so 
            # will have been sucked up as part of a reverse engineer - don't 
            # recreate them.
            if not index.startswith('SYS'):
                index_details = self.indexes[index]
                ddl_strings.append('CREATE')
                # Only put the uniqueness if the index is actually unique
                if index_details[1] != 'NONUNIQUE':
                    ddl_strings.append(' %s' % index_details[1])
                ddl_strings.append(' INDEX %s ON %s' % (index, self.name))
                ddl_strings.append(' ( %s );\n' % ','.join(index_details[2]))
        return "".join(ddl_strings)

    def _get_trigger_ddl(self):
        """
        Generate the DDL necessary to create any triggers defined against this
        table in an Oracle database.

        @return: DDL to create zero, one or more triggers
        @rtype: String
        """
        ddl_strings = []
        for trigger in self.triggers:
            ddl_strings.append('\n')
            ddl_strings.append(self.triggers[trigger].get_ddl())
        return "".join(ddl_strings)


class View(schema.View, OracleCalcPrecisionMixin):
    """
    A representation of a database view.

    A View is made up of columns and also has an associated SQL statement.
    
    Most of the methods for this class are inherited from schema.View
    """

    view_sql = {
      'text': "SELECT text FROM user_views WHERE view_name=:name",
      'columns': """SELECT column_id, column_name, data_type, data_length,
                           data_precision, data_scale, nullable
                    FROM   user_tab_columns
                    WHERE  table_name=:name""",
      'triggers': """SELECT trigger_name 
                     FROM user_triggers 
                     WHERE table_name=:name""",
    }

    def _get_view(self, cursor):
        """
        Query the data dictionary for this view

        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        cursor.execute(self.view_sql['text'], (self.name, ))
        self.sql = cursor.fetchone()[0]
        # Columns, bizarrely these are stored in user_tab_columns
        cursor.execute(self.view_sql['columns'], (self.name, ))
        self.columns = cursor.fetchall()
        # Triggers
        cursor.execute(self.view_sql['triggers'], (self.name, ))
        for trigger in cursor.fetchall():
            trigger_name = trigger[0]
            self.triggers[trigger_name] = Trigger(trigger_name, cursor)

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
        stmt = """SELECT trigger_type, triggering_event, 
                         trigger_body, table_name
                  FROM   user_triggers
                  WHERE  trigger_name = :name""" 
        cursor.execute(stmt, (self.name, ))
        results = cursor.fetchone()
        self.type, self.events, self.sql, self.table_name = results
        # Type is a bit of a bodge (bad Oracle)
        if self.type.endswith('EACH ROW'):
            self.type = self.type[:-9]
            self.level = 'EACH ROW'
        else:
            self.level = '' # Its a statement level trigger really

    def get_ddl(self):
        """
        Generate the DDL necessary to create this trigger

        @return: DDL to create this trigger
        @rtype: String
        """
        ddl_strings = ['CREATE OR REPLACE TRIGGER %s' % self.name]
        ddl_strings.append(' %s ' % self.type)
        ddl_strings.append('%s ON ' % self.events)
        ddl_strings.append('%s\n' % self.table_name)
        if self.level:
            ddl_strings.append(' FOR %s\n' % self.level)
        ddl_strings.append(self.sql)
        ddl_strings.append('\n/\n')
        return "".join(ddl_strings)


class Sequence(schema.Sequence):
    """
    A representation of a database sequence.

    A sequence is an in memory construct that provides numbers in a sequence. 
    They are generally used to generate primary key values.

    Most of the methods for this class are inherited from schema.Sequence
    """
    def _get_sequence(self, cursor):
        """
        Query the data dictionary for this sequence

        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        stmt = """SELECT min_value, max_value, increment_by, %s.nextval
                  FROM   user_sequences
                  WHERE  sequence_name=:seqname""" % self.name
        # Ensure sequence name is upper case
        cursor.execute(stmt, seqname=self.name.upper()) 
        results = cursor.fetchone()
        self.min_value, self.max_value, self.increment_by, self.curr_value = results

    def get_ddl(self):
        """Produce the DDL necessary to create this sequence

        @return: DDL to create this sequence
        @rtype: String
        """
        ddl_strings = ["CREATE SEQUENCE " + self.name]
        if hasattr(self, 'curr_value') and self.curr_value != None:
            ddl_strings.append(" START WITH %d" % self.curr_value)
        if hasattr(self, 'min_value') and self.min_value > 1:
            ddl_strings.append(" MINVALUE %d" % self.min_value)
        if hasattr(self, 'max_value') and self.max_value != None:
            try:
                max_value = int(self.max_value)
            except OverflowError:
                # maxValue is 1.000E+27 which we can't convert to an int
                max_value = -1 
            if max_value > 1:
                ddl_strings.append(" MAXVALUE %d" % max_value)
        if hasattr(self, 'increment_by') and self.increment_by > 1:
            ddl_strings.append(" INCREMENT BY %d" % self.increment_by)
        ddl_strings.append(';\n')
        return "".join(ddl_strings)


class CodeObject(schema.CodeObject):
    """
    A representation of a database stored code object.

    Most of the methods for this class are inherited from schema.CodeObject

    For Oracle databases stored procedures and functions will be represented by
    a CodeObject. Database packages have their own sub-class called Package.
    """
    def _get_code_object(self, cursor):
        """
        Query the data dictionary for this code object

        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        stmt = """SELECT line, text 
                  FROM   user_source 
                  WHERE  name=:object_name
                  AND    type=:object_type
                  ORDER BY line"""
        cursor.execute(stmt, (self.name, self.type))
        self.source = []
        for code_line in cursor.fetchall():
            self.source.append(code_line)
        if self.type == 'PACKAGE':
            cursor.execute(stmt, (self.name, 'PACKAGE BODY'))
            self.body_source = []
            for code_line in cursor.fetchall():
                self.body_source.append(code_line)

    def get_ddl(self):
        """
        Produce the DDL necessary to create this code object

        @return: DDL to create this code object
        @rtype: String
        """
        if not self.source:
            return ""
        ddl_strings = ["CREATE OR REPLACE "]
        ddl_strings.extend([x[1] for x in self.source])
        return "".join(ddl_strings)


class Package(CodeObject):
    """
    A representation of a database stored code object.

    Most of the methods for this class are inherited from schema.CodeObject

    A key differentiator for Oracle is the Package. This is made up of a package
    header and a package body, each of which is a separate database object.
    These will have an extra attribute

      - body_source (does what it says on the tin)
    """
    def _get_code_object(self, cursor):
        """Query the data dictionary for this code object

        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        # Should call method on parent class rather than duplicate the code
        # CodeObject._get_code_object(self, cursor)
        stmt = """SELECT line, text 
                  FROM   user_source 
                  WHERE  name=:object_name
                  AND    type=:object_type
                  ORDER BY line"""
        uppercase_name = self.name.upper()
        cursor.execute(stmt, (uppercase_name, self.type.upper()))
        self.source = []
        for code_line in cursor.fetchall():
            self.source.append(code_line)
        cursor.execute(stmt, (uppercase_name, 'PACKAGE BODY'))
        self.body_source = []
        for code_line in cursor.fetchall():
            self.body_source.append(code_line)

    def get_body_ddl(self):
        """Produce the DDL for a package body

        @return: DDL to create a package body
        @rtype: String
        """
        if not self.body_source:
            return ""
        ddl_strings = ["CREATE OR REPLACE "]
        ddl_strings.extend([x[1] for x in self.body_source])
        return "".join(ddl_strings)


class DatabaseLink(object):
    """A representation of a database link.

    A database link is a way of accessing objects from another database without
    having to create another connection.

    This is, to the best of my knowledge, an Oracle specific concept so there is
    no super class to inherit from. This means that this class implements all of
    the 'standard' methods for schema objects (get_ddl, dump, to_xml, compare, 
    etc.)

    A database link has two attributes;
      - name  
      - connection_string
    """
    def __init__(self, name, cursor=None):
        """Initialise a database link object. If a value is passed into the
        cursor parameter then the last thing we do is call L{_get_database_link}.

        @param name: The name of this database link
        @type name: String
        @param cursor: When specified this is used to access the data dictionary for the details of this database link
        @type cursor: Database cursor object
        @return: Nothing
        """
        self.name = name
        self.connection_string = None
        if cursor:
            self._get_database_link(cursor)

    def _get_database_link(self, cursor):
        """Get the details of this database link from the data dictionary.

        @param cursor: A database cursor
        @type cursor: Database cursor object
        @return: Nothing
        """
        stmt = """SELECT username, password, host
                  FROM   user_db_links
                  WHERE  db_link=:db_link_name
               """
        cursor.execute(stmt, db_link_name=self.name.upper())
        results = cursor.fetchone()
        connection_string = ''
        # Older db links have values in all three fields, newer ones seem to
        # have the whole connection string in the 'host' column
        if results[0]:
            connection_string = results[0]+'/'+results[1]
            if results[2]:
                connection_string += '@' + results[2]
        elif results[2]:
            connection_string = results[2] # Seems to be the case in 10g
        self.connection_string = connection_string

    def get_ddl(self):
        """Produce the DDL necessar to create this database link

        @return: DDL to create this database link
        @rtype: String
        """
        ddl_string = "CREATE DATABASE LINK %s " % self.name
        ddl_string += "USING '%s'" % self.connection_string
        return ddl_string

    def dump(self):
        """Return the structure of this database link 
        
        Preferably in a nice easy to read format.

        @return: A description of this database link
        @rtype: String
        """
        outputs = ["Database link : %s" % self.name]
        outputs.append("  connection string : %s" % self.connection_string)
        return "\n".join(outputs)

    def to_xml(self):
        """Return the structure of this database link as an XML document 
        fragment

        This will be of the form::
          <database_link name="%s">
            <connection_string>%s</connection_string>
          </database_link>

        @return: An XML fragment describing this database link
        @rtype: String
        """
        xml_strings = ['<database_link name="%s">' % self.name]
        conn_string = '  <connection_string>%s' % self.connection_string
        conn_string += '</connection_string>'
        xml_strings.append(conn_string)
        xml_strings.append('</database_link>')
        return "\n".join(xml_strings)

    def __cmp__(self, other_database_link):
        if self.compare(other_database_link):
            return 1
        else:
            return 0

    def compare(self, other_db_link):
        """
        Calculate the differences between this db link and <other_db_link>

        @param other_db_link: Another database link to compare to this one
        @type other_db_link: A DatabaseLink object
        @return: The differences between the two database links or nothing if 
          they are equal
        @rtype: String
        """
        response = []
        if self.name != other_db_link.name:
            response.append('DIFF: Database link names: ')
            response.append('%s and %s' % (self.name, other_db_link.name))
        if hasattr(self, 'connection_string') or \
           hasattr(other_db_link, 'connection_string'):
            if hasattr(self, 'connection_string') and \
               hasattr(other_db_link, 'connection_string'):
                if self.connection_string != other_db_link.connection_string:
                    response.append('DIFF: Database link ')
                    response.append('connection strings: ')
                    response.append('%s and ' % self.connection_string)
                    response.append('%s' % other_db_link.connection_string)
            elif not hasattr(self, 'connection_string'):
                response.append('DIFF: Database link %s' % self.name)
                response.append('connection string')
            elif not hasattr(other_db_link, 'connection_string'):
                response.append('DIFF: Database link')
                response.append('%s connection string' % other_db_link.name)
        # If we have a response return it
        if len(response) > 0:
            return response


if __name__ == "__main__":
    print "This module should not be invoked from the command line"
    sys.exit(1)
