"""
Introduction
============
  Capture, document and manage database schemas.

  This is the Schema module, it contains one useful class, Schema. This is a 
  super class which is then sub-classed for specific databases (eg. 
  OracleSchema, MySQLSchema, etc).

  A schema is comprised of collections of tables, views, stored code objects, 
  triggers, sequences and other assorted 'objects'

  This module is licensed under the BSD License (see LICENSE.txt)

  This module requires Python 2.3 (and above) and a valid DB-API module

To do
=====
  - stored code objects class
  - change get_ddl method(s) to put different objects in different files like 
    Oracle Designer (one each for tables, constraints, views, code objects)
  - Table and View dump methods rely on calc_precision function, we really 
    should do away with this
  - One possible solution is to make Column a class and just implement a dump 
    method for that

Possible Future development
===========================
  - Support the Jakarta Torque schema DTD 
    (http://db.apache.org/torque/schema-reference.html) 
  - Or possibly the Dewdrop DTD 
    (http://dewdrop.sourceforge.net/xmlns/database.xsd)
  - Change the compare method for the Schema class. Perhaps using the difflib 
    library module?
  - Change the to_xml methods to use ElementTree elements rather than strings
"""
__author__ = "Andy Todd <andy47@halfcooked.com>"
__date__ = (2009, 1, 3)
__version__ = (0, 2, 4)

import os
import sys

from gerald.utilities.dburi import get_connection
from gerald.utilities.Log import get_log

if os.environ.has_key('TMP'):
    LOG_DIRECTORY = os.environ['TMP']
elif os.environ.has_key('HOME'):
    LOG_DIRECTORY = os.environ['HOME']
LOG_FILENAME = os.path.join(LOG_DIRECTORY, 'gerald.log')
LOG = get_log('gerald', LOG_FILENAME, 'INFO')

