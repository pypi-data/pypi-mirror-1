"""Plugin for data stored in SQL servers.

This plugin should work with any database module that conforms with the
Python DB-API 2 specification:

    http://www.python.org/peps/pep-0249.html

You can find a list of database modules here:

    http://www.python.org/topics/database/modules.html
"""

# TODO: add typeconversion and handle datetime objects.

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path
import ConfigParser
import urllib
import re

from dap import dtypes
from dap.server import BaseHandler
from dap.util.safeeval import expr_eval
from dap.exceptions import ConstraintExpressionError

extensions = r"""^.*\.(sql|SQL)$"""


def split_dsn(location):
    """Split DSN into user, password, host, port and dbname.
    
        >>> print split_dsn('user:pass@host:80/db')
        ('user', 'pass', 'host', '80', 'db')
        >>> print split_dsn('host/db')
        (None, None, 'host', None, 'db')
        >>> print split_dsn('user@host/db')
        ('user', None, 'host', None, 'db')
        >>> print split_dsn('user:pass@host/db')
        ('user', 'pass', 'host', None, 'db')
    """
    user, host = urllib.splituser(location)
    if user:
        user, password = urllib.splitpasswd(user)
    else:
        password = None

    host, dbname = urllib.splithost('//' + host)
    if dbname.startswith('/'): dbname = dbname[1:]
    host, port = urllib.splitport(host)

    return user, password, host, port, dbname


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        dir, self.filename = os.path.split(filepath)
        self.environ = environ

        # Read and store configuration.
        self.config = ConfigParser.ConfigParser()
        self.config.read(filepath)

        dsn = self.config.get('database', 'dsn')
        self.conn = self._get_conn(dsn)

    def _get_conn(self, dsn):
        self.protocol, location = dsn.split('://', 2)

        conns = {'sqlite': self._conn_sqlite,
                 'pgsql' : self._conn_pgsql,
                }
        return conns[self.protocol](location)

    def _conn_sqlite(self, location):
        from pysqlite2 import dbapi2 as sqlite

        conn = sqlite.connect(location)
        return conn

    def _conn_pgsql(self, location):
        raise Exception, "Not fully implemented."
        from psycopg import connect, INTEGER, STRING, FLOAT, LONG, DATETIME

        # Convert between cursor.description[1] types and DAP types.
        self.typeconvert = {INTEGER: 'Int32',
                            LONG   : 'Float64',
                            FLOAT  : 'Float32',
                            STRING : 'String',
                           }

        user, password, host, port, dname = split_dsn(location)

        conn_str = ["dbname=%s" % dbname]
        for name in ['host', 'port', 'user', 'password']:
            var = locals()[name]
            if var is not None:
                conn_str.append("%s=%s" % (name, var))
        conn_str = ' '.join(conn_str)

        conn = connect(conn_str)
        return conn

    def _parseconstraints(self, constraints=None):
        # Build the dataset and the main sequence.
        dataset = dtypes.DatasetType(name=self.filename)

        # Add attributes.
        for option in self.config.options('database'):
            if option not in ['dsn']:
                dataset.attributes[option] = self.config.get('database', option)

        # Get sequence name and build it.
        if 'name' in self.config.options('database'):
            seqname = self.config.get('database', 'name')
        else:
            seqname = os.path.splitext(self.filename)[0]
        seq = dataset[seqname] = dtypes.SequenceType(name=seqname)

        # Collect all variables, their ids and corresponding row names.
        allvars = [var for var in self.config.sections() if var != 'database']
        allids  = ['%s.%s' % (seqname, var) for var in allvars]
        allrows = [self.config.get(var, 'row') for var in allvars]

        if constraints:
            constraints = urllib.unquote(constraints)
            constraints = constraints.split('&')

            # Selection expression.
            queries = constraints[1:]

            # Build condition.
            condition = parse_queries(queries, allids, allrows)
            if condition: condition = "WHERE " + condition

            # Requested vars.
            vars_ = constraints[0]
            vars_ = vars_.split(',')
            
            # Strip seq name (casts.temp -> temp). Another ugly hack!
            prefix = seqname + '.'
            vars_ = [[var, var[len(prefix):]][var.startswith(prefix)] for var in vars_]

            # Check that all vars are defined in the SQL file.
            vars_ = [var for var in vars_ if var in allvars]
        else:
            condition = ''  # select everything
            vars_ = allvars[:]

        for var in vars_:
            seq[var] = dtypes.BaseType(name=var, type=None)  # set type later

            # Add attributes.
            for option in self.config.options(var):
                if option not in ['row', 'type', 'id']:
                    seq[var].attributes[option] = self.config.get(var, option)

        rows = [self.config.get(var, 'row') for var in vars_]

        # Build FROM. Here we build one or more JOINs if the data is in
        # more than a single table; in this case, the user must set the id
        # for the joining the tables.
        tables = []
        from_ = []
        for row, var in zip(rows, vars_):
            if 'table' in self.config.options(var):
                table = self.config.get(var, 'table')
            else:
                table = row.split('.')[0]

            # Get the ID for JOINs or use the default of "id".
            if 'id' in self.config.options(var):
                id = self.config.get(var, 'id')
            else:
                id = 'id'

            if table not in tables:
                if not tables:  # initial table
                    from_.append("FROM %s" % table)
                else:
                    from_.append("JOIN %s ON %s.%s = %s.%s" % (table, oldtable, oldid, table, id))
                tables.append(table)
                oldtable = table
                oldid = id
        from_ = ' '.join(from_)

        # Join rows for the queries...
        rows = ', '.join(rows)
        
        # Try to infer type. We read a single line of data (TODO: do we?).
        query = "SELECT %s %s LIMIT 1;" % (rows, from_)
        curs = self.conn.cursor()
        self.environ['logger'].debug('Trying to execute: %s' % query)
        curs.execute(query)
        self.environ['logger'].debug('Ok!')
        types_ = [desc[1] for desc in curs.description]
        for var, type_ in zip(vars_, types_):
            if type_ is None or 'type' in self.config.options(var):
                type_ = self.config.get(var, 'type')
            else:
                type_ = self.typeconvert[type_]
            seq[var].type = type_

        query = "SELECT %s %s %s;" % (rows, from_, condition)
        
        # Add data. We add it directly to the Sequence object, so we
        # only have to do a single query to the database.
        def data():
            curs = self.conn.cursor()
            self.environ['logger'].debug('Trying to execute: %s' % query)
            curs.execute(query)
            self.environ['logger'].debug('Ok!')
            for row in curs: yield row
        seq.data = data()

        return dataset

    def close(self):
        self.conn.close()


