#!/usr/bin/python
"""
Introduction
============
  Test suite for mySQLSchema module from the gerald framework

  Note that this suite uses the py.test module 
  (http://codespeak.net/py/current/doc/test.html)

Approach
========
  We want to test two different aspects of the mySQLSchema module;
    - Reading a schema from a MySQL database 
    - Specifying a schema in the in memory structures

  There will be tests for both of these approaches and hopefully some checking 
  that the two starting points produce the same results.

  To run these tests you must have a MySQL database on the local server called 
  'gerald_test'. Additionally the database must contain a user called 'gerald'
  with the password 'gerald' that has full rights to this database.

  You can create this catalog and user by running the create_mysql_test.sql
  script in the 'scripts' directory of the distribution root.

  If this is not the case then modify the value of TEST_CONNECTION_STRING

  Tests relying on an existing schema will use the EXISTING_CONNECTION_STRING.
  Modify this to point to a database that has one or more objects.

  Note that because this script imports ElementTree from xml.etree you will need
  to be running Python 2.5 or later

  To Do;
    Read the connection strings from a configuration file that is not under
    version control.
"""
__date__ = (2009, 1, 3)
__version__ = (0, 2, 4)
__author__ = "Andy Todd <andy47@halfcooked.com>"

import os
import re
from xml.etree import ElementTree

from gerald import MySQLSchema
from gerald.mysql_schema import Table
from gerald.utilities.dburi import get_connection
from gerald.utilities.Log import get_log

import py.test
# Imported solely so that we can gain access to its exception hierarchy
import MySQLdb

LOG_FILENAME = os.path.join(os.environ['HOME'], 'Temp', 'test_mysqlschema.log')
log = get_log('test_mysqlschema', LOG_FILENAME, 'INFO')
TEST_CONNECTION_STRING = 'mysql:/gerald:gerald@localhost/gerald_test'
EXISTING_CONNECTION_STRING = 'mysql:/andy47:w1bble@localhost/portfolio'

class TestSchemaNew(object):
    "Unit tests for creating schemas using our Schema class"
    def setup_class(self):
        self.schema_name = 'empty test'

    def test_empty(self):
        "Can we create an empty (in memory) schema"
        empty_schema = MySQLSchema(self.schema_name)

    def test_name_attribute(self):
        "Does our schema object have a name attribute?"
        assert MySQLSchema(self.schema_name).name == self.schema_name

    def test_version_attribute(self):
        "Does our schema object have a schema_api_version attribute?"
        assert hasattr(MySQLSchema(self.schema_name), 'schema_api_version')


class TestSchemaAddTable(object):
    "Test the addition of objects to a new Schema"

    def setup_class(self):
        self.schema_name = 'empty test'
        self.empty_schema = MySQLSchema(self.schema_name)

    def test_new_table(self):
        "Add a table to our empty (in memory) schema"
        table_name = 'test_table'
        new_table = Table(table_name)
        new_table.table_type = 'InnoDB'
        new_table.columns['col1'] = (1, 'col1', 'VARCHAR', 20, None, None, 'NOT NULL', None, None)
        self.empty_schema.schema[table_name] = new_table

    def test_new_table_ddl(self):
        "Make sure that we generate valid DDL for our new schema"
        assert self.empty_schema.get_ddl() != None

    def test_remove_table(self):
        "Remove the first table from the (in memory) schema"
        pass


class TestTableNew(object):
    "Unit tests for creating tables using our Table class"
    def setup_class(self):
        self.table_name = 'test_table'

    def test_empty(self):
        "Can we create an empty (in memory) table?"
        empty_table = Table(self.table_name)

    def test_empty_get_ddl(self):
        "Can we get valid DDL from this empty table?"
        ddl = Table(self.table_name).get_ddl() 
        log.info(ddl)
        assert ddl == "CREATE TABLE test_table"

    def test_table_without_name(self):
        table = Table('no_name')
        table.name = None
        py.test.raises(AttributeError, table.get_ddl)


class TestTableAddColumns(object):
    "Unit tests for adding columns and comments to a new table"
    def setup_class(self):
        self.empty_table = Table('test_table')
        self.column_name = 'empty_column'

    def test_add_column(self):
        "Can we add a column to our new (in memory) table?"
        column_name = 'empty_column'
        column = (1, column_name, 'VARCHAR', 20, None, None, 'NOT NULL', '', '')
        self.empty_table.columns[column_name] = column

    def test_one_column_get_ddl(self):
        ddl = self.empty_table.get_ddl()
        log.info(ddl)
        assert ddl == "CREATE TABLE test_table\n ( empty_column VARCHAR(20) DEFAULT NOT NULL"

    def test_add_invalid_column(self):
        pass
        """ 
        AJT 2006.11.07 - This test will only be valid when we have a Column class
        "Add an enum column with a value in the 'special' field, this shouldn't happen"
        column_name = 'impossible_column'
        column = (2, column_name, 'enum', None, 1, 2, 'NULL', None, '1,2')
        py.test.raises(TypeError, "self.empty_table.columns[column_name] = column")
        """