class Schema(object):
    """
    A representation of a database schema.

    A schema is a collection of objects within a database. It is a logical 
    grouping, physical implementation is independent of the schema.

    This is an abstract class which shouldn't be used directly. It is designed 
    to be sub-classed in database specific modules.

    These sub-classes will need to implement the _get_schema and __init__ methods

    A schema will have the following attributes

      - name. This will be the same as the connectionString
      - schema_api_version. To indicate when we are change the API
      - _db. A database connection. Optional, need not be provided by sub-classes.
        May be removed in future releases.
      - _cursor. A cursor generated from _db
      - schema. A collection of objects which form this schema.
    """
    def __init__(self, schema_name, connection_string=None):
        """
        Initialise the schema. 

        @param schema_name: A name for this schema
        @type schema_name: String
        @param connection_string: If this is provided then we populate the 
        schema's attributes from the database it connects us to.
        @type connection_string: String
        @return: Success or failure
        @rtype: Boolean
        """
        self.name = schema_name
        self.schema_api_version = 1.0
        self.schema = {}
        if connection_string:
            # Connect to the db and suck out the data dictionary information
            LOG.debug("Connecting to %s" % self.name)
            self._db = get_connection(connection_string)
            self._cursor = self._db.cursor()
            LOG.debug("Established connection to %s" % self.name)
            self.schema = self._get_schema(self._cursor)

    def _get_schema(self, cursor):
        "Place holder method to be implemented by child classes"
        return None

    def dump(self, file_name=None, sort=None):
        """
        Output this schema in a nice easy to read format to <file_name>. If a
        <file_name> isn't provided then we return the stream.
        
        We rely on each object to output its own details.

        @param file_name: The name of a file to dump the output to
        @type file_name: String
        @param sort: If this is set the schema objects will be sorted by name
        @type sort: Boolean
        @return: Schema contents or, if file_name is specified, nothing
        @rtype: String
        """
        if file_name:
            dump_file = open(file_name, 'w')
        results = ["Schema: %s\n" % self.name]
        objects = self.schema.keys()
        if sort:
            objects.sort()
        for schema_object in objects:
            results.append(self.schema[schema_object].dump())
        if file_name:
            dump_file.write('\n'.join(results))
            dump_file.close()
        else:
            return '\n'.join(results)

    def to_xml(self, file_name=None):
        """
        Output this schema in XML format to <file_name>. If a <file_name> isn't 
        provided then we return the stream.

        We rely on each object to produce its own XML fragment which are then
        combined here.

        @param file_name: The name of a file to dump the XML to
        @type file_name: String
        @return: Schema XML or, if file_name is specified, nothing
        @rtype: String
        """
        if file_name:
            xml_file = open(file_name, 'w')
        results = ['<schema name="%s">' % self.name]
        for schema_object in self.schema.keys():
            results.append(self.schema[schema_object].to_xml())
        results.append('</schema>')
        if file_name:
            xml_file.write('\n'.join(results))
            xml_file.close()
        else:
            return '\n'.join(results)

    def get_ddl(self, file_name=None):
        """
        Output the DDL to create this schema to <file_name>. If a <file_name> 
        isn't provided then we return the stream.

        We rely on each schema object to produce its own DDL statements which are 
        then combined here.

        @param file_name: The name of a file to dump the XML to
        @type file_name: String
        @return: Schema DDL or, if file_name is specified, nothing
        @rtype: String
        """
        results = []
        for schema_object in self.schema.keys():
            results.append(self.schema[schema_object].get_ddl())
        if file_name:
            ddl_file = open(file_name, 'w')
            ddl_file.write('\n'.join(results))
            ddl_file.close()
        else:
            return '\n'.join(results)

    def __cmp__(self, other_schema):
        """
        Compare this schema with <other_schema>
        
        @param other_schema: A schema to be compared to self
        @type other_schema: An object of a class inherited from schema.Schema
        @return: 0 if the two schemas are the same, otherwise we return 1
        @rtype: Boolean, well Integer really
        """
        # __cmp__ functions return -1 if we are less than schema
        #                          0 if we are the same as schema
        #                          1 if we are greater than schema
        # If our 'compare' method returns anything there are differences
        if self.compare(other_schema):
            return 1
        else:
            return 0

    def compare(self, other_schema):
        """
        Calculate the differences between the current schema and <other_schema>.
        
        @param other_schema: A schema to be compared to self
        @type other_schema: An object of a class inherited from schema.Schema
        @return: The differences between the two schemas
        @rtype: String
        """
        # I left a note here about difflib, but can't find it. Oh dear.
        results = []
        if not isinstance(other_schema, Schema):
            results.append('We are not comparing two schemas')
        else:
            if self.schema.keys() != other_schema.schema.keys():
                results.append('The schemas have different objects')
            for schema_object in self.schema.keys():
                if self.schema[schema_object].__class__ != \
                   other_schema.schema[schema_object].__class__:
                    results.append('%s is of different types' % schema_object)
                    results.append('in the two schemas')
                if self.schema[schema_object] != \
                   other_schema.schema[schema_object]:
                    results.append('%s is different ' % schema_object)
                    results.append('in the two schemas')
        return ''.join(results)


