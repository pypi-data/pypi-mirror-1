#!/usr/bin/python
"""
Introduction
============
  Test suite for postgresSchema module from the gerald framework

  Note that this suite uses the py.test module to run
  (http://codespeak.net/py/current/doc/test.html)

Approach
========
  We want to test two different aspects of the postgresSchema module;
    - Reading a schema from a PostgreSQL database 
    - Specifying a schema using the in memory structures

  There will be tests for both of these approaches and hopefully some checking 
  that the two starting points produce the same results.

  To run these tests you must have a PostgreSQL database called 'gerald' with a 
  user called 'gerald' that has a password of 'gerald' running on a server that
  you can access. 

  These connection details should be recorded in URI form in the global variable
  TEST_CONNECTION_STRING

  Tests relying on an existing database will use the EXISTING_CONNECTION_STRING.
  Make sure that this points to a valid schema that contains one or more database
  objects.

  To Do;
    Read the connection strings from a configuration file that is not under
    version control
"""
__date__ = (2009, 1, 3)
__version__ = (0, 2, 4)
__author__ = "Andy Todd <andy47@halfcooked.com>"

import os
import re

# Imported solely so that we can access the Exception hierarchy
import psycopg2

from gerald import PostgresSchema
from gerald.postgres_schema import Table, View
from gerald.schema import Trigger as schema_trigger
from gerald.utilities.dburi import get_connection
import py.test

from gerald.utilities.Log import get_log

LOG_FILENAME = os.path.join(os.environ['HOME'], 'Temp', 'test_postgresschema.log')
log = get_log('test_postgresschema', LOG_FILENAME, 'INFO')

TEST_INSTANCE = ''
TEST_CONNECTION_STRING = 'postgres:/gerald:gerald@localhost/gerald'
if TEST_INSTANCE:
    TEST_CONNECTION_STRING += '@%s' % TEST_INSTANCE

# Make sure this points to an existing, valid, user in a PostgreSQL database 
EXISTING_CONNECTION_STRING = 'postgres:/andy47:w1bble@localhost/portfolio'

class TestSchemaNew:
    "Unit test for creating schemas using our Schema class"
    def test_empty(self):
        "Can we create an empty (in memory) schema"
        self.empty_schema = PostgresSchema('empty test')

    def test_name_attribute(self):
        "Does our schema object have a name attribute?"
        assert self.empty_schema.name == 'empty test'

    def test_version_attribute(self):
        "Does our schema object have a schema_api_version attribute?"
        assert hasattr(self.empty_schema, 'schema_api_version')

    def test_new_table(self):
        "Add a table to our empty (in memory) schema"
        self.table_name = 'test_table'
        new_table = Table(self.table_name)
        new_table.columns['col1'] = (1, 'col1', 'VARCHAR', 20, None, None, 'N', None, None)
        self.empty_schema.schema[self.table_name] = new_table

    def test_new_table_ddl(self):
        "Make sure that our new schema generates some DDL"
        assert self.empty_schema.get_ddl() != None

    def test_remove_table(self):
        "Remove the first table from the (in memory) schema"
        self.empty_schema.schema.pop(self.table_name)


class TestTableNew:
    "Unit tests for creating tables using our Table class"
    def test_empty(self):
        "Can we create an empty (in memory) table?"
        self.empty_table = Table('test_table')

    def test_empty_table_get_ddl(self):
        "Can we get valid DDL from this empty table?"
        ddl = self.empty_table.get_ddl() 
        log.debug(ddl)
        assert ddl == "CREATE TABLE test_table "

    def test_table_without_name(self):
        table = Table('no_name')
        table.name = None
        py.test.raises(AttributeError, table.get_ddl)

    def test_add_column(self):
        "Can we add a column to our new (in memory) table?"
        column_name = 'empty_column'
        column = (1, column_name, 'VARCHAR', 20, None, None, 'N', '', '')
        self.empty_table.columns[column_name] = column

    def test_one_column_get_ddl(self):
        "Is the ddl we get back correct?"
        ddl = self.empty_table.get_ddl()
        log.debug(ddl)
        assert ddl == "CREATE TABLE test_table\n ( empty_column VARCHAR(20) NOT NULL ) "


