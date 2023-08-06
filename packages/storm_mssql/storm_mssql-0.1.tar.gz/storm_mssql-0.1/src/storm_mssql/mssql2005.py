#
# Copyright (c) 2006, 2007 Canonical
#
# Contribution by ZeOmega.com (contact Brad Allen <ballen@zeomega.com>)
#
# This file is part of Storm Object Relational Mapper.
#
# Storm is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# Storm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Storm backend for Microsoft SQL Server versions 2005 and later.
Earlier versions of SQL Server have a different way of introspecting
column attributes, which this module does not support.

Module Configuration Options:

    To select different backend connectors such as mxODBC,
    mxODBC Connect, pyodbc, pymssql, adodbapi, etc., 
    use mssql_connector.initialize_connector before you
    import this module.
    
    To enable WITH(NOLOCK) on all SELECT statements, call
    the module level function: set_global_nolock(enable=True) 
    
    To enable automatic generation of SET IDENTITY INSERT
    statements, set the module level attribute as follows:
    ENABLE_IDENTITY_INSERT = True. This uses db introspection
    to determine if a column is an identity column
    for each and every insert before trying to insert 
    a value to that column. WARNING -- this is very slowww!
    In practice it is not useful, but is present to allow
    passing Storm unit tests. If you need to use
    IDENTITY INSERT in practice you should try BULK INSERT.