class Table(object):
    """
    A representation of a database table.
    
    A table is made up of columns and will have indexes, triggers, constraints,
    primary and foreign keys.

    It may also have comments - although this is currently only available in Oracle

    This is an abstract class which shouldn't be used. It is designed to be 
    sub-classed in database specific modules.

    The sub-classes will need to implement the L{_get_table} and L{get_ddl} 
    methods

    They will also need a class method called calc_precision, whose signature
    will depend on the module

    A table will have the following attributes

      - name
      - tablespace_name, or table_type (for MySQL)
      - columns. A dictionary (keyed on column name) of tuples of the form 
          - 0 - Sequence
          - 1 - Column name
          - 2 - Data type
          - 3 - Data length
          - 4 - Data precision
          - 5 - Data scale
          - 6 - Nullable
          - 7 - Default
          - 8 - Special - only used by MySQL to indicate if a column has auto_increment set
          - 9 - Comment - optional, only used by Oracle
      - indexes
      - constraints. A dictionary (keyed on constraint name) of tuples of the form
          - 0 - Constraint type (one of 'Primary', 'Foreign', 'Check' or 'Unique'
          - 1 - Constraint enabled? (one of 'Y' or 'N')
          - 2 - Columns. A sequence of the column names in this constraint
          - 3 - Reference table (only used for Foreign keys)
          - 4 - Reference columns (only used for Foreign keys)
          - 5 - Status (Y for enabled, N for disabled)
      - triggers. A dictionary of trigger objects keyed on name 
      - comments. Optional. A text string describing the table
    """
    def __init__(self, table_name, cursor=None):
        """
        Initialise a table object. If a value is passed into the cursor parameter
        then the last thing we do is call L{_get_table}.

        @param table_name: The name of this table
        @type table_name: String
        @param cursor: If this is provided then we use it to call L{_get_table}
        @type cursor: Database cursor object
        @return: Nothing
        """
        self.name = table_name
        self.tablespace_name = None
        self.table_type = None
        self.columns = {}
        self.indexes = {}
        self.constraints = {}
        self.triggers = {}
        if cursor:
            self._get_table(cursor)

    def _get_table(self, cursor):
        """
        Query the data dictionary for this table and populate the object 
        attributes

        Not implemented in this class as its database specific, but present 
        for completeness.

        @param cursor: A database cursor
        @type cursor: Database cursor object
        @return: Nothing
        """
        pass

    def dump(self):
        """
        Return the structure of the table in a nice, easy to read, format
        
        @return: A description of this table 
        @rtype: String
        """
         # This is pretty, but we could just return the ddl_string
        outputs = ["Table : %s\n" % self.name]
        cols = self.columns.values()
        cols.sort()
        for column in cols:
            outputs.append("  %-30s" % column[1])
            outputs.append(" %-15s " % column[2]+self.__class__.calc_precision(column[2], column[3], column[4], column[5]))
            if column[6] == 'Y':
                outputs.append(" NOT NULL")
            outputs.append("\n")
        # Constraints please
        if len(self.constraints) != 0:
            outputs.append("  Constraints;\n")
            for constraint_name, constraint in self.constraints.items():
                outputs.append("    %s, " % constraint_name)
                outputs.append("%s " % (constraint[0]))
                if len(constraint) > 2 and constraint[2]:
                    outputs.append(": %s" % constraint[2])
                outputs.append("\n")
        outputs.append("\n")
        return "".join(outputs)

    def get_ddl(self):
        """
        Generate the DDL necessary to create this table

        Not implemented in this class as its database specific.

        @return: DDL to create this table 
        @rtype: String
        """
        pass

    def to_xml(self):
        """
        Return the structure of this table as an XML document fragment
        
        This will be of the form::
          <table name="table name">
            <tablespace name="tablespace name" />
            <column name="name" data-type="data type" sequence="sequence">
              <length>x</length>
              <precision>x</precision>
              <scale>x</scale>
            </column>
            <column ...>
            <constraint name="constraint name" type="Primary|Foreign|Check">
              ... constraint details ...
            </constraint>
            ... trigger details ...
          </table>

        @return: An XML fragment describing this table 
        @rtype: String
        """
        xml_strings = ['<table name="%s">\n' % self.name]
        if self.tablespace_name:
            xml_strings.append('  <tablespace name=')
            xml_strings.append('"%s" />\n' % self.tablespace_name)
        for column in self.columns:
            col_details = self.columns[column]
            xml_strings.append('  <column name="%s"' % column)
            xml_strings.append(' data-type="%s"' % col_details[2])
            xml_strings.append(' sequence="%d">\n' % col_details[0])
            if col_details[3]:
                xml_strings.append('    <length>')
                xml_strings.append(str(col_details[3]))
                xml_strings.append('</length>\n')
            if col_details[4] and col_details[4] != 0:
                xml_strings.append('    <precision>')
                xml_strings.append(str(col_details[4])+'</precision>\n')
                if col_details[5]:
                    xml_strings.append('    <scale>')
                    xml_strings.append(str(col_details[5]))
                    xml_strings.append('</scale>\n')
            xml_strings.append('  </column>\n')
        for constraint in self.constraints.keys():
            cons_details = self.constraints[constraint]
            cons_type = cons_details[0]
            if cons_type != 'Check' or not constraint.startswith("SYS_C"):
                xml_strings.append('  <constraint name="%s"' % constraint)
                xml_strings.append(' type="%s">\n' % cons_type)
                if cons_type == 'Check':
                    xml_strings.append('   <details>')
                    xml_strings.append(cons_details[2])
                    xml_strings.append('</details>\n')
                if cons_type == 'Primary':
                    for column in cons_details[2]:
                        xml_strings.append('    <column name="%s" />\n' % column)
                if cons_type == 'Foreign':
                    xml_strings.append('    <jointable ')
                    xml_strings.append(' name="%s"' % cons_details[4])
                    xml_strings.append(' pk="%s">\n' % cons_details[3])
                    for col_index in range(len(cons_details[2])):
                        xml_strings.append('      <constraintcolumn')
                        name = cons_details[2][col_index]
                        xml_strings.append(' name="%s"' % name)
                        xml_strings.append(' joincolumn')
                        join_column = cons_details[5][col_index]
                        xml_strings.append('="%s" />\n' % join_column)
                    xml_strings.append('    </jointable>\n')
                xml_strings.append('  </constraint>\n')
        # Triggers
        for trigger in self.triggers:
            xml_strings.append(self.triggers[trigger].to_xml())
        xml_strings.append('</table>')
        return "".join(xml_strings)

    def __cmp__(self, other_table):
        """
        Compare this table with <other_table>

        @param other_table: A table to compare this one to
        @type other_table: An object of a class derived from Schema.Table
        @return: 0 if the two tables are the same, otherwise we return 1
        @rtype: Boolean, well integer really
        """
        # __cmp__ functions return -1 if we are less than schema
        #                          0 if we are the same as schema
        #                          1 if we are greater than schema
        # If our 'compare' method returns anything there are differences
        if self.compare(other_table):
            return 1
        else:
            return 0

    def compare(self, other_table):
        """
        Calculate the differences between the current table and <other_table>.

        @param other_table: Another table to compare to this one
        @type other_table: An object of a class derived from Schema.Table
        @return: The differences between the two tables
        @rtype: String
        """
        response = []
        if self.name != other_table.name:
            response.append('DIFF: Table names: %s and %s' % (self.name, other_table.name))
        if self.tablespace_name != other_table.tablespace_name:
            response.append('DIFF: Tablespace names: %s and %s' % (self.tablespace_name, other_table.tablespace_name))
        # Compare columns
        for column_name in self.columns.keys():
            if column_name in other_table.columns.keys():
                if self.columns[column_name] != other_table.columns[column_name]:
                    response.append('DIFF: Definition of %s is different' % column_name)
            else:
                response.append('DIFF: Column %s not in %s' % (column_name, other_table.name))
        for column_name in other_table.columns.keys():
            if column_name not in self.columns.keys():
                response.append('DIFF: Column %s not in %s' % (column_name, self.name))
        return "\n".join(response)