class TestViewNew:
    "Unit test for creating views using our View class"
    def test_empty(self):
        "Can we create an empty (in memory) view?"
        self.view_name = 'test_view'
        self.empty_view = View(self.view_name)

    def test_empty_view_get_ddl(self):
        "Can we get valid DDL from our empty view?"
        ddl = self.empty_view.get_ddl()
        log.debug(ddl)
        assert ddl == "CREATE VIEW %s" % self.view_name

    def test_view_without_name(self):
        view = View('no_name')
        view.name = None
        py.test.raises(AttributeError, view.get_ddl)

    def test_add_column(self):
        "Can we add a column to our new (in memory) view?"
        column_name = "empty_column"
        column = (1, column_name, 'VARCHAR', 20, None, None, 'N')
        self.empty_view.columns.append(column)
        self.empty_view.sql = "SELECT %s FROM dummy_table" % (column_name)

    def test_one_column_get_ddl(self):
        "Is the ddl we get back for our view correct?"
        ddl = self.empty_view.get_ddl()
        log.debug(ddl)
        assert ddl == "CREATE VIEW test_view ( empty_column ) AS\n  SELECT empty_column FROM dummy_table"


class TestSchemaDatabase:
    "Unit test for creating schemas from an existing database"

    def setup_class(self):
        "Set up our test connection"
        self.schema_name = 'public'
        self.test_schema = PostgresSchema(self.schema_name, EXISTING_CONNECTION_STRING)

    def test_invalid_connection_string(self):
        "If we try and create a schema using an invalid connection string we should get an exception"
        py.test.raises(psycopg2.OperationalError, PostgresSchema, 'invalid', 'postgres:/scot:tigger@localhost')

    def test_simple(self):
        "Test connecting to the 'test' database"
        assert self.test_schema is not None

    def test_dump(self):
        "Does the dump method work on an existing schema?"
        assert self.test_schema.dump() is not None

    def test_name(self):
        "The name of our schema should be the one we provided at initialisation"
        assert self.test_schema.name == self.schema_name

    def test_get_ddl(self):
        "The get_ddl method should return more than an empty string"
        assert self.test_schema.get_ddl() != None

    def test_to_xml(self):
        "The toXml method should return more than an empty string"
        assert self.test_schema.to_xml() != None

    def test_compare(self):
        "Test that equivalent schemas are indicated as such"
        duplicate_schema = PostgresSchema(self.schema_name, EXISTING_CONNECTION_STRING)
        assert self.test_schema == duplicate_schema


