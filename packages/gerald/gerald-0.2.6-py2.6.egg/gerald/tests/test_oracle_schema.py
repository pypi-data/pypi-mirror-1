#!/usr/bin/python
"""
Introduction
============
  Test suite for oracle_schema module from the gerald framework

  Note that this suite uses the py.test module to run
  (http://codespeak.net/py/current/doc/test.html)

Approach
========
  We want to test two different aspects of the oracle_schema module;
    - Reading a schema from an Oracle database 
    - Specifying a schema in the in memory structures

  There will be tests for both of these approaches and hopefully some checking 
  that the two starting points produce the same results.

  To run these tests you must have an Oracle schema called 'gerald' with a 
  password of 'gerald' in a database that you can access. Alter the global 
  variable TEST_INSTANCE to specify the connection identifier that describes 
  the database containing this schema.

  If you want to use a different schema then change TEST_CONNECTION_STRING

  Tests relying on an existing database will use the EXISTING_CONNECTION_STRING.
  Make sure that this points to a valid schema that contains one or more database
  objects.

  Because this module uses xml.etree for ElementTree you must be running Python 
  2.5 or later.

  To Do;
    Read the connection strings from a configuration file that is not under
    version control
"""
__date__ = (2009, 1, 2)
__version__ = (0, 2, 4)
__author__ = "Andy Todd <andy47@halfcooked.com>"

import os
import re
from xml.etree import ElementTree

# Used in all of the round trip tests
ws_re = re.compile('\s')

# Imported solely so that we can access the Exception hierarchy
import cx_Oracle

from gerald import OracleSchema
from gerald.oracle_schema import Table, CodeObject, Package, Sequence, View, DatabaseLink
from gerald.schema import Trigger as schema_trigger
from gerald.utilities.dburi import get_connection
import py.test

from gerald.utilities.Log import get_log
LOG_FILENAME = os.path.join(os.environ['HOME'], 'Temp', 'test_oracleschema.log')
log = get_log('test_oracleschema', LOG_FILENAME, 'INFO')

TEST_INSTANCE = ''
TEST_CONNECTION_STRING = 'oracle:/gerald:gerald'
if TEST_INSTANCE:
    TEST_CONNECTION_STRING += '@%s' % TEST_INSTANCE

# Make sure this points to an existing, valid, user in an Oracle database 
EXISTING_CONNECTION_STRING = 'oracle:/portfolio:portfolio'

class TestSchemaNew:
    "Unit test for creating schemas using our Schema class"
    def setup_class(self):
        self.schema_name = 'empty test'

    def test_empty(self):
        "Can we create an empty (in memory) schema"
        empty_schema = OracleSchema(self.schema_name)

    def test_name_attribute(self):
        "Does our schema object have a name attribute?"
        assert OracleSchema(self.schema_name).name == self.schema_name

    def test_version_attribute(self):
        "Does our schema object have a schema_api_version attribute?"
        assert hasattr(OracleSchema(self.schema_name), 'schema_api_version')