class View(object):
    """
    A representation of a database view.

    A View is made up of columns and also has an associated SQL statement.

    It may also have comments - although this is currently only available in Oracle

    This is an abstract class which shouldn't be used. It is designed to be 
    sub-classed in database specific modules.

    The sub-classes will need to implement the L{_get_view} and L{get_ddl} methods

    A view will have the following attributes
      - name
      - columns. A collection of tuples of the form (column_id, column_name,
        data_type, data_length, data_precision, data_scale, nullable)
      - sql. The SQL that forms the view
      - triggers. A dictionary of trigger objects keyed on name
    """
    def __init__(self, view_name, cursor=None):
        """
        Initialise a view object. 

        A view will have the following attributes

          - name
          - columns. A collection of tuples of the form
            (column_id, column_name, data_type, data_length, data_precision,
            data_scale, nullable)
          - sql. The SQL text which forms the body of the trigger
          - triggers. A dictionary of trigger objects keyed on name 

        @param view_name: The name of the view
        @type view_name: String
        @param cursor: An optional database cursor which, if provided, will be 
            used to populate this object's attributes by calling _getView
        @type cursor: Database cursor object
        @return: Nothing
        """
        self.name = view_name
        self.type = 'view' # Saves using type() or isinstance
        self.columns = []
        self.sql = ''
        self.triggers = {}
        if cursor:
            self._get_view(cursor)

    def _get_view(self, cursor):
        """
        Query the data dictionary for this view and populate the object attributes

        Not implemented in this class as it's database specific, but present
        for completeness.

        @param cursor: A database cursor
        @type cursor: Database cursor object
        @return: Nothing
        """
        pass

    def dump(self):
        """
        Output the structure of the view in a nice, easy to read, format

        @return: A description of this view
        @rtype: String
        """
        outputs = ["View : %s\n" % self.name]
        cols = self.columns[:] # Copy because we are going to ...
        cols.sort()
        for column in cols:
            outputs.append("  %-30s %-12s" % (column[1], column[2]))
            outputs.append("%7s" % self.__class__.calc_precision(column[2], column[3], column[4], column[5]))
            if column[6] == "N":
                outputs.append(" NOT NULL")
            outputs.append("\n")
        outputs.append("\n")
        outputs.append(self.sql+"\n")
        outputs.append("\n")
        return "".join(outputs)

    def to_xml(self):
        """
        Return the structure of this view as an XML document fragment
        
        This will be of the form::
          <view name="view name">
            <column name="column name" sequence="numeric indicator of order" />
            <column ...>
            <...>
            <sql>SQL text to create the view</sql>
          </view>

        @return: An XML fragment describing this view
        @rtype: String
        """
        xml_strings = ['<view name="%s">\n' % self.name]
        for column in self.columns:
            xml_strings.append('  <column name="%s"' % column[1])
            xml_strings.append(' sequence="%d" />\n' % column[0])
        xml_strings.append('  <sql>%s</sql>\n' % self.sql)
        xml_strings.append('</view>\n')
        return "".join(xml_strings)

    def get_ddl(self):
        """
        Generate the DDL necessary to create this view

        Not implemented in this class as its database specific.

        @return: DDL to create this table
        @rtype: String
        """
        pass

    def __cmp__(self, other_view):
        """
        Compare this view with <other_view>

        @param other_view: A view to compare this one to
        @type other_view: An object of a class derived from Schema.View
        @return: 0 if the two views are the same, otherwise we return 1
        @rtype: Boolean, well integer really
        """
        # __cmp__ functions return -1 if we are less than schema
        #                          0 if we are the same as schema
        #                          1 if we are greater than schema
        # If our 'compare' method returns anything there are differences
        if self.compare(other_view):
            return 1
        else:
            return 0

    def compare(self, other_view):
        """
        Calculate the differences between this view and <other_view>.

        @param other_view: Another view to compare to this one
        @type other_view: An object of a class derived from Schema.View
        @return: A string describing the differences between the two views
        """
        response = []
        if self.name != other_view.name:
            response.append('DIFF: View names:')
            response.append('%s and %s' % (self.name, other_view.name))
        # Compare columns
        tv_column_names = [col[1] for col in self.columns]
        ov_column_names = [col[1] for col in other_view.columns]
        for column in tv_column_names:
            if column not in ov_column_names:
                response.append('DIFF: Column %s' % column)
                response.append('not in %s' % other_view.name)
        for column in ov_column_names:
            if column not in tv_column_names:
                response.append('DIFF: Column %s' % column)
                response.append('not in %s' % self.name)
        return response


