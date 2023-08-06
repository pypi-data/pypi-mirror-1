"""
Introduction
============
  Capture, document, and manage MySQL database schemas.

  This is the mysql_schema module, it contains one useful class, Schema. This 
  is a sub-class of Schema (from the schema.py file in this directory).

  A schema is comprised of collections of tables, views, stored code objects, 
  triggers, and other assorted 'objects'

  For reference, here are the current valid data types in MySQL

  Text Data Types
  ---------------

  'char', 'varchar', 'tibyblob', 'tinytext', 'blob', 'text', 'mediumblob', 
  'mediumtext', 'longblob', 'longtext'

  Numeric Data Types
  ------------------
  'int', 'tinyint', 'smallint', 'mediumint', 'bigint', 'float', 'double', 
  'decimal'


Meta-data
=========
  Module  : mysql_schema.py
 
  License : BSD License (see LICENSE.txt)

To do
=====
  - change get_ddl method(s) to put different objects in different files like 
    Oracle Designer (one each for tables, constraints, views, code objects)

"""
__author__ = "Andrew J Todd esq <andy47@halfcooked.com>"
__date__ = (2009, 1, 3)
__version__ = (0, 2, 4)

import sys

import schema

LOG = schema.LOG

DATE_DATATYPES = ('date', 'datetime', 'time', 'timestamp', 'year')

class Schema(schema.Schema):
    """
    A representation of a MySQL database schema
    
    A MySQL schema is a database on a particular host. MySQL currently doesn't
    support views, triggers or sequences.
    """
    def _get_schema(self, cursor):
        """
        Get definitions for the objects in the current schema
        
        @param cursor: The cursor to use to query the data dictionary
        @type cursor: Database cursor object
        @return: All of the objects in this schema
        @rtype: Dictionary
        """
        schema = {}
        # Tables
        stmt = """SHOW TABLES"""
        cursor.execute(stmt)
        for table in self._cursor.fetchall():
            schema[table[0]] = Table(table[0], cursor)
        return schema