class TestSchemaAddTable:
    "Unit tests for adding a table to a new, empty Schema"
    def setup_class(self):
        self.schema_name = 'empty test'
        self.empty_schema = OracleSchema(self.schema_name)

    def test_new_table(self):
        "Add a table to our empty (in memory) schema"
        table_name = 'test_table'
        new_table = Table(table_name)
        new_table.tablespace_name = 'USERS'
        new_table.columns['col1'] = (1, 'col1', 'VARCHAR2', 20, None, None, 'N', "'Default value'", None, None)
        self.empty_schema.schema[table_name] = new_table

    def test_new_table_ddl(self):
        log.debug('Empty schema with table DDL : %s' % self.empty_schema.get_ddl())
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

    def test_empty_table_get_ddl(self):
        "Can we get valid DDL from this empty table?"
        ddl = Table(self.table_name).get_ddl() 
        assert ddl == "CREATE TABLE test_table;\n"

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
        column = [1, self.column_name, 'VARCHAR2', 20, None, None, 'NOT NULL', '', '', '']
        self.empty_table.columns[self.column_name] = column

    def test_one_column_get_ddl(self):
        ddl = self.empty_table.get_ddl()
        assert ddl == "CREATE TABLE test_table\n ( empty_column VARCHAR2(20) );\n"

    def test_add_table_comment(self):
        "Can we add a comment to our new (in memory) table?"
        comment = "A comment on test_table"
        self.empty_table.comments = comment
        assert self.empty_table.comments == comment

    def test_table_comment_get_ddl(self):
        ddl = self.empty_table.get_ddl()
        assert ddl == "CREATE TABLE test_table\n ( empty_column VARCHAR2(20) );\nCOMMENT ON TABLE test_table IS 'A comment on test_table';\n"

    def test_add_column_comment(self):
        "Can we add a comment to one of the columns of our new table?"
        comment = "A comment on empty_column"
        self.empty_table.columns[self.column_name][9] = comment
        assert self.empty_table.columns[self.column_name][9] == comment

    def test_column_comment_get_ddl(self):
        "Is the correct DDL returned for our new table with comments?"
        ddl = self.empty_table.get_ddl()
        assert ddl == "CREATE TABLE test_table\n ( empty_column VARCHAR2(20) );\nCOMMENT ON TABLE test_table IS 'A comment on test_table';\nCOMMENT ON COLUMN test_table.empty_column IS 'A comment on empty_column';\n"


class TestViewNew(object):
    "Unit test for creating views using our View class"
    def setup_class(self):
        self.view_name = 'test_view'

    def test_empty(self):
        "Can we create an empty (in memory) view?"
        self.empty_view = View(self.view_name)

    def test_empty_view_get_ddl(self):
        "Can we get valid DDL from our empty view?"
        ddl = View(self.view_name).get_ddl()
        assert ddl == "CREATE VIEW test_view"

    def test_view_without_name(self):
        view = View('no_name')
        view.name = None
        py.test.raises(AttributeError, view.get_ddl)


class TestCodeObjectNew(object):
    "Unit test for creating code objects using our CodeObject class"
    def setup_class(self):
        self.co_name = 'empty_proc'
        self.co_type = 'PROCEDURE'

    def test_empty(self):
        "Can we create an empty (in memory) code object?"
        self.empty_co = CodeObject(self.co_name, self.co_type)

    def test_no_type_fails(self):
        "Trying to create a code object without a type should fail"
        py.test.raises(TypeError, CodeObject, self.co_name)

    def test_empty_co_get_ddl(self):
        "get_ddl on our empty code object should return an empty statement"
        ddl = CodeObject(self.co_name, self.co_type).get_ddl()
        assert ddl == ""


class TestSequenceNew(object):
    "Unit test for creating sequences using our Sequence class"
    def setup_class(self):
        self.sequence_name = 'empty_sequence'

    def test_empty(self):
        "Can we create an empty (in memory) sequence?"
        self.empty_seq = Sequence(self.sequence_name)

    def test_empty_ddl(self):
        "Our new empty sequence shouldn't have any values in its attributes"
        assert Sequence(self.sequence_name).get_ddl() == "CREATE SEQUENCE empty_sequence;\n"

    def test_spurious_attribute(self):
        "Test that adding a spurious attribute doesn't effect the get_ddl output"
        empty_seq = Sequence(self.sequence_name)
        ddl = empty_seq.get_ddl()
        empty_seq.wibble = 'wibble'
        assert ddl == empty_seq.get_ddl()

    def test_full(self):
        "Can we add attributes to our in memory sequence"
        sequence = Sequence('full_sequence')
        sequence.min_value = 10
        sequence.curr_value = 103
        sequence.max_value = 200000
        sequence.increment_by = 5
        assert sequence.get_ddl() == "CREATE SEQUENCE full_sequence START WITH 103 MINVALUE 10 MAXVALUE 200000 INCREMENT BY 5;\n"