def parse_queries(queries, vars_, rows=None):
    """Build SQL query from DAP queries.

        >>> vars_ = ['index',  'site']
        >>> parse_queries(['index>=11'], vars_)
        '(index >= 11)'
        >>> parse_queries(['site=~".*_St"'], vars_)
        Traceback (most recent call last):
        ...
        ConstraintExpressionError: 'Regular expressions disallowed!'
        >>> parse_queries(['site=~".*_St"', 'index>=11'], vars_)
        Traceback (most recent call last):
        ...
        ConstraintExpressionError: 'Regular expressions disallowed!'
        >>> parse_queries(['site={"Diamond_St", "Blacktail_Loop"}'], vars_)
        "((site = 'Diamond_St') OR (site = 'Blacktail_Loop'))"
        >>> parse_queries(['index={10, 12}'], vars_)
        '((index = 10) OR (index = 12))'
    """
    if rows is None: rows = vars_

    out = []
    p = re.compile(r'''^                          # Start of selection
                       (?P<var1>.*?)              # Anything
                       (?P<op><=|>=|!=|=~|>|<|=)  # Operators
                       {?                         # {
                       (?P<var2>.*?)              # Anything
                       }?                         # }
                       $                          # EOL
                    ''', re.VERBOSE)
    for query in queries:
        m = p.match(query)
        if not m: raise ConstraintExpressionError, 'Invalid constraint expression: %s.' % query

        var1, op, var2 = m.groups()

        # Disallow regexps for now.
        if op == '=~': raise ConstraintExpressionError, 'Regular expressions disallowed!'

        # Evaluate variables. var1 must be a valid variable, and var2 must
        # be a constant.
        if not var1 in vars_:
            raise ConstraintExpressionError, 'Invalid constraint expression: %s.' % query
        row = rows[vars_.index(var1)]
        try:
            var2 = expr_eval(var2)
        except:
            raise ConstraintExpressionError, 'Invalid constraint expression: %s.' % query

        subsubquery = []
        if isinstance(var2, tuple):
            for var in var2:
                subsubquery.append('(%s %s %s)' % (row, op, repr(var)))
            subquery = ' OR '.join(subsubquery)
        else:
            subquery = '%s %s %s' % (row, op, repr(var2))
        subquery = '(%s)' % subquery
        out.append(subquery)

    out = ' AND '.join(out)
    return out