class Trigger(object):
    """
    A representation of a database trigger.

    A trigger has triggering events and a SQL statement. A trigger can only
    exist within the context of a table and thus doesn't need any table references
    as you can get those from its parent. Apart from the table name, of course,
    which we need for the get_ddl method.

    This is an abstract class which shouldn't be used. It is designed to be 
    sub-classed in database specific modules.

    The sub-classes will need to implement the L{_get_trigger} and L{get_ddl} 
    methods

    A trigger will have the following attributes

      - name
      - type. Row or Table
      - events. A list of the events that cause this trigger to fire
      - level. Is this a 'row' or 'statement' level trigger?
      - sql. The SQL that is executed when this trigger is fired
    """
    def __init__(self, trigger_name, cursor=None):
        """
        Initialise a trigger object. If a value is passed into the cursor 
        parameter then the last thing we do is call _get_trigger.

        @param trigger_name: The name of this trigger
        @type trigger_name: String
        @param cursor: If this is provided then we use it to call _get_trigger
        @type cursor: Database cursor object
        @return: Nothing
        """
        self.name = trigger_name
        self.table_name = None
        self.type = 'trigger' # Saves using type() or isinstance
        self.events = []
        self.sql = ''
        self.level = None
        if cursor:
            self._get_trigger(cursor)

    def _get_trigger(self, cursor):
        """
        Query the data dictionary for this trigger and populate the object 
        attributes

        Not implemented in this class as it's database specific, but present
        for completeness.

        @param cursor: A database cursor
        @type cursor: Database cursor object
        @return: Nothing
        """
        pass

    def dump(self):
        """
        Return the structure of the trigger in a nice, easy to read, format

        @return: A description of this trigger
        @rtype: String
        """
        outputs = ["Trigger : %s\n" % self.name]
        outputs.append(" %s %s " % (self.type, self.events))
        if self.level:
            outputs.append("ON %s\n" % self.level)
        outputs.append("\n")
        outputs.append(self.sql+"\n")
        outputs.append("\n")
        return "".join(outputs)

    def to_xml(self):
        """
        Return the structure of this trigger as an XML document fragment
        
        This will be of the form::
          <trigger name="view name">
            <type>trigger type</type>
            <level>trigger level</type>
            <events>triggering events</events/>
            <sql>SQL statement that is fired</sql>
          </trigger>

        @return: An XML fragment describing this trigger
        @rtype: String
        """
        xml_strings = ['  <trigger name="%s">\n' % self.name]
        xml_strings.append('    <type>%s</type>\n' % self.type)
        if self.level:
            xml_strings.append('    <level>%s</level>\n' % self.level)
        xml_strings.append('    <events>%s</events>\n' % self.events)
        xml_strings.append('    <sql>%s</sql>\n' % self.sql)
        xml_strings.append('  </trigger>\n')
        return "".join(xml_strings)

    def get_ddl(self):
        """
        Generate the DDL necessary to create this trigger

        Not implemented in this class as its database specific

        @return: DDL to create this trigger
        @rtype: String
        """
        pass

    def __cmp__(self, other_trigger):
        """
        Compare this trigger with <other_trigger>

        @param other_trigger: A trigger to compare this one to
        @type other_trigger: An object of a class derived from Schema.Trigger
        @return: 1 if triggers are different, 0 if they are the same
        @rtype: Boolean, well integer really
        """
        # __cmp__ functions return -1 if we are less than schema
        #                          0 if we are the same as schema
        #                          1 if we are greater than schema
        # If our 'compare' method returns anything there are differences
        if self.compare(other_trigger):
            return 1
        else:
            return 0

    def compare(self, other_trigger):
        """
        Calculate the differences between the current trigger and 
        <other_trigger>

        @param other_trigger: Another trigger to compare to this one
        @type other_trigger: An object of a class derived from Schema.Trigger
        @return: The differences between the two triggers
        @rtype: String
        """
        response = []
        if self.name != other_trigger.name:
            response.append('DIFF: Trigger names: %s' % self.name)
            response.append('and %s' % other_trigger.name)
        # Compare types
        if self.type != other_trigger.type:
            response.append('DIFF: Trigger %s type' % self.name)
            response.append('%s is different to ' % self.type)
            response.append('trigger %s ' % other_trigger.name)
            response.append('type %s' % other_trigger.type)
        # Compare triggering events
        if self.events != other_trigger.events:
            response.append('DIFF: Trigger %s' % self.name)
            response.append(' events %s is ' % self.events)
            response.append('different to trigger %s' % other_trigger.name)
            response.append('events %s' % other_trigger.events)
        # Compare SQL statements
        if self.sql != other_trigger.sql:
            response.append('DIFF: Trigger %s ' % self.name)
            response.append('SQL %s ' % self.sql)
            response.append('is different to trigger %s ' % other_trigger.name)
            response.append('SQL %s' % other_trigger.sql)
        return response


