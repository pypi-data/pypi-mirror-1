#!/usr/bin/env python
#
# pgsql.py version 0.9.2
#
# Updated by Cristian Gafton to use the bind parameters
# and adapt to the new interface provided by the C bindings
#
# Originally written by D'Arcy J.M. Cain
#

"""pgsql - DB-API 2.0 compliant module for PostgreSQL.

(c) 2006 Cristian Gafton <gafton@rpath.com>
Reworked the C and Python modules based on PyGreSQL sources

(c) 1999, Pascal Andre <andre@via.ecp.fr>.
See COPYRIGHT file for further information on copyright.

Inline documentation is sparse.
See DB-API 2.0 specification for usage information:
http://www.python.org/peps/pep-0249.html

See the README file for an overview of this module's contents.
"""

import os
import types
import time

import _pgsql

# exceptions
from _pgsql import InterfaceError, DatabaseError, InternalError, \
     OperationalError, ProgrammingError, IntegrityError, DataError, \
     NotSupportedError
# constants we might use
from _pgsql import INV_READ, INV_WRITE, SEEK_CUR, SEEK_END, SEEK_SET, \
     RESULT_DDL, RESULT_DML, RESULT_DQL, RESULT_EMPTY, \
     TRANS_ACTIVE, TRANS_IDLE, TRANS_INERROR, TRANS_INTRANS, TRANS_UNKNOWN

try: # use mx.DateTime module if available
    from mx.DateTime import DateTime, \
         TimeDelta, DateTimeType
except ImportError: # otherwise use standard datetime module
    from datetime import datetime as DateTime, \
         timedelta as TimeDelta, datetime as DateTimeType

### module constants
version = "0.9.2"

# compliant with DB SIG 2.0
apilevel = '2.0'

# module may be shared, but not connections
threadsafety = 1

# this module use extended python format codes
paramstyle = 'numeric'

# default values for connection parameters
def_host   = None #default database host
def_base   = None #default database name
def_opt    = None #default connection options
def_tty    = None #default debug tty
def_port   = -1   #default connection port
def_user   = None #default username
def_passwd = None #default password


# convert to Python types the values that were not automatically
# converted by pgsql.c
def typecast(typ, value):
    if typ == DATETIME:
        # FIXME... we should prolly do something here to transalate
        # datetime strings, when we need it
        pass
    return value

### cursor object
class Cursor(object):
    def __init__(self, src):
        self._source = src

    def close(self):
        self._source.close()

    def arraysize(self, size):
        self.arraysize = size

    # if parameters are passed in, we'll attempt to bind them
    def execute(self, operation, *params):
        if not len(params):
            ret = self._source.execute(operation)
        elif isinstance(params[0], (list, tuple)):
            ret = self._source.execute(operation, params[0])
        else:
            ret = self._source.execute(operation, params)
        if isinstance(ret, int):
            return ret
        return self

    def executemany(self, operation, param_seq):
        ret = self._source.executemany(operation, param_seq)
        return self

    def fetchone(self):
        return self._source.fetchone()

    def fetchall(self):
        return self._source.fetchall()

    def fetchmany(self, size = None):
        if size == None:
            size = self.arraysize
        return [self._source.fetchone() for x in range(size)]

    def nextset(self):
        raise NotSupportedError, "nextset() is not supported"

    def setinputsizes(self, sizes):
        pass

    def setoutputsize(self, size, col = 0):
        pass

    # iterator support
    def __iter__(self):
        return self
    def next(self):
        item = self.fetchone()
        if item is None:
            raise StopIteration
        else:
            return item
    # access to other attributes
    def __getattr__(self, name):
        if name in set(["fields", "description", "rowcount", "notices",
                        "arraysize", "resulttype", "rownumber",
                        "oidstatus", "valid"]):
            return getattr(self._source, name)
        elif name in set(["escape_string", "escape_bytea", "unescape_bytea"]):
            return getattr(self._source.connection, name)
        elif self.__dict__.has_key(name):
            return self.__dict__[name]
        raise AttributeError, name

    def __setattr__(self, name, val):
        if name == "arraysize":
            setattr(self._source, name, val)
        else:
            object.__setattr__(self, name, val)

# A cursor class for prepared statements
class PreparedCursor(Cursor):
    # we require parameters since we've already bound a query
    def execute(self, *params):
        if not len(params):
            ret = self._source.execute(None)
        elif isinstance(params[0], (tuple, list)):
            ret = self._source.execute(params[0])
        else:
            ret = self._source.execute(params)
        if isinstance(ret, int):
            return ret
        return self
    def executemany(self, param_seq):
        ret = self._source.executemany(param_seq)
        return self