class TestSchemaDatabase(object):
    "Unit test for creating schemas from an existing database"

    def setup_class(self):
        "Set up our test connection"
        self.schema_name = 'portfolio'
        self.test_schema = OracleSchema(self.schema_name, EXISTING_CONNECTION_STRING)

    def test_invalid_connection_string(self):
        "If we try and create a schema using an invalid connection string we should get an exception"
        py.test.raises(cx_Oracle.DatabaseError, OracleSchema, 'invalid', 'oracle:/scot:tigger')

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
        duplicate_schema = OracleSchema(self.schema_name, EXISTING_CONNECTION_STRING)
        assert self.test_schema == duplicate_schema


class TestTableParent(object):

    def setup_class(self):
        "Create our table in the designated database"
        self.table_name = 'test_table_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(10) DEFAULT 'default' NOT NULL
           ,col3 VARCHAR2(20)
           ,col4 DATE
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.table_name, self.table_name)
        self.cursor.execute(self.stmt)
        self.db.commit()
        self.table_comment = 'A meaningful comment on our table'

    def teardown_class(self):
        "Clean up our temporary table"
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()

    def test_get_table_from_db(self):
        "Does the _getTable method work correctly?"
        self.table = Table(self.table_name, self.cursor)


class TestTableFromDb(TestTableParent):

    def setup_method(self, method):
        "Create the table object we are going to test"
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

    def test_tablespace_name(self):
        "Make sure the tablespace_name attribute of our table is correct"
        assert self.table.tablespace_name == 'USERS'

    def test_table_type(self):
        "Make sure the table_type attribute of our table is correct"
        # Oracle tables shouldn't set the table_type, its only useful for MySQL
        assert self.table.table_type == None

    def test_table_dump(self):
        "Test the dump method on the table and make sure it produces some output"
        assert self.table.dump() != None

    def test_table_to_xml(self):
        "Does the to_xml method on the table produce some output"
        assert self.table.to_xml().startswith('<table name="')

    def test_table_to_xml_roundtrip(self):
        "Is the output from the to_xml method valid"
        xml_string = self.table.to_xml()
        xml_fragment = ElementTree.fromstring(xml_string)

    def test_column_default(self):
        "Is the default defined against a column picked up correctly?"
        assert self.table.columns['COL2'][7] == "'default' "

    def test_additional_columns(self):
        "Add a series of columns and after each check that _getTable still works"
        for column in ( 'varchar_col VARCHAR2(255)'
            ,'char_col CHAR(255)'
            ,'integer_col INTEGER'
            ,'date_col DATE'
            ,'numeric_col NUMERIC(38,3)'
            # ,'float_col FLOAT(9,2)'
            ):
            yield self.add_column, column

    def add_column(self, column_definition):
        stmt = "ALTER TABLE %s ADD ( %s )" % (self.table_name, column_definition)
        self.cursor.execute(stmt)
        table = Table(self.table_name, self.cursor)

    def test_invalid_table_name(self):
        "Make sure an appopriate exception is raised if we ask for a non-existent table"
        py.test.raises(AttributeError, Table, None, self.cursor)


class TestTableCompare(TestTableParent):

    def setup_method(self, method):
        "Create the table object we are going to test"
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
        assert self.table.compare(table) == 'DIFF: Column extra not in test_table_from_db'


class TestAddComments(TestTableParent):

    def test_add_comment(self):
        "Can we add a table comment direct to the database?"
        stmt = "COMMENT ON TABLE %s IS '%s'" % (self.table_name, self.table_comment)
        self.cursor.execute(stmt)

    def test_add_column_comment(self):
        "Can we add a column comment direct to the database?"
        self.column_comment = 'A meaningful comment on a column in our table'
        stmt = "COMMENT ON COLUMN %s.%s IS '%s'" % (self.table_name, 'col1', self.column_comment)
        self.cursor.execute(stmt)

    def test_add_long_column_comment(self):
        "Can we add a long (>255 character) comment direct to the database?"
        self.long_column_comment = 'abcdefghijklmnopqrstuvwxyz1234567890' * 10
        stmt = "COMMENT ON COLUMN %s.%s IS '%s'" % (self.table_name, 'col2', self.long_column_comment)
        self.cursor.execute(stmt)

    def test_add_short_column_comment(self):
        "Can we add a short (1 character) comment direct to the database?"
        self.short_column_comment = 'a'
        stmt = "COMMENT ON COLUMN %s.%s IS '%s'" % (self.table_name, 'col3', self.short_column_comment)
        self.cursor.execute(stmt)


