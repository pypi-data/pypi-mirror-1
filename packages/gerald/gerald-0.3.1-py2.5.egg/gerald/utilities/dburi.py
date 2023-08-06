"""
This module provides a series of utility classes and functions to return a 
database connection from a URI.

These URIs are of the form;

 - 'mysql://username[:password]@host[:port]/database name'
 - 'sqlite://path/to/db/file'
 - 'sqlite:/C|/path/to/db/file' - On MS Windows
 - 'sqlite:/:memory:' - For an in memory database
 - 'oracle://username:password@tns entry'
 - 'postgres://username[:password]@host[:port]/database name'

This module is inspired by (and somewhat borrows from) SQLObject's dbconnection.py, I've just purposely not included a lot of the baggage from that particular module.

This module is licensed under the BSD License (see LICENSE.txt)

To do;
 - Add ODBC support via pyodbc - http://pyodbc.sourceforge.net/
"""
__version__ = (0, 2, 1)
__date__ = (2008, 7, 24)
__author__ = "Andy Todd <andy47@halfcooked.com>"

# Use a relative import because Log should be in the same directory
from .Log import get_log
log = get_log(level='INFO')

class Connection(object):
    def parse_uri(self, connection_string):
        "Turn the connection_string into a series of parameters to the connect method"
        # Strip the leading '/'
        if connection_string.startswith('/'):
            connection_string = connection_string[1:]
        if connection_string.find('@') != -1:
            # Split into the username (and password) and the rest
            username, rest = connection_string.split('@')
            if username.find(':') != -1:
                username, password = username.split(':')
            else:
                password = None
            # Take the rest and split into its host, port and db name parts
            if rest.find('/') != -1:
                host, dbName = rest.split('/')
            else:
                host = rest
                dbName = ''
            if host.find(':') != -1:
                host, port = host.split(':')
                try:
                    port = int(port)
                except ValueError:
                    raise ValueError, "port must be integer, got '%s' instead" % port
                if not (1 <= port <= 65535):
                    raise ValueError, "port must be integer in the range 1-65535, got '%d' instead" % port
            else:
                port = None
        else:
            raise ValueError, "Connection passed invalid connection_string"
        return username, password, host, port, dbName

class MySqlConnection(Connection):
    def __init__(self, connection_string):
        try:
            import MySQLdb as db
        except ImportError:
            raise ImportError, "Can't connect to MySQL as db-api module not present"

        username, password, host, port, dbName = self.parse_uri(connection_string)
        self.connection = db.connect(user=username or '', passwd=password or '', host=host or 'localhost', port=port or 0, db=dbName or '')

class SqliteConnection(Connection):
    def __init__(self, connection_string):
        if not connection_string:
            raise ValueError, "Cannot connect to sqlite. You must provide a connection string"
        try:
            from sqlite3 import dbapi2 as db # For Python 2.5 and above
        except ImportError:
            try:
                from pysqlite2 import dbapi2 as db
            except ImportError:
                raise ImportError, "Can't connect to sqlite as db-api module not present"
        # If the path has a | character we replace it with a :
        if connection_string.find('|') != -1:
            connection_string.replace('|', ':')
        log.debug(connection_string)
        self.connection = db.connect(connection_string)

class OracleConnection(Connection):
    """Establish a connection to the Oracle database identified by connection_string

    The acceptable form of the connection string is;::

        oracle://username:password@tns_entry

    The db modules we try (in order of preference) are cx_Oracle and dcoracle2
    """
    def __init__(self, connection_string):
        try:
            import cx_Oracle as db
        except ImportError:
            import dcoracle2 as db
        # Remove the leading / from the connection string 
        if connection_string.startswith('/'):
            connection_string = connection_string[1:]
        # replace the : between the username and password with a /
        if connection_string.find(':') != -1:
            connection_string = connection_string.replace(':', '/')
        # Connect to the database
        log.debug('Trying to establish connection to Oracle using %s' % connection_string)
        self.connection = db.connect(connection_string)

class PostgresConnection(Connection):
    def __init__(self, connection_string):
        """Establish a connection to the PostgreSQL database identified by connection_string

        The acceptable form of the connection string is;::

          'postgres://username[:password]@host[:port]/database name'

        The db modules we try (in order of preference) are psycopg2, pygresql and
        pyPgSQL

        I may add the db module as an optional parameter in a future release
        """
        try:
            import psycopg2 as db
            module = 'psycopg2'
        except ImportError:
            try:
                import pgdb as db
                module = 'pygresql'
            except ImportError:
                from pyPgSQL import PgSQL as db
                module = 'pypgsql'
        # Extract pertinent details from the connection_string
        connection = {}
        connection['username'], connection['password'], connection['host'], connection['port'], connection['dbname'] = self.parse_uri(connection_string)
        # Use these to create our actual DSN taking into account optionality
        if module == 'psycopg2':
            dsn = "user='%s'" % connection['username']
            if connection.has_key('password') and connection['password'] != None:
                dsn += " password='%s'" % connection['password']
            dsn += " host='%s'" % connection['host']
            if connection.has_key('dbname') and connection['dbname'] != '':
                dsn += " dbname='%s'" % connection['dbname']
            if connection.has_key('port') and connection['port'] != None:
                dsn += " port=%d" % connection['port']
            log.debug('Trying to establish connection to Postgres using %s' % dsn)
            self.connection = db.connect(dsn)
        elif module=='pygresql' or module=='pypgsql':
            if connection.has_key('port') and connection['port'] != None:
                host = connection['host'] + ':' + connection['port']
            else:
                host = connection['host']
            if connection.has_key('password') and connection['password'] != None:
                self.connection = db.connect(host=host, user=connection['username'], database=connection['dbname'], password=connection['password'])
            else:
                self.connection = db.connect(host=host, user=connection['username'], database=connection['dbname'])
        else:
            # Not implemented yet
            raise NotImplementedError

def get_connection(uri):
    """Get and return a database connection based on the uri
    
    The uri scheme is blatantly ripped off from SQLObject_. The general form 
    of these uris is;
     - 'plugin://user:password@host/database name'

    e.g.
     - 'mysql://username[:password]@host[:port]/database name'
     - 'sqlite:/path/to/db/file'
     - 'oracle://username:password@tns entry'
     - 'postgres://username[:password]@host[:post]/database name'

    .. _SQLObject: http://www.sqlobject.org/sqlapi/module-sqlapi.uri.html
    """
    helpers = { 'mysql': MySqlConnection,
                'sqlite': SqliteConnection,
                'oracle': OracleConnection,
                'postgres': PostgresConnection }
    scheme, connection_string = uri.split(':/')
    connection = helpers[scheme](connection_string)
    return connection.connection