# A cursor for large SELECTs that uses server side cursors
class IterCursor(Cursor):
    def __init__(self, source):
        Cursor.__init__(self, source)
        self.active = 0
        # we need a fairly random name for our cursor executions
        self.name = "p%did%s" % (os.getpid(), hex(abs(id(source))))

    def execute(self, query, *params):
        query = query.strip()
        if not query.upper().startswith("SELECT"):
            return Cursor.execute(self, query, *params)
        # we have a select query, open up the cursor
        if self.active:
            self._source.execute("CLOSE %s" % self.name)
            self.active = 0
        # open up this cursor for select
        query = "DECLARE %s NO SCROLL CURSOR WITH HOLD FOR\n%s" %(
            self.name, query)
        if not len(params):
            ret = self._source.execute(query)
        elif isinstance(params[0], (tuple, list)):
            ret = self._source.execute(query, params[0])
        else:
            ret = self._source.execute(query, params)
        self.active = 1
        return ret

    def fetchone(self):
        # if this is not an active cursor, passthrough
        if self.active:
            self._source.query("FETCH NEXT FROM %s" % self.name)
        return Cursor.fetchone(self)

    def fetchall(self):
        if self.active:
            self._source.execute("FETCH ALL FROM %s" % self.name)
        return Cursor.fetchall(self)

    def fetchmany(self, size = None):
        if size is None:
            size = self.arraysize
        if not self.active:
            return Cursor.fetchmany(self, size)
        self._source.execute("FETCH %d FROM %s" % (size, self.name))
        return Cursor.fetchall(self)

    def close(self):
        if self.active and self._source.valid:
            self._source.execute("CLOSE %s" % self.name)
            self.active = 0
    # be nice to the server side and let it free resources...
    def __del__(self):
        self.close()
        self._source.close()
        del self

### connection object
class Database(object):
    def __init__(self, cnx):
        self.__cnx = cnx
        cnx.execute("START TRANSACTION")
        # for prepared statement cache
        self.__cache = {}

    def close(self):
        # deallocate statements
        self.rollback()
        for src, name in self.__cache.itervalues():
            if not src.valid:
                continue
            try:
                self.__cnx.execute("DEALLOCATE %s" % (name,))
            except pgsql.ProgrammingError:
                self.rollback()
            src.close()
        self.__cache = {}
        self.__cnx.close()

    # Postgresql autocommits everything not inside a transaction
    # block, so to simulate autocommit=off, we have to start new
    # transactions as soon as we flush them
    def commit(self):
        self.__cnx.execute("COMMIT")
        self.__cnx.execute("START TRANSACTION")

    def rollback(self):
        self.__cnx.execute("ROLLBACK")
        self.__cnx.execute("START TRANSACTION")

    def execute(self, query, *params):
        if not len(params):
            ret = self.__cnx.execute(query)
        elif isinstance(params[0], (tuple, list)):
            ret = self.__cnx.execute(query, params[0])
        else:
            ret = self.__cnx.execute(query, params)
        if isinstance(ret, int):
            return ret
        return Cursor(ret)

    def cursor(self):
        src = self.__cnx.source()
        return Cursor(src)

    def itercursor(self):
        src = self.__cnx.source()
        return IterCursor(src)

    def prepare(self, sql):
        sql = sql.strip()
        (src, name) = self.__cache.get(sql, (None, None))
        if src is None:
            name = "prep%d" % (len(self.__cache),)
            src = self.__cnx.prepare(sql, name)
            self.__cache[sql] = (src, name)
        return PreparedCursor(src)

    def __getattr__(self, name):
        if name in set([
            "dbname", "host", "port", "opt", "tty", "notices", "status",
            "escape_string", "escape_bytea", "unescape_bytea", "transaction",
            "locreate", "loimport", "getlo", "setnotices"]):
            return getattr(self.__cnx, name)
        elif self.__dict__.has_key(name):
            return self.__dict__[name]
        raise AttributeError, name

### module interface

# connects to a database
def connect(database = def_base, user = def_user, password = def_passwd,
            host = def_host, port = def_port, opt = def_opt, tty = def_tty):
    # open the connection
    cnx = _pgsql.connect(database, user, password, host, port, opt, tty)
    return Database(cnx)

### types handling

# PostgreSQL is object-oriented: types are dynamic.
# We must thus use type names as internal type codes.
class pgType:
    def __init__(self, *values):
        self.values = values

    def __cmp__(self, other):
        if other in self.values:
            return 0
        if other < self.values:
            return 1
        else:
            return -1

STRING = pgType("string")
BINARY = pgType("binary")
INTEGER = pgType("integer")
LONG = pgType("long")
FLOAT = pgType("double")
NUMBER = pgType("integer", "long", "double", "oid")
BOOL = pgType("bool")
MONEY = pgType('money')

# this may be problematic as type are quite different ... I hope it won't hurt
DATETIME = pgType("datetime")

# OIDs are used for everything (types, tables, BLOBs, rows, ...). This may cause
# confusion, but we are unable to find out what exactly is behind the OID (at
# least not easily enough). Should this be undefined as BLOBs ?
ROWID = pgType("oid")

# mandatory type helpers
def Date(year, month, day):
    return DateTime(year, month, day)

def Time(hour, minute, second):
    return TimeDelta(hour, minute, second)

def Timestamp(year, month, day, hour, minute, second):
    return DateTime(year, month, day, hour, minute, second)

def DateFromTicks(ticks):
    return apply(Date, time.localtime(ticks)[:3])

def TimeFromTicks(ticks):
    return apply(Time, time.localtime(ticks)[3:6])

def TimestampFromTicks(ticks):
    return apply(Timestamp, time.localtime(ticks)[:6])

def Binary(str):
    return str

# if run as script, print some information
if __name__ == '__main__':
    print 'pgsql version', version
    print
    print __doc__