class TestTableParent(object):

    def setup_class(self):
        "Create our table in the designated database"
        log.debug("Setting up TestTableFromDb")
        self.table_name = 'test_table_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        stmt = 'CREATE TABLE %s' % self.table_name
        stmt += ' ( col1 INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY '
        stmt += ' )'
        self.cursor.execute(stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our temporary table"
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()

    def test_get_table_from_db(self):
        "Does the _getTable method work correctly?"
        self.table = Table(self.table_name, self.cursor)


class TestTableFromDb(TestTableParent):

    def add_column(self, column_definition):
        stmt = "ALTER TABLE %s ADD ( %s )" % (self.table_name, column_definition)
        self.cursor.execute(stmt)
        table = Table(self.table_name, self.cursor)

    def test_additional_columns(self):
        "Add a series of columns and after each check that _getTable still works"
        for column in (
                'varchar_col VARCHAR(255)'
               ,'char_col CHAR(255)'
               ,'varbinary_col VARBINARY(1000)'
               ,'integer_col INTEGER'
               ,'date_col DATE'
               ,'datetime_col DATETIME'
               ,'timestamp_col TIMESTAMP'
               ,'numeric_col NUMERIC(65,3)'
               ,'decimal_col DECIMAL(12,3)'
               ,'float_col FLOAT(9,2)'
               ,"enum_col ENUM('0', '1', '2', '3')"
               ):
            yield self.add_column, column

    def test_data_length_type(self):
        "Make sure that the data length attribute of columns is a number"
        table = Table(self.table_name, self.cursor)
        vc_col = table.columns['varchar_col']
        # Duck typing check - is dataLength (the fourth attribute) a number?
        assert vc_col[3] + 1 > vc_col[3]

    def test_data_precision_type(self):
        "Make sure that the data precision attribute of columns is a number"
        table = Table(self.table_name, self.cursor)
        dec_col = table.columns['decimal_col']
        # Duck typing check - is dataScale (the fifth attribute) a number?
        assert dec_col[4] + 1 > dec_col[4]

    def test_data_scale_type(self):
        "Make sure that the data scale attribute of columns is a number"
        table = Table(self.table_name, self.cursor)
        dec_col = table.columns['decimal_col']
        # Duck typing check - is dataScale (the sixth attribute) a number?
        assert dec_col[5] + 1 > dec_col[5]

    def test_invalid_table_name(self):
        "Make sure an appopriate exception is raised if we ask for a non-existent table"
        py.test.raises(AttributeError, Table, None, self.cursor)


class TestTableCompare(TestTableParent):

    def setup_method(self, method):
        "Each test case requires a table object to have been created"
        self.table = Table(self.table_name, self.cursor)

    def test_table_equivalence(self):
        "Test that our equivalent tables are equivalent"
        table = Table(self.table_name, self.cursor)
        assert self.table == table

    def test_table_compare(self):
        "Test that comparing the same table to itself returns an empty string"
        table = Table(self.table_name, self.cursor)
        assert self.table.compare(table) == ""

    def test_different_tables_not_equivalent(self):
        "Test that different tables are not equivalent"
        table = Table(self.table_name, self.cursor)
        table.columns['extra'] = (99, 'EXTRA', 'VARCHAR2', 10, None, None, 'Y', None)
        assert self.table != table

    def test_different_tables_compare(self):
        "Make sure that comparing different tables returns the actual differences"
        table = Table(self.table_name, self.cursor)
        table.columns['extra'] = (99, 'extra', 'varchar', 10, None, None, 'Y', None)
        assert self.table.compare(table) == "DIFF: Column extra not in test_table_from_db"


class TestTableAndIndexFromDb(object):

    def setup_class(self):
        "Create our table and index in the designated database"
        self.table_name = 'test_tab_index_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.table_stmt = """CREATE TABLE %s
          ( col1 INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY 
           ,col2 VARCHAR(200)
          )""" % (self.table_name, )
        self.cursor.execute(self.table_stmt)
        self.index_stmt = """CREATE INDEX %s_ind1 ON %s (col2)""" % (self.table_name, self.table_name)
        self.cursor.execute(self.index_stmt)
        self.db.commit()

    def setup_method(self, method):
        self.table = Table(self.table_name, self.cursor)

    def test_get_table_from_db(self):
        "Does the mySQLSchema.Table._getTable method work correctly?"
        self.table = Table(self.table_name, self.cursor)

    def test_to_xml(self):
        "Does the to_xml method return something?"
        assert self.table.to_xml().startswith('<table name="')

    def test_to_xml_roundtrip(self):
        "Make sure that the XML returned from to_xml is valid"
        xml_string = self.table.to_xml()
        xml_fragment = ElementTree.fromstring(xml_string)

    def test_dump_with_constraints(self):
        "Make sure that the dump method includes the table constraints"
        dump_re = re.compile('Constraints;')
        assert dump_re.search(self.table.dump()) != None

    def teardown_class(self):
        "Clean up after ourselves"
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestSimpleTableRoundTrip(object):
    """
    Actual SQL comparison is difficult as I would have to tokenize both strings
    and ensure the important parts were equivalent, resulitng in more test
    code than is absolutely necessary.

    The tests in this class will be straightforward and only look for things
    that are known to be problematic.
    """

    def setup_class(self):
        log.debug("Setting up TestSimpleTableFromDb")
        self.table_name = 'test_table_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.stmt = 'CREATE TABLE %s' % self.table_name
        self.stmt += ' ( col1 INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY '
        self.stmt += ' )'
        self.cursor.execute(self.stmt)
        self.db.commit()

    def test_table_name_round_trip(self):
        """Test round tripping of table DDL

        Create a Table object based on the table we created in the setup method
        and then check that its get_ddl method produces equivalent SQL to the 
        initial statement.
        """
        table = Table(self.table_name, self.cursor)
        ddl = table.get_ddl()
        creation_re = re.compile('^CREATE\sTABLE.*%s' % self.table_name, re.IGNORECASE)
        # Check that both strings contain our regular expression
        assert creation_re.match(ddl) != None
        assert creation_re.match(self.stmt) != None

    def teardown_class(self):
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestSchemaDatabase(object):
    "Unit test for creating schemas from an existing database"
    def setup_class(self):
        "Test connecting to the 'test' database"
        self.schema_name = 'test schema'
        self.test_schema = MySQLSchema(self.schema_name, EXISTING_CONNECTION_STRING)

    def test_invalid_connection_string(self):
        "If we try and create a schema without a valid connection string we should raise an exception"
        py.test.raises(MySQLdb.DatabaseError, MySQLSchema, 'invalid', 'mysql:/error:error@error/error')

    def test_simple(self):
        "Test that the setup method actually returned something"
        assert self.test_schema is not None

    def test_dump(self):
        "Does the schema dump method return something?"
        assert self.test_schema.dump() is not None

    def test_name(self):
        "Does the schema name get correctly set?"
        assert self.test_schema.name == self.schema_name

    def test_get_ddl(self):
        "The get_ddl method should return more than an empty string"
        assert self.test_schema.get_ddl() is not None

    def test_to_xml(self):
        "The to_xml method should return something"
        assert self.test_schema.to_xml() is not None

    def test_compare(self):
        "Comparing a schema with itself should return True"
        duplicate_schema = MySQLSchema(self.schema_name, EXISTING_CONNECTION_STRING)
        assert self.test_schema == duplicate_schema


class TestTableColumnType(object):
    """Test the determine_column_type static method on the Table class
    """

    def test_dct_datetime(self):
        assert Table.determine_column_type('datetime') == ('datetime', None, None, None, None)

    def test_dct_tiny_unsigned(self):
        "Can the function split up a column def with something after the length"
        assert Table.determine_column_type('tinyint(2) unsigned') == \
                ('tinyint', 2, None, None, 'unsigned')


class TestCalcPrecision(object):
    "Test the calc_precision static method on the Table class"
    def test_data_length_only(self):
        assert Table.calc_precision('varchar', '10', None, None) == '(10)'

    def test_data_length_and_others(self):
        "If a data_length is provided the data_precision and data_scale parameters are ignored"
        assert Table.calc_precision('varchar', '15', 1, 1) == '(15)'

    def test_data_precision_and_scale(self):
        assert Table.calc_precision('numeric', None, 9, 2) == '(9,2)'

    def test_data_type_irrelevant_length(self):
        "If we don't provide a data type an exception should be raised"
        py.test.raises(ValueError, Table.calc_precision, None, '20', None, None)

    def test_date_data_type(self):
        "If the column is a date data type then we should get an empty return string"
        assert Table.calc_precision('date', None, None, None) == ''

    def test_data_type_irrelevant_precision(self):
        "Not providing a data type will raise an exception"
        py.test.raises(ValueError, Table.calc_precision, None, None, 11, 3)

    def test_negative_length(self):
        "Providing a negative data_length should raise an exception"
        py.test.raises(ValueError, Table.calc_precision, 'varchar', -1, None, None)

    def test_zero_length(self):
        "Providing a zero data_length should raise an exception"
        py.test.raises(ValueError, Table.calc_precision, 'varchar', 0, None, None)
