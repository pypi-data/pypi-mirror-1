"""Plugin for data stored in SQL servers.

This plugin should work with any database module that conforms with the
Python DB-API 2 specification:

    http://www.python.org/peps/pep-0249.html

You can find a list of database modules here:

    http://www.python.org/topics/database/modules.html

It currently has been tested with SQLite, MySQL and PostgreSQL.

TODO: add support for OFFSET and LIMIT if a slice is requested? This is
part of ANSI SQL, IIRC.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path
import urllib
import re
import itertools
import datetime
import sys
import csv
from ConfigParser import ConfigParser

from coards import to_udunits

import dap.lib
from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import ConstraintExpressionError
from dap.helper import parse_querystring
from dap.util.safeeval import expr_eval
from dap.plugins.csvfiles import lazy_eval

extensions = r"""^.*\.(sql|SQL)$"""

# These units are used when converting timestamps and intervals. They can
# be overrided for each variable in the .sql file.
DATETIME_DEFAULT_UNITS = "years since 1-1-1"
TIMEDELTA_DEFAULT_UNITS = "years"
MISSING_VALUE = -9999


def parse(value):
    """
    Parse values on the config file.

    This functions parses the values from the config file,
    handling lists, string, ints and floats properly.
    """
    # Split value on comma.
    value = csv.reader([value]).next()
    value = [lazy_eval(v.strip()) for v in value]
    if len(value) == 1: value = value[0]
    return value


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        """
        Handler constructor.
        """
        dir, self.filename = os.path.split(filepath)
        self.environ = environ

        # Read and store configuration.
        self.config = ConfigParser({'here': dir})
        self.config.read(filepath)

        # Read the DSN and make the connection.
        dsn = self.config.get('database', 'dsn')
        self.conn, self.type_convert = _get_conn(dsn)

        # Add description.
        if 'description' in self.config.options('metadata'):
            self.description = self.config.get('metadata', 'description')
        else:
            self.description = 'Connection to SQL database defined in file %s.' % self.filename

    def _parseconstraints(self, constraints=None):
        """Dataset builder.

        Build the dataset, selecting and filtering the data using a SQL
        query translated from the constraint expression.
        """
        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)

        # Add attributes to the dataset.
        for option in self.config.options('metadata'):
            if option != 'here': dataset.attributes[option] = parse(self.config.get('metadata', option))
        dataset.attributes['NC_GLOBAL'] = {}
        for option in self.config.options('NC_GLOBAL'):
            if option != 'here': dataset.attributes['NC_GLOBAL'][option] = parse(self.config.get('NC_GLOBAL', option))
        dataset.attributes['default datetime units'] = DATETIME_DEFAULT_UNITS
        dataset.attributes['default timedelta units'] = TIMEDELTA_DEFAULT_UNITS

        # Get sequence name and build it.
        if 'name' in self.config.options('metadata'):
            seqname = self.config.get('metadata', 'name')
            #seqname = seqname.lower().replace(' ', '_')
        else:
            seqname = self.filename[:-4].split('_', 1)[0]
        seq = dataset[seqname] = dtypes.SequenceType(name=seqname)

        # Collect all variables, their ids and corresponding column names.
        allvars = [var for var in self.config.sections() if var not in ['metadata', 'database', 'NC_GLOBAL']]
        allids  = ['%s.%s' % (seqname, var) for var in allvars]
        allcols = [self.config.get(var, 'col') for var in allvars]

        # Parse constraints.
        fields, queries = parse_querystring(constraints)

        # Get the SQL condition.
        if queries:
            # Build SQL condition from CE.
            condition = parse_queries(queries, allids, allcols)
            if condition: condition = "WHERE " + condition
        else:
            condition = ''

        # Get a list of requested variables.
        if not fields or seq.id in fields.keys():
            vars_ = allvars[:]
        else:
            # Strip seq name (casts.temp -> temp). Another ugly hack!
            prefix = seqname + '.'
            vars_ = [[var, var[len(prefix):]][var.startswith(prefix)] for var in fields.keys()]

            # Check that all vars are defined in the SQL file.
            vars_ = [var for var in vars_ if var in allvars]

        # Add variables to the Sequence object.
        for var in vars_:
            seq[var] = dtypes.BaseType(name=var, type=None)  # set type later

            # Add attributes.
            for option in self.config.options(var):
                if option not in ['col', 'type', 'id', 'here']:
                    seq[var].attributes[option] = parse(self.config.get(var, option))

        # The columns from which data will be retrieved.
        cols = [self.config.get(var, 'col') for var in vars_]

        # Check if this is empty.
        if not cols: return dataset

        # Build FROM. Here we build one or more JOINs if the data is in
        # more than a single table; in this case, the user must set the id
        # for the joining the tables.
        if 'join' in self.config.options('database'): join = self.config.get('database', 'join')
        else: join = 'INNER JOIN'
        tables = []
        from_ = []
        for col, var in zip(cols, vars_):
            if 'table' in self.config.options(var):
                table = self.config.get(var, 'table')
            else:
                table = col.split('.')[0]

            # Get the ID for JOINs or use the default of "id".
            if 'id' in self.config.options(var):
                id = self.config.get(var, 'id')
            else:
                id = 'id'

            if table not in tables:
                if not tables:  # initial table
                    from_.append("FROM %s" % table)
                else:  # an additinal table; make a join
                    from_.append("%s %s ON %s.%s = %s.%s" % (join, table, oldtable, oldid, table, id))
                tables.append(table)
                oldtable = table
                oldid = id
        from_ = ' '.join(from_)

        # Join cols for the queries...
        cols = ', '.join(cols)
        
        # Try to infer type. 
        query = "SELECT %s %s LIMIT 1;" % (cols, from_)
        curs = self.conn.cursor()
        if dap.lib.VERBOSE: self.environ['wsgi.errors'].write('%s\n' % query)
        curs.execute(query)
        types_ = [desc[1] for desc in curs.description]
        for var, type_ in zip(vars_, types_):
            if type_ is None or 'type' in self.config.options(var):
                basetype = self.config.get(var, 'type')
            else:
                basetype = self.type_convert(type_)
            seq[var].type = basetype
            seq[var].attributes.setdefault('missing_value', MISSING_VALUE)

        # Build query: SELECT cols FROM ... [WHERE ...]
        query = "SELECT %s %s %s;" % (cols, from_, condition)

        # Add data. We add it directly to the Sequence object, so we
        # only have to do a single query to the database.
        def data(query):
            curs = self.conn.cursor()
            if dap.lib.VERBOSE: self.environ['wsgi.errors'].write('%s\n' % query)
            curs.execute(query)
            for row in curs: yield row
        data_ = data(query)

        # Apply stride to sequence?
        slice_ = fields.get(seq.id)
        if slice_:
            slice_ = slice_[0]
            data_ = itertools.islice(data_, slice_.start or 0, slice_.stop or sys.maxint, slice_.step or 1)
        else:
            # Check stored variables. If more than one variable is selected,
            # and they have different slices, use the most restritive start,
            # step and stop.
            #
            # Behaviour rev-eng'ed from http://test.opendap.org/dap/data/ff/1998-6-avhrr.dat
            slices = []
            for var in seq.walk():
                slice_ = fields.get(var.id)
                if slice_: slices.append(slice_[0])
            if slices:
                start, step, stop = zip(*[(s.start or 0, s.step or 1, s.stop or sys.maxint) for s in slices])
                data_ = itertools.islice(data_, max(start), min(stop), max(step))

        # Insert data directly into sequence.
        seq._data = itertools.imap(filter1(seq.values()), data_)

        return dataset

    def close(self):
        """Close the DB connection."""
        self.conn.close()


def filter1(vars_):
    """
    Dynamic filter for converting special values into numbers.
    """
    def convert(cols):
        out = []
        for col, var in itertools.izip(cols, vars_):
            # Missing values.
            if col is None:
                missing_value = var.attributes.get('missing_value', MISSING_VALUE)                    
                col = missing_value

            # Datetime & timedelta.
            if isinstance(col, datetime.datetime):
                units = var.attributes.get('units', DATETIME_DEFAULT_UNITS)
                col = to_udunits(col, units)
            elif isinstance(col, datetime.timedelta):
                units = var.attributes.get('units', TIMEDELTA_DEFAULT_UNITS)
                col = to_udunits(col, units)

            out.append(col)
        return out
    return convert
        

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


def parse_queries(queries, vars_, cols=None):
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
    if cols is None: cols = vars_

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
        if not m: raise ConstraintExpressionError('Invalid constraint expression: %s.' % query)

        var1, op, var2 = m.groups()

        # Disallow regexps for now.
        if op == '=~': raise ConstraintExpressionError('Regular expressions disallowed!')

        # Evaluate variables. var1 must be a valid variable, and var2 must
        # be a constant.
        if var1 in vars_:
            col = cols[vars_.index(var1)]
            var2 = expr_eval(var2)

            subsubquery = []
            if isinstance(var2, tuple):
                for var in var2:
                    subsubquery.append('(%s %s %s)' % (col, op, repr(var)))
                subquery = ' OR '.join(subsubquery)
            else:
                subquery = '%s %s %s' % (col, op, repr(var2))
            subquery = '(%s)' % subquery
            out.append(subquery)

    out = ' AND '.join(out)
    return out


def _get_conn(dsn):
    """
    Build the connection.
    """
    protocol, location = dsn.split('://', 2)

    # Return a connection according to the protocol.
    conns = {'sqlite'     : _conn_sqlite,
             'pgsql'      : _conn_pgsql,
             'psql'       : _conn_pgsql,
             'postgres'   : _conn_pgsql,
             'postgresql' : _conn_pgsql,
             'mysql'      : _conn_mysql,
             'oracle'     : _conn_oracle,
             'mssql'      : _conn_mssql,
             'odbc'       : _conn_odbc,
            }
    return conns[protocol](location)
    

def _conn_sqlite(location):
    """SQLite connection."""
    from pysqlite2 import dbapi2 as sqlite

    conn = sqlite.connect(location)
    type_convert = None
    return conn, type_convert


def _conn_odbc(conn_str):
    try:
        from ceODBC import connect, STRING, DATETIME, NUMBER
    except ImportError:
        from pyodbc import connect, STRING, DATETIME, NUMBER

    # Convert between cursor.description[1] types and DAP types.
    def type_convert(type_):
        if type_ in STRING: return 'String'
        elif type_ in DATETIME: return 'Float64'
        elif type_ in NUMBER: return 'Float64'  # assume Float64 for numbers, user can override

    conn = connect(conn_str)
    return conn, type_convert


def _conn_pgsql(location):
    """PostgreSQL connection."""
    from psycopg2 import connect, STRING, DATETIME, NUMBER

    # Convert between cursor.description[1] types and DAP types.
    def type_convert(type_):
        if type_ in STRING: return 'String'
        elif type_ in DATETIME: return 'Float64'
        elif type_ in NUMBER: return 'Float64'  # assume Float64 for numbers, user can override

    user, passwd, host, port, dbname = split_dsn(location)
    conn_str = [('dbname', dbname)]
    if host: conn_str.append(('host', host))
    if port: conn_str.append(('port', str(port)))
    if user: conn_str.append(('user', user))
    if passwd: conn_str.append(('password', passwd))
    conn_str = ['='.join(t) for t in conn_str]
    conn_str = ' '.join(conn_str)

    conn = connect(conn_str)
    return conn, type_convert


def _conn_mysql(location):
    """MySQL connection."""
    from MySQLdb import connect, STRING, DATETIME, NUMBER

    # Convert between cursor.description[1] types and DAP types.
    def type_convert(type_):
        if type_ in STRING: return 'String'
        elif type_ in DATETIME: return 'Float64'
        elif type_ in NUMBER: return 'Float64'  # assume Float64 for numbers, user can override

    user, passwd, host, port, db = split_dsn(location)
    kwargs = {'db': db}
    if host: kwargs['host'] = host
    if port: kwargs['port'] = port
    if user: kwargs['user'] = user
    if passwd: kwargs['passwd'] = passwd

    conn = connect(**kwargs)
    return conn, type_convert


def _conn_oracle(location):
    """Oracle connection."""
    from cx_Oracle import connect, STRING, DATETIME, NUMBER, makedsn
    
    # Convert between cursor.description[1] types and DAP types.
    def type_convert(type_):
        if type_ in STRING: return 'String'
        elif type_ in DATETIME: return 'Float64'
        elif type_ in NUMBER: return 'Float64'  # assume Float64 for numbers, user can override

    user, passwd, host, port, db = split_dsn(location)
    kwargs = {'dsn': makedsn(host, port, db)}
    if user: kwargs['user'] = user
    if passwd: kwargs['password'] = passwd

    conn = connect(**kwargs)
    return conn, type_convert


def _conn_mssql(location):
    """MS SQL connection."""
    from adodbapi import connect, STRING, DATETIME, NUMBER

    # Convert between cursor.description[1] types and DAP types.
    def type_convert(type_):
        if type_ in STRING: return 'String'
        elif type_ in DATETIME: return 'Float64'
        elif type_ in NUMBER: return 'Float64'  # assume Float64 for numbers, user can override

    user, passwd, host, port, db = split_dsn(location)
    conn_str = [('Driver', '{SQL Server}'),
                ('Database', db)]
    if host: conn_str.append(('Server', host))
    if port: conn_str.append(('Port', str(port)))
    if user: conn_str.append(('Uid', user))
    if passwd: conn_str.append(('Pwd', passwd))
    conn_str = ['='.join(t) for t in conn_str]
    conn_str = ';'.join(conn_str)

    conn = connect(conn_str)
    return conn, type_convert


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()