def create_data():
    """Create some sample data.

    This function creates bogus data for the SQL plugin. To access the data
    create a file called 'something.sql' with the following content:
    
        [database]
        # DSN should be module://user:pass@host:port/dbname
        dsn: sqlite:///path/to/test.db
        history: Bogus data for testing purposes.
        author: Your name goes here
        name: Cast
        arbitrary-attribute: 42

        [temp_a]
        # Table and row where the variable is located.
        row: casts0.temperature
        # Specify type if using SQLite or if you want to override the DB.
        type: Float32
        # Id is used for the SQL JOIN, when data is in different columns.
        id: id0
        # Add any arbitrary attributes here.
        units: deg C

        [temp_b]
        row: casts1.temperature
        type: Float32
        units: deg C
        id: id1

        [temp_c]
        row: casts2.temperature
        type: Float32
        units: deg C
        id: id2

        [saln_a]
        row: casts0.salinity
        type: Float32
        units: psu
        id: id0

        [saln_b]
        row: casts1.salinity
        type: Float32
        units: psu
        id: id1

        [saln_c]
        row: casts2.salinity
        type: Float32
        units: psu
        id: id2
    """
    sqls = [
            "create table casts0 (temperature float32, salinity float32, id0 int32);",
            "insert into casts0 (temperature, salinity, id0) values (24.1, 35.2, 0);",
            "insert into casts0 (temperature, salinity, id0) values (24.2, 35.1, 1);",
            "insert into casts0 (temperature, salinity, id0) values (24.3, 35.0, 2);",
            "insert into casts0 (temperature, salinity, id0) values (24.4, 34.9, 3);",
            "create table casts1 (temperature float32, salinity float32, id1 int32);",
            "insert into casts1 (temperature, salinity, id1) values (24.5, 34.8, 1);",
            "insert into casts1 (temperature, salinity, id1) values (24.6, 34.7, 2);",
            "insert into casts1 (temperature, salinity, id1) values (24.7, 34.6, 3);",
            "insert into casts1 (temperature, salinity, id1) values (24.8, 24.5, 4);",
            "create table casts2 (temperature float32, salinity float32, id2 int32);",
            "insert into casts2 (temperature, salinity, id2) values (24.9, 34.4, 2);",
            "insert into casts2 (temperature, salinity, id2) values (25.0, 34.3, 3);",
            "insert into casts2 (temperature, salinity, id2) values (25.1, 34.2, 4);",
            "insert into casts2 (temperature, salinity, id2) values (25.2, 34.1, 5);",
           ]

    from pysqlite2 import dbapi2 as sqlite

    con = sqlite.connect("test.db")
    cur = con.cursor()
    for sql in sqls:
        cur.execute(sql)
    con.commit()


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()