class Sequence(object):
    """
    A representation of a database sequence.

    A sequence is an in memory construct that provides numbers in a sequence. 
    They are generally used to generate primary key values.

    This is an abstract class which shouldn't be used. It is designed to be 
    sub-classed in database specific modules.

    The sub-classes will need to implement the L{_get_sequence} and L{get_ddl} 
    methods

    A sequence will have the following attributes

      - name
      - min_value
      - max_value
      - increment_by
      - curr_value
    """
    def __init__(self, sequence_name, cursor=None):
        """
        Initialise a sequence object. If a value is passed into the cursor 
        parameter then the last thing we do is call L{_get_sequence}.

        @param sequence_name: The name of this sequence
        @type sequence_name: String
        @param cursor: If this is provided then we use it to call L{_get_sequence}
        @type cursor: Database cursor object
        @return: Nothing
        """
        self.name = sequence_name
        self.type = 'sequence' # Saves using type() or isinstance
        self.min_value = None
        self.max_value = None
        self.increment_by = None
        self.curr_value = None
        if cursor:
            self._get_sequence(cursor)

    def _get_sequence(self, cursor):
        """
        Query the data dictionary for this sequence and populate the object
        attributes
        
        Not implemented in this class as it's database specific, but present
        for completeness.

        @param cursor: A database cursor
        @type cursor: Database cursor object
        @return: Nothing
        """
        pass

    def dump(self):
        """
        Return the structure of the sequence in a nice, easy to read, format

        @return: A description of this sequence
        @rtype: String
        """
        outputs = ["Sequence : %s" % self.name]
        outputs.append("  start : %d" % self.curr_value)
        outputs.append("  minimum : %d" % self.min_value)
        outputs.append("  maximum : %d" % self.max_value)
        if self.increment_by > 1:
            outputs.append("  increment : %d" % self.increment_by)
        return "\n".join(outputs)

    def to_xml(self):
        """
        Return the structure of this sequence as an XML document fragment
        
        This will be of the form::
          <sequence name="%s">
            <start value="%d" />
            <minimum value="%d" />
            <maximum value="%d" />
            <increment value="%d" />
          </sequence>

        @return: An XML fragment describing this sequence
        @rtype: String
        """
        xml_strings = ['<sequence name="%s">' % self.name]
        if hasattr(self, 'currval'):
            xml_strings.append('  <start value="%d" />' % self.curr_value)
        if self.min_value > 1:
            xml_strings.append('  <minimum value="%d" />' % self.min_value)
        try:
            xml_strings.append('  <maximum value="%d" />' % self.max_value)
        except OverflowError:
            None # maxValue is 1.000E+27 which we can't convert to an int
        if self.increment_by > 1:
            xml_strings.append('  <increment value="%d" />'% self.increment_by)
        xml_strings.append('</sequence>')
        return "".join(xml_strings)

    def get_ddl(self):
        """
        Generate the DDL necessary to create this sequence

        Not implemented in this class as it's database specific

        @return: DDL to create this sequence
        @rtype: String
        """
        pass

    def __cmp__(self, other_sequence):
        """
        Compare this sequence with <other_sequence>

        @param other_sequence: A sequence to compare this one to
        @type other_sequence: An object of a class derived from Schema.Sequence
        @return: 0 if the two sequences are the same, otherwise we return 1
        @rtype: Boolean, well integer really
        """
        # __cmp__ functions return -1 if we are less than schema
        #                          0 if we are the same as schema
        #                          1 if we are greater than schema
        # If our 'compare' method returns anything there are differences
        if self.compare(other_sequence):
            return 1
        else:
            return 0

    def compare(self, other_sequence):
        """
        Calculate the differences between this sequence and <other_sequence>

        @param other_sequence: Another sequence to compare to this one
        @type other_sequence: An object of a class derived from Schema.Sequence
        @return: The differences between the two sequences
        @rtype: String
        """
        response = []
        if self.name != other_sequence.name:
            response.append('DIFF: Sequence names: %s' % self.name)
            response.append('and %s' % other_sequence.name)
        if self.increment_by != other_sequence.increment_by:
            response.append('DIFF: Increment interval')
            response.append('is %d,' % self.increment_by)
            response.append('for %s' % other_sequence.name)
            response.append('it is %d' % other_sequence.increment_by)
        if self.min_value != other_sequence.min_value:
            response.append('DIFF: Min value is %d' % self.min_value)
            response.append(' for %s' % other_sequence.name)
            response.append('it is %d' % other_sequence.min_value)
        if self.max_value != other_sequence.max_value:
            response.append('DIFF: Max value is %d' % self.max_value)
            response.append(', for %s ' % other_sequence.name)
            response.append('it is %d' % other_sequence.max_value)
        # The only attribute we don't check is currval, becuase it will be 
        # different in 999 cases out of a 1000
        return response