class Table(schema.Table):
    """
    A representation of a database table.
    
    A table is made up of columns and will have indexes, triggers, primary keys 
    and foreign keys.
    Note that MySQL doesn't support tablespaces, but does have a table_type.
    The columns sequence is made up of the following elements;
      - 0 - Sequence
      - 1 - Column name
      - 2 - Data type
      - 3 - Data length
      - 4 - Data precision
      - 5 - Data scale
      - 6 - Nullable ('Y' or 'N')
      - 7 - Default value
      - 8 - Special (things like auto increment)
    """
    def calc_precision(data_type, data_length, data_precision, data_scale):
        """
        Calculate and then retun the precision of a column
        
        The value returned will depend on the provided values, if we just
        receive data_length then we return that encapsulated in braces, if
        we get data_precision and data_scale (for a numeric column for instance)
        we return those encapsulated with braces.

        This is a bit of a hack and will be replaced when columns become first 
        class objects.

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
        if not data_type:
            raise ValueError, "data_type parameter is mandatory"
        elif data_type in DATE_DATATYPES:
            return ''
        elif data_length:
            if data_length > 0:
                return "(%s)" % data_length
            else:
                raise ValueError, 'Data length must be greater than 0'
        elif (data_precision > 0 and data_scale >= 0):
            return "(%s,%s)" % (data_precision, data_scale)
        else:
            raise ValueError, 'data_length, data_precision and data_scale must be non-zero'

    calc_precision = staticmethod(calc_precision)

    def determine_column_type(column_def):
        """
        Split the type component of a column definition acquired from the database
        into its components parts

        Which will turn these input values into these return values;

          - datetime      - data_type = 'datetime'
          - int(11)       - data_type = 'int', data_length=11
          - decimal(13,3) - data_type = 'decimal', data_scale=13, data_precision=3
          - smallint(5) unsigned - data_type = 'smallint', data_length=5, special='unsigned'
          - enum(1,2,3) - data_type = 'enum', special='1,2,3'

        @param column_def: The definition of a database column acquired from the MySQL describe
        @type column_def: String
        @return: Definition of a column as described in the class doc string
        @rtype: Tuple of (data type, data length, data precision,
                          data scale, special)
        """
        data_type = None
        data_length = None
        data_precision = None
        data_scale = None
        special = None
        if column_def.find('(') > 0:
            # The data type and length are in the same field, we split them out
            data_type, data_length = column_def.split('(')
            # Special case for 'enum' columns
            if data_type == 'enum':
                special = data_length
                data_length = None
            # otherwise look for definitions like n,m and split them up
            elif data_length.find(',') > 0:
                data_precision, data_scale = data_length.split(',')
                # Remove the trailing ')'
                if data_scale.find(')') > 0: 
                    data_scale = data_scale[:-1]
                # Turn precision and scale into integers
                data_precision = int(data_precision)
                data_scale = int(data_scale)
                data_length = None
            # If there is a ')' within the string put the remainder in special
            elif data_length.find(')') > 0 and \
                    data_length.find(')') < (len(data_length)-1):
                data_length, special = data_length.split(')')
                # Just in case there are extra spaces at the beginning or end
                special = special.strip()
            elif data_length.find(')') > 0: data_length = data_length[:-1]
        else: # Just a plain data type like datetime
            data_type = column_def
        # Make sure data_length, data_precision and data_scale are not strings
        if isinstance(data_length, str):
            data_length = int(data_length)
        if isinstance(data_precision, str):
            data_precision = int(data_precision)
        if isinstance(data_scale, str):
            data_scale = int(data_scale)
        return (data_type, data_length, data_precision, data_scale, special)

    determine_column_type = staticmethod(determine_column_type)

    def _get_table(self, cursor):
        """
        Query the data dictionary for the details of this table
        
        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        # Table information
        LOG.debug("Getting details of table %s" % self.name)
        stmt = """SHOW TABLE STATUS LIKE '%s'""" % self.name
        cursor.execute(stmt)
        result = cursor.fetchone()
        if result is None:
            raise AttributeError, "Can't get DDL for table %s" % self.name
        self.table_type = result[1]
        # We define the columns for this table
        pk_columns = []
        col_seq = 0
        # This gives us data about each column in the form;
        # (field, type, null, key, default, special)
        stmt = """SHOW COLUMNS FROM %s""" % self.name
        cursor.execute(stmt)
        for row in cursor.fetchall():
            col_seq += 1
            column_name = row[0]
            result = self.determine_column_type(row[1])
            data_type, data_length, data_precision, data_scale, special = result
            # We convert the third element to NULL or NOT NULL
            if row[2] == 'YES':
                nullable = 'Y'
            else:
                nullable = 'N'
            if not special:
                special = row[5]
            elif row[5] != '':
                msg = "Column has unexpected definition : %s" % row
                LOG.debug(msg)
                raise TypeError, msg
            # Add our column to the dictionary
            self.columns[column_name] = [col_seq, column_name, data_type]
            self.columns[column_name] += (data_length, data_precision)
            self.columns[column_name] += (data_scale, nullable)
            self.columns[column_name] += (row[4], row[5])
            # If this column is in the primary key add it to the list
            if row[3] == 'PRI':
                pk_columns.append(column_name)
        # Indexes, bit of mess this, needs rework
        stmt = """SHOW INDEX FROM %s""" % self.name
        cursor.execute(stmt)
        index_name = ""
        for index in cursor.fetchall():
            if index[2] != 'PRIMARY':
                if index_name != index[2]:
                    index_name = index[2]
                    # Add the index type and uniqueness
                    self.indexes[index_name] = [index[10]]
                    if index[1]:
                        self.indexes[index_name].append('NON-UNIQUE')
                    else:
                        self.indexes[index_name].append('UNIQUE')
                    # The columns are the last element in the index list, in 
                    # their own list
                    self.indexes[index_name].append([])
                self.indexes[index_name][2].append(index[4])
        # Constraints, MySQL doesn't really have these apart from a primary key
        if pk_columns:
            self.constraints['PRIMARY'] = ['Primary', 'Y', pk_columns]
        # Triggers, MySQL doesn't have these
        # Secret MySQL trick, as we are getting the details from a database, we 
        # can do this
        stmt = "SHOW CREATE TABLE %s" % self.name
        cursor.execute(stmt)
        self._sql = cursor.fetchone()[1]

    def get_ddl(self):
        """
        Generate the DDL necessary to create this table in a MySQL database
        
        @return: DDL to create this table
        @rtype: String
        """
        try:
            # If we have retrieved the DDL direct from the database
            ddl_strings = self._sql
        except AttributeError:
            # Create the SQL ourselves
            if not hasattr(self, 'name') or self.name == None:
                raise AttributeError, "Can't generate DDL for a table without a name"
            ddl_strings = ["CREATE TABLE "+self.name]
            in_columns = False
            cols = self.columns.values()
            cols.sort()
            for column in cols:
                if in_columns:
                    ddl_strings.append("\n  ,")
                else:
                    ddl_strings.append("\n ( ")
                    in_columns = True
                ddl_strings.append(column[1] + " ")
                ddl_strings.append(column[2] + '(')
                ddl_strings.append(str(int(column[3])) + ')')
                # Nullable?
                if column[5]:
                    ddl_strings.append(" " + column[5])
                # Default value
                if column[6]:
                    ddl_strings.append(" DEFAULT " + column[6])
                # Primary Key anyone?
                if 'PRIMARY' in self.constraints:
                    ddl_strings.append(" ,PRIMARY KEY")
                    pk_columns = ",".join(self.constraints['PRIMARY'][2])
                    ddl_strings.append("( %s )" % pk_columns)
                # Indexes
                for index in self.indexes:
                    ddl_strings.append(" ,KEY %s ( " % index)
                    ddl_strings.append("%s )" % self.indexes[index][2])
        return "".join(ddl_strings)


if __name__ == "__main__":
    print "This module should not be invoked from the command line"
    sys.exit(1)