"""

from platform import platform
from datetime import datetime, date, time, timedelta
from array import array
import sys
import pdb

from storm.databases import dummy
from storm.tracer import trace
from storm.expr import (
    And, build_tables, COLUMN, COLUMN_NAME, Eq, EXPR, Expr, Insert, 
    SQLRaw, SQLToken, Select, TABLE, Undef, compile, compile_select,
    is_safe_token, has_tables, NamedFunc, Context, JoinExpr
    )
from storm.variables import Variable
from storm.info import get_cls_info, ClassAlias
from storm.database import Database, Connection, Result
from storm.exceptions import (DatabaseModuleError, 
                              OperationalError,
                              ProgrammingError)

try:
    from mssql_connector import MsSQLdbapi
except ImportError, e:
    # Since it was not initialized, run default initialization
    import mssql_connector
    mssql_connector.initialize_connector()
    from mssql_connector import MsSQLdbapi


# --------- Configuration for global WITH(NOLOCK) setting ---------------------

 #Storm context object needed for calling a  for a table called WITH(NOLOCK)
TABLE_WITH_NOLOCK = Context("TABLE")

def set_global_nolock (enable=False):
    """
    SQL Server has a WITH(NOLOCK) syntax to enable dirty reads;
    this helps with performance in some highly concurrent apps
    where risking data integrity is an issue.
    
    Example: SELECT * FROM foo WITH(NOLOCK) join bar WITH(NOLOCK)
                 ON foo.foo_id = bar.foo_id
    """
    global g_table_context
    if enable:
        g_table_context = TABLE_WITH_NOLOCK
    else:
        g_table_context = TABLE

# most apps will want this turned off
set_global_nolock(enable=False)

# ------- Configuration for enabling the IDENTITY_INSERT (see module docstring)

ENABLE_IDENTITY_INSERT = False # needed to pass unit tests,
                              # but best to disable when not needed because
                              # it may degrade insert performance

# ---------- Escape T-SQL Reserved Words --------------------------------------
# This is the set of T-SQL reserved words used by SQL Server.
# Having to check against this large set for every compile may slow
# performance so this should be profiled.
RESERVED_WORDS = (
    'ADD','EXIT','PRIMARY','ALL','FETCH','PRINT','ALTER','FILE',
    'PRIVILEGES','AND','FILLFACTOR','PROC','ANY','FLOPPY','PROCEDURE','AS',
    'FOR','PROCESSEXIT','ASC','FOREIGN','PUBLIC','AUTHORIZATION','FREETEXT'
    'RAISERROR','AVG','FREETEXTTABLE','READ','BACKUP','FROM','READTEXT',
    'BEGIN','FULL','RECONFIGURE','BETWEEN','GOTO','REFERENCES','BREAK',
    'GRANT','REPEATABLE','BROWSE','GROUP','REPLICATION','BULK','HAVING',
    'RESTORE','BY','HOLDLOCK','RESTRICT','CASCADE','IDENTITY','RETURN',
    'CASE','IDENTITY_INSERT','REVOKE','CHECK','IDENTITYCOL','RIGHT',
    'CHECKPOINT','IF','ROLLBACK','CLOSE','IN','ROWCOUNT','CLUSTERED','INDEX',
    'ROWGUIDCOL','COALESCE','INNER','RULE','COLUMN','INSERT','SAVE',
    'COMMIT','INTERSECT','SCHEMA','COMMITTED','INTO','SELECT','COMPUTE','IS',
    'SERIALIZABLE','CONFIRM','ISOLATION','SESSION_USER','CONSTRAINT',
    'JOIN','SET','CONTAINS','KEY','SETUSER','CONTAINSTABLE','KILL',
    'SHUTDOWN','CONTINUE','LEFT','SOME','CONTROLROW','LEVEL','STATISTICS',
    'CONVERT','LIKE','SUM','COUNT','LINENO','SYSTEM_USER','CREATE','LOAD',
    'TABLE','CROSS','MAX','TAPE','CURRENT','MIN','TEMP','CURRENT_DATE',
    'MIRROREXIT','TEMPORARY','CURRENT_TIME','NATIONAL','TEXTSIZE',
    'CURRENT_TIMESTAMP','NOCHECK','THEN','CURRENT_USER','NONCLUSTERED','TO'
    'CURSOR','NOT','TOP','DATABASE','NULL','TRAN','DBCC','NULLIF',
    'TRANSACTION','DEALLOCATE','OF','TRIGGER','DECLARE','OFF','TRUNCATE',
    'DEFAULT','OFFSETS','TSEQUAL','DELETE','ON','UNCOMMITTED','DENY','ONCE'
    'UNION','DESC','ONLY','UNIQUE','DISK','OPEN','UPDATE','DISTINCT',
    'OPENDATASOURCE','UPDATETEXT','DISTRIBUTED','OPENQUERY','USE','DOUBLE',
    'OPENROWSET','USER','DROP','OPTION','VALUES','DUMMY','OR','VARYING',
    'DUMP','ORDER','VIEW','ELSE','OUTER','WAITFOR','END','OVER','WHEN',
    'ERRLVL','PERCENT','WHERE','ERROREXIT','PERM','WHILE','ESCAPE',
    'PERMANENT','WITH','EXCEPT','PIPE','WORK','EXEC','PLAN','WRITETEXT',
    'EXECUTE','PRECISION','EXISTS','PREPARE', 'OUTPUT')
                              
compile = compile.create_child() # create a database-engine specific compiler
 # add local engine-specific reserved words
compile.add_reserved_words(RESERVED_WORDS)

# ----------- SQL Server-specific built-in functions --------------------------


class IsNull(NamedFunc):
    "Enable use of SQL Server ISNULL built-in function"
    name = "ISNULL"

class Replace(NamedFunc):
    "Enable use of SQL Server REPLACE built in function"
    name = "REPLACE"

# ----------- SQL Server-specific built-in functions --------------------------

class Output(Expr):
    """
    Inserts the "OUTPUT INSERTED.*" subclause to an INSERT.

    This is only supported in Microsoft SQL Server 2005, not 2000.
    """

    def __init__(self, insert):
        self.insert = insert

# ----------- SQL Server-specific syntax overrides ----------------------------

@compile.when(Output)
def compile_output(compile, expr, state):

    state.push("context", COLUMN)
    columns = compile(expr.insert.primary_columns, state)
    state.pop()

    state.push("precedence", 0)
    insert = compile(expr.insert, state)
    state.pop()

    return "%s" % insert
#    return "%s %s" % (insert, columns)
#    return "INSERT INTO person (name) OUTPUT INSERTED.* VALUES ('Joe Johnes')"

@compile.when(Insert)
def compile_insert(compile, insert, state):
    state.push("context", COLUMN_NAME)
    columns = compile(tuple(insert.map), state, token=True)
    state.context = TABLE
    table = build_tables(compile, insert.table, insert.default_table, state)
    state.context = EXPR
    values = compile(tuple(insert.map.itervalues()), state)
    state.pop()
    return "".join(["INSERT INTO ",
                    table,
                    " (", columns, ") OUTPUT INSERTED.* VALUES ",
                    "(",  values, ")"])

@compile.when(Select)
def compile_select(compile, select, state):
    tokens = ["SELECT "]
    if select.distinct:
        tokens.append("DISTINCT ")
    if select.limit is not Undef:
        tokens.append(" TOP %d " % select.limit)
    state.push("auto_tables", [])
    state.push("context", COLUMN)
    tokens.append(compile(select.columns, state))
    tables_pos = len(tokens)
    parameters_pos = len(state.parameters)
    state.context = EXPR
    if select.where is not Undef:
        tokens.append(" WHERE ")
        tokens.append(compile(select.where, state, raw=True))
    if select.group_by is not Undef:
        tokens.append(" GROUP BY ")
        tokens.append(compile(select.group_by, state, raw=True))
    if select.order_by is not Undef:
        tokens.append(" ORDER BY ")
        tokens.append(compile(select.order_by, state, raw=True))
    if select.offset is not Undef:
        tokens.append(" OFFSET %d" % select.offset)
    if has_tables(state, select):
        state.context = g_table_context
        state.push("parameters", [])
        tokens.insert(tables_pos, " FROM ")
        table_tokens =  build_tables(compile, select.tables, select.default_tables, state)
        tokens.insert(tables_pos+1, table_tokens)
        parameters = state.parameters
        state.pop()
        state.parameters[parameters_pos:parameters_pos] = parameters
    state.pop()
    state.pop()
    return "".join(tokens)


@compile.when(SQLToken)
def compile_sql_token(compile, expr, state):
    """
    Put square brackets around any object name which uses
    reserved words or which contains special characters
    such as space, punctuation, etc.
    """
    if is_safe_token(expr) and not compile.is_reserved_word(expr):
        return expr
    return '[%s]' % expr.replace('"', '""')


def compile_type(compile, expr, state):
    #for some reason this gets called for compiling tables; not sure why not use @compile.when(Table)
    cls_info = get_cls_info(expr)
    table = compile(cls_info.table, state)
    if state.context is TABLE_WITH_NOLOCK:
        table += ' WITH (NOLOCK) '
    if state.context is TABLE and issubclass(expr, ClassAlias):
        return "%s AS %s" % (compile(cls_info.cls, state), table)
    return table


class MsSQLResult(Result):
    """
    MS SQL-specific Result subclass
    """


class MsSQLConnection(Connection):

    result_factory = MsSQLResult
    param_mark = "?"
    compile = compile

    @staticmethod
    def to_database(params):
        """
        Like L{Connection.to_database}, but this also converts
        instances of L{datetime} types to strings, and strings
        instances to C{buffer} instances.
        """
        for param in params:
            if isinstance(param, Variable):
                param = param.get(to_db=True)
            if isinstance(param, (datetime, date, time, timedelta)):
                yield str(param)
            elif isinstance(param, str):
                yield buffer(param)
            else:
                yield param

    def execute(self, statement, params=None, noresult=False):
        """Execute a statement with the given parameters.

        This extends the L{Connection.execute} method to add support
        for automatic retrieval of inserted primary keys to link
        in-memory objects with their specific rows.
        """
        if (isinstance(statement, Insert) and
            statement.primary_variables is not Undef and
            statement.primary_columns is not Undef):
            
            if ENABLE_IDENTITY_INSERT:
                # SQL Server does not allow insertion into identity columns
                # explicitly allowed by calling SET IDENTITY_INSERT tablename ON
                identity_insert_table = None
                for variable in statement.map.itervalues():
                #for variable in statement.primary_variables:
                    if variable.has_changed and isIdentityColumn (statement.table, 
                                                                  variable.column.name):
                        identity_insert_table = statement.table
                        break # only need to discover one identity column
                if identity_insert_table:
                    setIdentityInsert (identity_insert_table, state='ON')
            
            # Here we decorate the Insert statement with an Output
            # expression, so that we get back in the result the values
            # for the primary key just inserted.  This prevents a round
            # trip to the database for obtaining these values.
            result = Connection.execute(self, Output(statement), params)
            for variable, value in zip(statement.primary_variables, result.get_one()):
                result.set_variable(variable, value)

            if ENABLE_IDENTITY_INSERT:
                # now disable identity insert if it was enabled before the insert
                if identity_insert_table:
                    setIdentityInsert (identity_insert_table, state='OFF')
            return result
                

        return Connection.execute(self, statement, params, noresult)
        
    def raw_execute_direct(self, statement, params=None):
        """
        mxODBC-specific method; see mxODBC docs for executedirect
        """
        raw_cursor = self.build_raw_cursor()
        trace("connection_raw_execute", self, raw_cursor,
              statement, params or ())
        if params:
            args = (statement, tuple(self.to_database(params)))
        else:
            args = (statement,)
        try:
            self._check_disconnect(raw_cursor.executedirect, *args)
        except Exception, error:
            trace("connection_raw_execute_error", self, raw_cursor,
                  statement, params or (), error)
            raise
        return raw_cursor
        
def set_mx_execute_direct():
    MsSQLConnection.raw_execute = MsSQLConnection.raw_execute_direct
     

class MsSQL (Database):

    connection_factory = MsSQLConnection
    _converters = None

    def __init__(self, uri):
        if MsSQLdbapi is dummy:
            raise DatabaseModuleError("mssql_connector was not initialized.")
        self._connect_kwargs = {}
        if uri.database is not None:
            self._connect_kwargs["db"] = uri.database
        if uri.host is not None:
            self._connect_kwargs["dsn"] = uri.host # we treat the hostname as a database source name
        if uri.port is not None:
            self._connect_kwargs["port"] = uri.port
        if uri.username is not None:
            self._connect_kwargs["user"] = uri.username
        if uri.password is not None:
            self._connect_kwargs["password"] = uri.password # changed from 'passwd' to 'password'
        for option in ["unix_socket"]:
            if option in uri.options:
                self._connect_kwargs[option] = uri.options.get(option)
                
        global g_backend_connection
        g_backend_connection = _BackendConnection(self._connect_kwargs)
        
#        if self._converters is None:
#            # MySQLdb returns a timedelta by default on TIME fields.
#            converters = MySQLdb.converters.conversions.copy()
#            converters[MySQLdb.converters.FIELD_TYPE.TIME] = _convert_time
#            self.__class__._converters = converters

###        self._connect_kwargs["conv"] = self._converters
###        self._connect_kwargs["use_unicode"] = True
###        self._connect_kwargs["charset"] = uri.options.get("charset", "utf8")

    def raw_connect(self):
        raw_connection = MsSQLdbapi.connect(**self._connect_kwargs)
        MsSQLdbapi.stormify_connection(raw_connection)
        return raw_connection

# Storm API expects the backend to provide a callable named 'create_from_uri'
# to establish the backend database; here we use the MsSQL class for that.
create_from_uri = MsSQL 


class _BackendConnection (object):
    """
    Wrap a raw connection designed for use by this backend only
    for purposes of database introspection. It has the capability
    of attempting reconnect once, if a call to cursor() fails to
    deliver due to a dropped connection.
    """
    def __init__ (self, connect_kwargs):
        self._connect_kwargs = connect_kwargs
        self.connection = MsSQLdbapi.connect(**self._connect_kwargs)
        MsSQLdbapi.stormify_connection(self.connection)
    def reconnect (self):
        self.connection = MsSQLdbapi.connect(**self._connect_kwargs)
        MsSQLdbapi.stormify_connection(self.connection)
    def cursor (self):
        try:
            cursor = self.connection.cursor()
        except ProgrammingError, e:
            # somehow the previous connection was closed
            self.reconnect()
            cursor = self.connection.cursor()
        return cursor


def setIdentityInsert (table_name, state):
    """
    Call MS SQL Server's SET IDENTITY_INSERT statement.
    
    @table_name is a string indicating the table name
    @state is a string, either 'ON' or 'OFF'
    """
    query = "SET IDENTITY_INSERT %s %s\n" % (table_name, state)
    cursor = g_backend_connection.cursor()
    try:
        cursor.execute(query)
    except Exception, e:
        print "Error setting identity insert:", e
    cursor.close()
    

def isIdentityColumn (table_name, column_name):
    """
    MS SQL Server has the concept of identity columns, which 
    auto-increments numeric values every time a record is inserted.
    (Other databases use different names for the same concept:
    MySQL uses the term 'AUTO INCREMENT', Oracle calls it 'SEQUENCE',
    PostGreSQL calls it 'SERIAL'.)
    
    This function introspects the database for a given
    table and column to determine if it is an identity column,
    and caches the result in a module level attribute.
    """
    # makes use of module level attribute cache
    cached_result = g_table_column_cache.get((table_name,column_name), None)
    if cached_result:
        return cached_result
    query =  """SELECT is_identity FROM sys.all_columns columns WHERE object_id = 
                       (SELECT TOP 1 object_id FROM sys.tables tables
                       WHERE tables.[name] = ?
                         AND columns.[name] = ?)
             """
    cursor = g_backend_connection.cursor()
    cursor.executedirect(query, (table_name, column_name))
    result = cursor.fetchall()
    cursor.close()
    if not result:
        raise ValueError, 'Unknown table/column:' + str(table_name) + '.' + str(column_name)
    # each table/column should be unique in the db, so expect only one or zero result
    assert len(result) == 1
    if result:
        is_identity = bool(result[0][0])
    g_table_column_cache[(table_name, column_name)] = is_identity
    return is_identity


g_table_column_cache = dict() # define a cache for use with isIdentityColumn