class CodeObject(object):
    """
    A representation of a database code object.

    This is an abstract class which shouldn't be used. It is designed to be 
    sub-classed in database specific modules.

    The sub-classes will need to implement the L{_get_code_object} and 
    L{get_ddl} methods

    A code object will have the following attributes

      - name
      - type (usually one of function, procedure or package)
      - source code (a sequence of (line number, code) sequences
    """
    def __init__(self, code_object_name, code_object_type, cursor=None):
        """
        Initialise a code object. If a value is passed into the cursor 
        parameter then the last thing we do is call L{_get_code_object}.

        @param code_object_name: The name of this code object
        @type code_object_name: String
        @param code_object_type: The type of this code object (function, 
          procedure, etc)
        @type code_object_type: String
        @param cursor: If this is provided then we use it to call 
          L{_get_code_object}
        @type cursor: Database cursor object
        @return: Nothing
        """
        self.name = code_object_name
        self.type = code_object_type
        self.source = []
        if cursor:
            self._get_code_object(cursor)

    def _get_code_object(self, cursor):
        """
        Query the data dictionary for this code object and populate the object
        attributes
        
        Not implemented in this class as it's database specific, but present
        for completeness.

        @param cursor: A database cursor
        @type cursor: Database cursor object
        @return: Nothing
        """
        pass

    def dump(self):
        """
        Return the structure of the code object in a nice, easy to read, format

        @return: A description of this code object
        @rtype: String
        """
        outputs = ["Code object : %s" % self.name]
        outputs.append("  Type : %s" % self.type)
        outputs.append(self.source)
        return "".join(outputs)

    def to_xml(self):
        """
        Return the structure of this code object as an XML document fragment
        
        This will be of the form::
          <code_object name="%s">
            <type value="%s" />
            <source>
              .. The source code to recreate this object ..
            </source>
          </code_object>

        @return: An XML fragment describing this code object
        @rtype: String
        """
        pass

    def get_ddl(self):
        """
        Generate the DDL necessary to create this code object

        Not implemented in this class as it's database specific

        @return: DDL to create this code object
        @rtype: String
        """
        pass

    def __cmp__(self, other_code_object):
        """
        Compare this code object with <other_code_object>

        @param other_code_object : A code object to compare this one to
        @type other_code_object : An object of a class derived from Schema.CodeObject
        @return: True if the two sequences are the same, otherwise False
        @rtype: Boolean
        """
        # If our 'compare' method returns anything there are differences
        if self.compare(other_code_object):
            return True
        else:
            return False

    def compare(self, other_code_object):
        """
        Calculate the differences between this code object and <other_code_sequence>

        @param other_code_object: Another code object to compare to this one
        @type other_code_object: An object of a class derived from Schema.CodeObject
        @return: The differences between the two code objects
        @rtype: String
        """
        pass


if __name__ == "__main__":
    print "This module should not be invoked from the command line"
    sys.exit(1)