class TestTableComments(object):
    """Test the retrieval of comments against tables and columns direct from the
    database.
    """

    def setup_class(self):
        "Create our table in the designated database"
        self.table_name = 'test_table_for_comments'
        db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = db.cursor()
        stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(10) DEFAULT 'default' NOT NULL
           ,col3 VARCHAR2(20)
           ,col4 DATE
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.table_name, self.table_name)
        self.cursor.execute(stmt)
        # Table level comment
        self.table_comment = 'A meaningful comment on our table'
        stmt = "COMMENT ON TABLE %s IS '%s'" % (self.table_name, self.table_comment)
        self.cursor.execute(stmt)
        # Column comment
        self.column_comment = 'A meaningful comment on a column in our table'
        stmt = "COMMENT ON COLUMN %s.%s IS '%s'" % (self.table_name, 'col1', self.column_comment)
        self.cursor.execute(stmt)
        db.commit()

    def test_get_table_comment(self):
        "Does the table comment we have created get included in the round trip DDL?"
        table = Table(self.table_name, self.cursor)
        ddl = table.get_ddl()
        assert ddl.find(self.table_comment) != -1

    def test_get_column_comment(self):
        "Does the column comment we have created get included in the round trip DDL?"
        table = Table(self.table_name, self.cursor)
        ddl = table.get_ddl()
        assert ddl.find(self.column_comment) != -1

    def teardown_class(self):
        "Clean up our temporary table"
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestTableCompareDiff(object):

    def setup_class(self):
        "Create our table in the designated database"
        # Create the first (base) table
        self.table_name = 'test_table_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(10) NOT NULL
           ,col3 VARCHAR2(20)
           ,col4 DATE
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.table_name, self.table_name)
        log.debug('Creating table %s' % self.table_name)
        self.cursor.execute(self.stmt)
        # This is necessary because it is used in the test method
        self.table = Table(self.table_name, self.cursor)
        # Create the table to compare to
        self.new_table_name = 'test_table_from_db2'
        new_table = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL
           ,col2 VARCHAR2(10) NOT NULL
           ,col3 VARCHAR2(20)
           ,col4 DATE
           ,col5 VARCHAR2(255)
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.new_table_name, self.new_table_name)
        log.debug('Creating table %s' % self.new_table_name)
        self.cursor.execute(new_table)
        self.db.commit()

    def test_different_tables_compare(self):
        "Make sure that comparing almost equivalent tables returns the actual differences"
        table = Table(self.new_table_name, self.cursor)
        assert self.table.compare(table) == "DIFF: Table names: test_table_from_db and test_table_from_db2\nDIFF: Column COL5 not in test_table_from_db"

    def teardown_class(self):
        "Clean up our temporary table"
        for table_name in (self.table_name, self.new_table_name):
            stmt = 'DROP TABLE %s' % table_name
            log.debug('Dropping table %s' % table_name)
            self.cursor.execute(stmt)
        self.cursor.close()


class TestMixedCaseTableName(object):
    """Make sure that our code can cope with tables (or other objects) that have
    mixed case names
    """

    def setup_class(self):
        "Create our table in the designated database"
        # Create the first (base) table
        self.table_name = '"Mixed_Case_Table"'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(10) NOT NULL
           ,col3 VARCHAR2(20)
           ,col4 DATE
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.table_name, self.table_name.strip('"'))
        log.debug('Creating table %s' % self.table_name)
        self.cursor.execute(self.stmt)

    def test_get_table_definition(self):
        "Make sure that we can get the details of a table with a mixed case name"
        self.table = Table(self.table_name, self.cursor)

    def teardown_class(self):
        "Clean up our temporary table"
        stmt = 'DROP TABLE %s' % self.table_name
        log.debug('Dropping table %s' % self.table_name)
        self.cursor.execute(stmt)
        self.cursor.close()