class TestTableFromDb:
    "Unit tests for determining the structure of a table from the database"
    def setup_class(self):
        "Create our table in the designated database"
        self.table_name = 'test_table_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.stmt = """CREATE TABLE %s
          ( col1 NUMERIC(16) NOT NULL 
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
        """ % (self.table_name, self.table_name)
        self.cursor.execute(self.stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our temporary table"
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.commit()

    def test_get_table_from_db(self):
        "Does the _getTable method work correctly?"
        self.table = Table(self.table_name, self.cursor)

    def test_ddl_round_trip(self):
        """Does the get_ddl method generate equivalent SQL to the original?
        
        This one gets tricky because the strings are never going to be exactly
        the same. So at the moment I simply test for the correct start to the
        returned string.
        """
        ddl = self.table.get_ddl()
        table_re = re.compile('CREATE\sTABLE\s%s' % self.table_name, re.IGNORECASE)
        assert table_re.match(ddl) != None

    def test_table_name(self):
        "Make sure the name attribute of our table is correct"
        assert self.table.name == self.table_name

    def todo_test_tablespace_name(self):
        "Make sure the tablespace_name attribute of our table is correct"
        assert self.table.tablespace_name == 'USERS'

    def test_table_type(self):
        "Make sure the table_type attribute of our table is correct"
        # Postgres tables shouldn't set the table_type, its only useful for MySQL
        assert self.table.table_type == None

    def test_table_dump(self):
        "Test the dump method on the table and make sure it produces some output"
        assert self.table.dump() != None

    def test_dump_with_constraints(self):
        "Make sure that the dump method includes the table constraints"
        dump_re = re.compile('Constraints;')
        assert dump_re.search(self.table.dump()) != None

    def test_table_to_xml(self):
        "Test that the to_xml method produces some output"
        assert self.table.to_xml().startswith('<table name="')

    def test_table_compare(self):
        "Test that our equivalent tables compare as such"
        table = Table(self.table_name, self.cursor)
        assert self.table == table

    def test_additional_columns(self):
        "Add a series of columns and after each check that _getTable still works"
        for column in ( 'varchar_col VARCHAR(255)'
            ,'char_col CHAR(255)'
            ,'integer_col INTEGER'
            ,'date_col DATE'
            ,'numeric_col NUMERIC(38,3)'
            # ,'float_col FLOAT(9,2)'
            ):
            yield self.add_column, column

    def add_column(self, column_definition):
        stmt = "ALTER TABLE %s ADD COLUMN %s" % (self.table_name, column_definition)
        log.debug(stmt)
        self.cursor.execute(stmt)
        self.db.commit()
        table = Table(self.table_name, self.cursor)

    def test_invalid_table_name(self):
        "Make sure an appopriate exception is raised if we ask for a non-existent table"
        py.test.raises(AttributeError, Table, None, self.cursor)


class TestTableAndIndexFromDb:

    def setup_class(self):
        "Create our table and index in the designated database"
        self.table_name = 'test_tab_index_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.table_stmt = """CREATE TABLE %s
          ( col1 NUMERIC(16) NOT NULL 
           ,col2 VARCHAR(200) 
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
        """ % (self.table_name, self.table_name)
        self.cursor.execute(self.table_stmt)
        self.index_stmt = """CREATE INDEX %s_ind1 ON %s ( col2 )""" % (self.table_name, self.table_name)
        self.cursor.execute(self.index_stmt)
        self.db.commit()

    def teardown_class(self):
        """Clean up our temporary table
        
        Dropping the table will drop the index so we don't need to do that 
        explicitly.
        """
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.commit()

    def test_get_table_from_db(self):
        "Does the _getTable method work correctly?"
        self.table = Table(self.table_name, self.cursor)

    def test_round_trip(self):
        """Does the get_ddl method generate equivalent SQL to the original?
        
        This one gets tricky because the strings are never going to be exactly
        the same. 
        """
        ddl = self.table.get_ddl()
        # Do they match after white space has been removed?
        table_re = re.compile('CREATE\sTABLE\s%s' % self.table_name, re.IGNORECASE)
        assert table_re.match(ddl) != None

    def test_index_round_trip(self):
        "Does the _getIndexDDL method generate the correct SQL?"
        index_ddl = self.table.get_index_ddl()
        log.debug(index_ddl)
        index_re = re.compile('CREATE\sINDEX\s%s_ind1' % self.table_name, re.IGNORECASE)
        assert index_re.match(index_ddl) != None


class TestCalcPrecision:
    "Test the calc_precision static method on the Table class"

    def test_data_length_only(self):
        assert Table.calc_precision('VARCHAR', '10', None, None) == '(10)'

    def test_data_length_and_others(self):
        "If a data_length is provided the data_precision and data_scale parameters are ignored"
        assert Table.calc_precision('VARCHAR', '15', 1, 1) == '(15)'

    def test_data_precision_and_scale(self):
        assert Table.calc_precision('NUMERIC', None, 9, 2) == '(9,2)'

    def test_data_type_irrelevant_length(self):
        "If we don't provide a data type we should get an exception raised"
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


class TestViewFromDb:

    def setup_class(self):
        "Create our view in the designated database"
        self.view_name = 'test_view_from_db'
        self.dummy_table_name = 'empty_table'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.dummy_table_stmt = "CREATE table %s (col1 VARCHAR(50))" % (self.dummy_table_name, )
        self.view_stmt = "CREATE VIEW %s (col1) AS SELECT col1 FROM %s" % (self.view_name, self.dummy_table_name)
        self.cursor.execute(self.dummy_table_stmt)
        self.db.commit()
        self.cursor.execute(self.view_stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our view"
        drop_view_stmt = 'DROP VIEW %s' % self.view_name
        drop_table_stmt = 'DROP TABLE %s' % self.dummy_table_name
        self.db.commit()
        self.cursor.execute(drop_view_stmt)
        self.cursor.execute(drop_table_stmt)
        self.cursor.close()
        self.db.commit()

    def test_get_view_from_db(self):
        "Does the _getView method work correctly?"
        self.db_view = View(self.view_name, self.cursor)

    def test_view_name(self):
        "Is the name attribute of our view set correctly?"
        assert self.db_view.name == self.view_name

    def test_view_sql(self):
        "Is the SQL attribute of the view set?"
        assert self.db_view.sql != None

    def test_view_columns_not_null(self):
        "Does this view have one or more columns defined?"
        assert len(self.db_view.columns) > 0

    def test_view_triggers(self):
        "If there are triggers defined are they valid?"
        if len(self.db_view.triggers) > 0:
            for trigger_name, trigger in self.db_view.triggers.items():
                assert isinstance(trigger, schema_trigger) == True

    def test_compare_views(self):
        "Does the comparison method work correctly?"
        new_view = View(self.view_name, self.cursor)
        assert self.db_view == new_view


class TestTableAndFkFromDb:
    """
    Test two tables with a foreign key defined between them.

    In this test case I'm also going to test composite primary keys which should
    be in separate unit tests but I'll split them if and when I encounter any
    errors.
    """

    def setup_class(self):
        "Create the necessary tables and constraints in the designated database"
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.parent_table_name = 'test_tab_cons1_from_db'
        self.parent_table_stmt = """CREATE TABLE %s
          ( col1 NUMERIC(16) NOT NULL 
           ,col2 VARCHAR(200) 
           ,CONSTRAINT %s_pk PRIMARY KEY (col1)
          )
        """ % (self.parent_table_name, self.parent_table_name)
        self.cursor.execute(self.parent_table_stmt)
        self.child_table_name = 'test_tab_cons2_from_db'
        self.child_fk_name = 'parent_child_fk'
        self.child_table_stmt = """CREATE TABLE %s
          ( cola NUMERIC(16) NOT NULL
           ,colb NUMERIC(9) NOT NULL
           ,colc VARCHAR(2000) 
           ,col1 NUMERIC(16) NOT NULL
           ,CONSTRAINT %s FOREIGN KEY (col1) REFERENCES %s (col1)
           ,CONSTRAINT %s_pk PRIMARY KEY (cola, colb)
          ) 
        """ % (self.child_table_name, self.child_fk_name, self.parent_table_name, self.child_table_name, )
        self.cursor.execute(self.child_table_stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our temporary tables"
        self.db.commit()
        stmt = 'DROP TABLE %s' % self.child_table_name
        self.cursor.execute(stmt)
        stmt = 'DROP TABLE %s' % self.parent_table_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.commit()

    def test_get_child_table_from_db(self):
        "Does the _getTable method work correctly for the child table?"
        self.child_table = Table(self.child_table_name, self.cursor)

    def test_constraint_defined(self):
        "Have we registered the foreign key owned by the child table?"
        assert self.child_table.constraints.has_key(self.child_fk_name)

    def test_constraint_type(self):
        "Is the constraint type correct?"
        constraint_type = self.child_table.constraints[self.child_fk_name][0]
        assert constraint_type == 'Foreign'

    def todo_test_constraint_columns(self):
        "Does the constraint contain the correct column(s)?"
        # Column names are a sequence after the constraint type
        columns = self.child_table.constraints[self.child_fk_name][1]

    def test_get_parent_table_from_db(self):
        "Does the _getTable method work correctly for the parent table?"
        self.parent_table = Table(self.parent_table_name, self.cursor)

    def test_table_and_fk_round_trip(self):
        """Does the _get_ddl method generate equivalent SQL to the original?
        
        This one gets tricky because the strings are never going to be exactly
        the same.

        We need to break our original DDL into its component parts and check 
        that they are present in the generated DDL string.

        Its also quite fragile because there is no guarantee what order the 
        columns or constraints are going to be included in the two different
        DDL strings. We should probably have some sort of tree of the key elements
        of the table and make sure that they are included in each string.
        """
        # Get the DDL from the objects we created in the last two tests
        parent_ddl = self.parent_table.get_ddl()
        child_ddl = self.child_table.get_ddl()
        parent_re = re.compile('^CREATE\sTABLE.*%s' % self.parent_table_name, re.IGNORECASE)
        child_re = re.compile('^CREATE\sTABLE.*%s' % self.child_table_name, re.IGNORECASE)
        # Do they match after white space has been removed?
        assert parent_re.match(parent_ddl) != None
        assert parent_re.match(self.parent_table_stmt) != None
        assert child_re.match(child_ddl) != None
        assert child_re.match(self.child_table_stmt) != None