class TestTableAndIndexFromDb(object):

    def setup_class(self):
        "Create our table and index in the designated database"
        self.table_name = 'test_tab_index_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.table_stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(200) 
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.table_name, self.table_name)
        self.cursor.execute(self.table_stmt)
        self.index_stmt = """CREATE INDEX %s_ind1 ON %s ( col2 )""" % (self.table_name, self.table_name)
        self.cursor.execute(self.index_stmt)
        self.db.commit()

    def setup_method(self, method):
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
        "Does the get_index_ddl method generate the correct SQL?"
        index_ddl = self.table._get_index_ddl()
        index_re = re.compile('CREATE\sINDEX\s%s_ind1' % self.table_name, re.IGNORECASE)
        assert index_re.match(index_ddl) != None

    def teardown_class(self):
        """Clean up our temporary table
        
        Dropping the table will drop the index so we don't need to do that 
        explicitly.
        """
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestTableAndFkFromDb(object):
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
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(200) 
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.parent_table_name, self.parent_table_name)
        self.cursor.execute(self.parent_table_stmt)
        self.child_table_name = 'test_tab_cons2_from_db'
        self.child_table_stmt = """CREATE TABLE %s
          ( cola NUMBER(16) NOT NULL
           ,colb NUMBER(9) NOT NULL
           ,colc VARCHAR2(2000) 
           ,col1 NUMBER(16) NOT NULL
           ,CONSTRAINT parent_child_fk FOREIGN KEY (col1) REFERENCES %s (col1)
           ,CONSTRAINT %s_pk PRIMARY KEY (cola, colb)
          ) TABLESPACE USERS
        """ % (self.child_table_name, self.parent_table_name, self.child_table_name, )
        self.cursor.execute(self.child_table_stmt)
        self.db.commit()

    def setup_method(self, method):
        self.child_table = Table(self.child_table_name, self.cursor)
        self.parent_table = Table(self.parent_table_name, self.cursor)

    def test_table_and_fk_round_trip(self):
        """Does the get_ddl method generate equivalent SQL to the original?
        
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

    def test_exact_parent_ddl(self):
        """Very fragile test to test (character by character) the output of get_ddl

        Ideally this should be covered by the previous test but this is an 
        interim measure until I improve my regex fu.
        """
        expected_parent_ddl = "CREATE TABLE %s\n ( COL1 NUMBER(16) NOT NULL\n  ,COL2 VARCHAR2(200) )\n TABLESPACE USERS;\nALTER TABLE %s ADD CONSTRAINT %s_PK PRIMARY KEY (COL1);\n" % (self.parent_table_name, self.parent_table_name, self.parent_table_name.upper())
        assert self.parent_table.get_ddl() == expected_parent_ddl

    def test_dump_with_constraints(self):
        "Make sure that the dump method includes the table constraints"
        dump_re = re.compile('Constraints;')
        assert dump_re.search(self.child_table.dump()) != None

    def teardown_class(self):
        """Clean up our temporary tables
        """
        stmt = 'DROP TABLE %s' % self.child_table_name
        self.cursor.execute(stmt)
        stmt = 'DROP TABLE %s' % self.parent_table_name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestCalcPrecision(object):
    "Test the calc_precision static method on the Table class"
    def test_data_length_only(self):
        assert Table.calc_precision('VARCHAR2', '10', None, None) == '(10)'

    def test_data_length_and_others(self):
        "If a data_length is provided the data_precision and data_scale parameters are ignored"
        assert Table.calc_precision('VARCHAR2', '15', 1, 1) == '(15)'

    def test_data_precision_and_scale(self):
        assert Table.calc_precision('NUMBER', None, 9, 2) == '(9,2)'

    def test_data_type_irrelevant_length(self):
        "Not providing a data type will raise an exception"
        py.test.raises(ValueError, Table.calc_precision, None, '20', None, None)

    def test_date_data_type(self):
        "If the column is a date data type then we should get an empty return string"
        assert Table.calc_precision('DATE', None, None, None) == ''

    def test_timestamp_data_type(self):
        "If the column is a timestamp data type then we should get an empty return string"
        assert Table.calc_precision('TIMESTAMP', None, None, None) == ''

    def test_data_type_irrelevant_precision(self):
        "Not providing a data type will raise an exception"
        py.test.raises(ValueError, Table.calc_precision, None, None, 11, 3)

    def test_negative_length(self):
        "Providing a negative data_length should raise an exception"
        py.test.raises(ValueError, Table.calc_precision, 'VARCHAR2', -1, None, None)

    def test_zero_length(self):
        "Providing a zero data_length should raise an exception"
        py.test.raises(ValueError, Table.calc_precision, 'VARCHAR2', 0, None, None)


class TestCodeObjectFromDb(object):

    def setup_class(self):
        "Create our code object(s) in the designated database"
        self.proc_name = 'test_procedure_from_db'
        self.proc_type = 'PROCEDURE'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        stmt = """CREATE PROCEDURE %s (param1 INTEGER, param2 VARCHAR2) AS
          l_string_length NUMBER;
        BEGIN
          param1 := param1 + 1;
          l_string := len(param2);
        END;
        """ % self.proc_name
        self.cursor.execute(stmt)
        self.db.commit()

    def test_get_co_from_db(self):
        "Does the _getCodeObject method work correctly?"
        proc = CodeObject(self.proc_name, self.proc_type, self.cursor)

    def teardown_class(self):
        "Clean up our temporary code object(s)"
        stmt = 'DROP PROCEDURE %s' % self.proc_name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestPackageFromDb(object):

    def setup_class(self):
        "Create our code object(s) in the designated database"
        self.name = 'test_package_from_db'
        self.type = 'PACKAGE'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        stmt = """CREATE PACKAGE %s AS
          FUNCTION test_func(param1 VARCHAR2) RETURN NUMBER;

          g_package_variable DATE;
        END;
        """ % self.name
        self.cursor.execute(stmt)
        stmt = """CREATE PACKAGE BODY %s AS
          FUNCTION test_func(param1 VARCHAR2) RETURN NUMBER IS
          BEGIN
            IF to_date(param1) != g_package_variable THEN
              RETURN 1;
            ELSE
              RETURN 0;
            END IF;
          END;
        END;
        """ % self.name
        self.cursor.execute(stmt)
        self.db.commit()

    def setup_method(self, method):
        # This could be in the setup_class method but no harm running it a few
        # times
        self.package = Package(self.name, self.type, self.cursor)

    def test_package_spec(self):
        "Does the package specification start with the correct text?"
        package_spec = self.package.get_ddl()
        package_re = re.compile('^CREATE\sOR\sREPLACE\sPACKAGE.*%s' % self.name, re.IGNORECASE)
        assert package_re.match(package_spec) != None

    def test_package_body(self):
        "Does the correct package body get returned by the appropriate method?"
        package_body = self.package.get_body_ddl()
        package_body_re = re.compile('^CREATE\sOR\sREPLACE\sPACKAGE\sBODY.*%s' % self.name, re.IGNORECASE)
        assert package_body_re.match(package_body) != None

    def teardown_class(self):
        "Clean up our temporary code object(s)"
        stmt = 'DROP PACKAGE %s' % self.name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestSequence(object):
    "Abstract class providing setup and teardown methods for Sequence tests"

    def setup_class(self):
        "Create our sequence in the designated database"
        self.sequence_name = 'test_sequence_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.stmt = 'CREATE SEQUENCE %s' % self.sequence_name
        self.cursor.execute(self.stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our sequence"
        stmt = 'DROP SEQUENCE %s' % self.sequence_name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestSequenceFromDb(TestSequence):
    "Test cases for sequence returned from the database"

    def test_get_sequence_from_db(self):
        "Does the _getSequence method work correctly?"
        self.db_sequence = Sequence(self.sequence_name, self.cursor)


class TestSequenceXml(TestSequence):

    def setup_method(self, method):
        "Note that this method is already tested in TestSequenceFromDb"
        self.db_sequence = Sequence(self.sequence_name, self.cursor)

    def test_sequence_to_xml(self):
        "Does the to_xml method on the sequence produce some output?"
        assert self.db_sequence.to_xml().startswith('<sequence name="')

    def test_sequence_to_xml_roundtrip(self):
        "Is the output from the to_xml method valid"
        xml_string = self.db_sequence.to_xml()
        xml_fragment = ElementTree.fromstring(xml_string)


class TestViewParent(object):

    def setup_class(self):
        "Create our view in the designated database"
        self.view_name = 'TEST_VIEW_FROM_DB'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.stmt = "CREATE VIEW %s (col1) AS SELECT 'x' col1 FROM dual" % self.view_name
        self.cursor.execute(self.stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our view"
        stmt = 'DROP VIEW %s' % self.view_name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestViewFromDb(TestViewParent):

    def test_get_view_from_db(self):
        "Does the _getView method work correctly?"
        self.db_view = View(self.view_name, self.cursor)


class TestViewMethodsAttributes(TestViewParent):

    def setup_method(self, method):
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

    def test_view_ddl(self):
        "Is the get_ddl method returning the correct value?"
        assert self.db_view.get_ddl() == "CREATE VIEW TEST_VIEW_FROM_DB ( COL1 ) AS\n  SELECT 'x' col1 FROM dual"

    def test_view_dump(self):
        "Do we get valid output from the dump method?"
        assert self.db_view.dump() is not None

    def test_view_triggers(self):
        "If there are triggers defined are they valid?"
        if len(self.db_view.triggers) > 0:
            for trigger_name, trigger in self.db_view.triggers.items():
                assert isinstance(trigger, schema_trigger) == True

    def test_compare_views(self):
        "Does the comparison method work correctly?"
        new_view = View(self.view_name, self.cursor)
        assert self.db_view == new_view

    def test_view_to_xml(self):
        "Does the to_xml method on the view produce some output"
        assert self.db_view.to_xml().startswith('<view name="')

    def test_view_to_xml_roundtrip(self):
        "Is the output from the to_xml method valid"
        xml_string = self.db_view.to_xml()
        xml_fragment = ElementTree.fromstring(xml_string)


class TestDatabaseLinkCreation(object):

    def setup_class(self):
        self.db_link_name = 'test_db_link'
        self.db_link_conn = 'user/password@schema'

    def test_database_link(self):
        "Can we create a new database link?"
        self.db_link = DatabaseLink(self.db_link_name)

    def test_add_connection_string(self):
        "Can we add a connection string to our new db link?"
        self.db_link = DatabaseLink(self.db_link_name)
        self.db_link.connection_string = self.db_link_conn

class TestDatabaseLink(object):

    def setup_class(self):
        self.db_link_name = 'test_db_link'
        self.db_link = DatabaseLink(self.db_link_name)
        self.db_link_conn = 'user/password@schema'
        self.db_link.connection_string = self.db_link_conn

    def test_ddl(self):
        "Does the DatabaseLink.get_ddl method return the expected results?"
        assert self.db_link.get_ddl() == "CREATE DATABASE LINK test_db_link USING 'user/password@schema'"

    def test_dump(self):
        "Does the DatabaseLink.dump method return the expected results?"
        assert self.db_link.dump() == "Database link : test_db_link\n  connection string : user/password@schema"

    def test_to_xml(self):
        "Does the DatabaseLink.to_xml method return the expected results?"
        assert self.db_link.to_xml() == '<database_link name="test_db_link">\n  <connection_string>user/password@schema</connection_string>\n</database_link>'

    def test_true_compare(self):
        "Does the DatabaseLink.compare method return the expected results?"
        other_db_link = DatabaseLink(self.db_link_name)
        other_db_link.connection_string = self.db_link_conn
        assert self.db_link.compare(other_db_link) == None

    def test_true_cmp(self):
        "Does the DatabaseLink.__cmp__ method return the expected results?"
        other_db_link = DatabaseLink(self.db_link_name)
        other_db_link.connection_string = self.db_link_conn
        assert self.db_link == other_db_link

    def test_false_compare(self):
        "Does the DatabaseLink.compare method return false when it should?"
        other_db_link = DatabaseLink(self.db_link_name)
        # Note that we aren't specifying a connection_string here
        assert self.db_link.compare(other_db_link) != None


class TestDatabaseLinkFromDb:
    pass
