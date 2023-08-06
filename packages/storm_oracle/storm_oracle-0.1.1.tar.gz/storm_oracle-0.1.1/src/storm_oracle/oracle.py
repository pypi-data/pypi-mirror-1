#
# Copyright (c) 2008 Alfaiati
#
# Written by Gustavo Noronha <kov@alfaiati.net>
#            Willi Langenberger <wlang@wu-wien.ac.at>
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
import os
import sys
from decimal import Decimal

from storm.tracer import trace
from storm.databases import dummy

# if no NLS_LANG is set, we'll use english with UTF-8
# Note that this variable MUST be set before importing
# cx_Oracle.
if not os.environ.get("NLS_LANG", None):
    os.environ["NLS_LANG"] = 'american_america.utf8'
try:
    import cx_Oracle as oracle
except Exception, e:
    oracle = dummy
    from traceback import format_exc
    sys.stderr.write('Encountered an error importing cx_Oracle')
    sys.stderr.write(format_exc())

from storm.variables import Variable, RawStrVariable, PickleVariable
from storm.database import Database, Connection, Result
from storm.exceptions import (install_exceptions, ClosedError, DatabaseModuleError, 
                              DatabaseError, OperationalError)
from storm.info import get_cls_info, ClassAlias
from storm.expr import (
    Undef, SetExpr, Select, Insert, Alias, And, Eq, FuncExpr, SQLRaw,
    Le, Gt, Column, is_safe_token, Except, Expr, Sequence, SQLToken,
    COLUMN, COLUMN_NAME, COLUMN_PREFIX, TABLE, compile, compile_eq,
    compile_select, compile_insert, compile_set_expr, compile_sql_token,
    State)

install_exceptions(oracle)
compile = compile.create_child()

RESERVED = set(
"""ACCESS ADD ALL ALTER AND ANY AS ASC AUDIT BETWEEN BY CHAR 
   CHECK CLUSTER COLUMN COMMENT COMPRESS CONNECT CREATE CURRENT
   DATE DECIMAL DEFAULT DELETE DESC DISTINCT DROP ELSE EXCLUSIVE
   EXISTS FILE FLOAT FOR FROM GRANT GROUP HAVING IDENTIFIED 
   IMMEDIATE IN INCREMENT INDEX INITIAL INSERT INTEGER INTERSECT
   INTO IS LEVEL LIKE LOCK LONG MAXEXTENTS MINUS MLSLABEL MODE
   MODIFY NOAUDIT NOCOMPRESS NOT NOWAIT NULL NUMBER OF OFFLINE
   ON ONLINE OPTION OR ORDER PCTFREE PRIOR PRIVILEGES PUBLIC
   RAW RENAME RESOURCE REVOKE ROW ROWS SELECT SESSION
   SET SHARE SIZE SMALLINT START SUCCESSFUL SYNONYM SYSDATE 
   TABLE THEN TO TRIGGER UID UNION UNIQUE UPDATE USER VALIDATE
   VALUES VARCHAR VARCHAR2 VIEW WHENEVER WHERE WITH""".split())

def alias_names():
    ct = 0
    while 1:
        yield '_%x' % ct
        ct += 1

@compile.when(type)
def compile_type(compile, expr, state):
    cls_info = get_cls_info(expr)
    table = compile(cls_info.table, state)
    if state.context is TABLE and issubclass(expr, ClassAlias):
        return "%s %s" % (compile(cls_info.cls, state), table)
    return table

@compile.when(Alias)
def compile_alias(compile, alias, state):
    name = compile(alias.name, state, token=True)
    if state.context is COLUMN or state.context is TABLE:
        return "%s %s" % (compile(alias.expr, state), name)
    return name

@compile.when(Sequence)
def compile_sequence_oracle(compile, sequence, state):
    return "%s.NEXTVAL" % sequence.name

class Minus(SetExpr):
    oper = " MINUS "

@compile.when(Except)
def compile_except_oracle(compile, expr, state):
    new_expr = Minus()
    new_expr.exprs = expr.exprs
    new_expr.all = expr.all
    new_expr.order_by = expr.order_by
    new_expr.limit = expr.limit
    new_expr.offset = expr.offset
    return compile_set_expr_oracle(compile, new_expr, state)

@compile.when(SetExpr)
def compile_set_expr_oracle(compile, expr, state):

    names = alias_names()

    if isinstance(expr, Minus):
        # Build new set expression without arguments (order_by, etc).
        new_expr = expr.__class__()
        new_expr.exprs = expr.exprs
        new_expr.all = expr.all

        if expr.order_by is not Undef:
            # Make sure that state.aliases isn't None, since we want them to
            # compile our order_by statement below.
            no_aliases = state.aliases is None
            if no_aliases:
                state.push("aliases", {})

            aliases = {}
            for subexpr in expr.exprs:
                if isinstance(subexpr, Select):
                    columns = subexpr.columns
                    if not isinstance(columns, (tuple, list)):
                        columns = [columns]
                    else:
                        columns = list(columns)
                    for i, column in enumerate(columns):
                        if column not in aliases:
                            if isinstance(column, Column):
                                aliases[column] = columns[i] = Alias(column, name=names.next())
                            elif isinstance(column, Alias):
                                aliases[column.expr] = column
                    subexpr.columns = columns
            aliases.update(state.aliases)
            state.aliases = aliases
            aliases = None

        set_stmt = SQLRaw('(%s)' % compile(expr.exprs, state, join=expr.oper))

        if expr.order_by is not Undef:
            # Build order_by statement, using aliases.
            state.push("context", COLUMN_NAME)
            order_by_stmt = SQLRaw(compile(expr.order_by, state))
            state.pop()
        else:
            order_by_stmt = Undef

        # Build wrapping select statement.
        select = Select(SQLRaw("*"), tables=Alias(set_stmt, name=names.next()), limit=expr.limit,
                        offset=expr.offset, order_by=order_by_stmt)

        return compile_select(compile, select, state)
    return compile_set_expr(compile, expr, state)



@compile.when(Select)
def compile_select_oracle(compile, select, state):
    limit = select.limit
    offset = select.offset
    # make sure limit is Undef'ed
    select.offset = select.limit = Undef

    names = alias_names()

    if select.default_tables is Undef:
        select.default_tables = ['DUAL']

    if select.order_by is not Undef:
        # copied from expr.py's compile_set_expr
        aliases = {}
        columns = select.columns
        if not isinstance(columns, (tuple, list)):
            columns = [columns]
        else:
            columns = list(columns)
        for i, column in enumerate(columns):
            if column not in aliases:
                if isinstance(column, Column):
                    aliases[column] = columns[i] = Alias(column, name=names.next())
                elif isinstance(column, Alias):
                    aliases[column.expr] = column
        select.columns = columns
        # /copied from expr.py's compile_set_expr
        stmt = SQLRaw("(%s)" % compile_select(compile, select, state))
        select = Select(SQLRaw('*'), tables=Alias(stmt, name=names.next()))

    if (limit is not Undef) and (offset is not Undef):
        rownum_alias = Alias(SQLRaw('ROWNUM'), name=names.next())

        # if we have an SQLRaw here that is because we are dealing
        # with a subquery
        if isinstance(select.columns, SQLRaw):
            select.columns = [SQLRaw('"' + select.tables.name + '".*'), rownum_alias]
        else:
            select.columns.append(rownum_alias)

        where_expr = Le(SQLRaw('ROWNUM'), limit + offset)
        if select.where is Undef:
            select.where = where_expr
        else:
            select.where = And(select.where, where_expr)

        stmt = SQLRaw("(%s)" % compile_select(compile, select, state))
        select = Select(SQLRaw('*'), tables=Alias(stmt, names.next()), where = Gt(rownum_alias, offset))
    elif limit is not Undef:
        expr = Le(SQLRaw('ROWNUM'), limit)
        if select.where is Undef:
            select.where = expr
        else:
            select.where = And(select.where, expr)
    elif offset is not Undef:
        rownum_alias = Alias(SQLRaw('ROWNUM'), name=names.next())

        # if we have an SQLRaw here that is because we are dealing
        # with a subquery
        if isinstance(select.columns, SQLRaw):
            select.columns = [SQLRaw('"' + select.tables.name + '".*'), rownum_alias]
        else:
            select.columns.append(rownum_alias)

        stmt = SQLRaw("(%s)" % compile_select(compile, select, state))
        select = Select(SQLRaw('*'), tables=Alias(stmt, name=names.next()), where = Gt(rownum_alias, offset))

    return compile_select(compile, select, state)

@compile.when(Insert)
def compile_insert_oracle(compile, insert, state):
    # shamelessly copied from PostgreSQL
    if not insert.map and insert.primary_columns is not Undef:
        insert.map.update(dict.fromkeys(insert.primary_columns,
                                        SQLRaw("DEFAULT")))
    return compile_insert(compile, insert, state)

@compile.when(Sequence)
def compile_sequence_oracle(compile, sequence, state):
    return "%s.nextval" % sequence.name

@compile.when(bool)
def compile_bool(compile, expr, state):
    return compile_eq(compile, Eq(1, int(expr)), state)    

class currval(FuncExpr):

    name = "currval"

    def __init__(self, column):
        self.column = column

@compile.when(currval)
def compile_currval(compile, expr, state):
    """Compile a currval.
    """
    state.push("context", COLUMN_PREFIX)
    table = compile(expr.column.table, state, token=True)
    state.pop()
    return "%s_seq.currval" % (table)

class Rowid(Expr):
    def __init__(self, rowid):
        self.rowid = rowid

@compile.when(Rowid)
def compile_rowid(compile, expr, state):
    state.parameters.append(expr.rowid)
    return "?"


@compile.when(SQLToken)
def compile_oracle_sql_token(compile, expr, state):
    if "." in expr and state.context in (TABLE, COLUMN_PREFIX):
        return ".".join(compile_sql_token(compile, subexpr, state)
                        for subexpr in expr.split("."))
    # A bit of a hack:  we're skipping the built-in reserved word list
    # and using our own set.
    if is_safe_token(expr) and not str(expr) in RESERVED:
        return expr
    elif state.context in (COLUMN, COLUMN_NAME) \
            and str(expr).lower() in ('rowid', 'rownum'):
        return expr
    return '"%s"' % expr.replace('"', '|')

class OracleResult(Result):

    def __init__(self, connection, raw_cursor, rowid = None):
        super(OracleResult, self).__init__(connection, raw_cursor)
        self.lastrowid = rowid
        
    def get_insert_identity(self, primary_key, primary_variables):
        return Eq(Column('rowid'), Rowid(self.lastrowid))

    @staticmethod
    def set_variable(variable, value):
        if isinstance(value, float):
            value = Decimal(str(value))

        variable.set(value, from_db=True)

    @staticmethod
    def from_database(row):
        """Convert Oracle-specific datatypes to "normal" Python types.

        If there are anny C{buffer} instances in the row, convert them
        to strings.
        """
        for value in row:
            if isinstance(value, oracle.LOB):
                yield value.read()
            else:
                yield value

class OracleConnection(Connection):

    result_factory = OracleResult
    compile = compile
    param_mark = "?"
    
    def as_read_committed(self):
        return _isolation_context(self)
    
    def is_disconnection_error(self, exc):
        if isinstance(exc, oracle.DatabaseError):
            error, = exc.args
            #Sometimes exceptions get caught here without a code attribute

            if hasattr(error, 'code') and error.code in (3135, 3113):
                return True
        return False
    

    def execute(self, statement, params=None, noresult=False):
        """NOTE: this is being overriden completely because the
        original from the base class expects to receive only a
        raw_cursor from raw_execute, and we need to receive also the
        rowid, as we cannot set it in the cursor object
 
        Execute a statement with the given parameters.

        @type statement: L{Expr} or C{str}
        @param statement: The statement to execute. It will be
            compiled if necessary.
        @param noresult: If True, no result will be returned.

        @raise DisconnectionError: Raised when the connection is lost.
            Reconnection happens automatically on rollback.

        @return: The result of C{self.result_factory}, or None if
            C{noresult} is True.
        """
        if self._closed:
            raise ClosedError("Connection is closed")
        self._ensure_connected()
        if self._event:
            self._event.emit("register-transaction")
        if isinstance(statement, Expr):
            if params is not None:
                raise ValueError("Can't pass parameters with expressions")
            state = State()
            statement = self.compile(statement, state)
            params = state.parameters
        statement = convert_to_sequential(statement)
        raw_cursor, rowid = self.raw_execute(statement, params)
        if noresult:
            self._check_disconnect(raw_cursor.close)
            return None
        return self.result_factory(self, raw_cursor, rowid)

    def raw_execute(self, statement, params):
        """NOTE: this is being overriden completely because the original
        from the base class converts params to a tuple, and we need a dictionary!

        Execute a raw statement with the given parameters.

        It's acceptable to override this method in subclasses, but it
        is not intended to be called externally.

        If the global C{DEBUG} is True, the statement will be printed
        to standard out.

        @return: The dbapi cursor object, as fetched from L{build_raw_cursor}.
        """
        rowid = None
        raw_cursor = self.build_raw_cursor()

        statement = str(statement)

        if statement.startswith('INSERT INTO'):
            statement = statement + ' RETURNING ROWID INTO :out_rowid'

            # make sure params is a list as we need to add to it
            if params is None:
                params = list()
            elif not isinstance(params, list):
                params = list(params)

            rowid = raw_cursor.var(oracle.ROWID)
            params.append(rowid)

        if not params:
            params = ()
        else:
            params = tuple(self.to_database(params))
            

        trace("connection_raw_execute", self, raw_cursor,
              statement, params or ())

        try:
            self._check_disconnect(raw_cursor.execute, statement, params)
            if rowid:
                rowid = rowid.getvalue()
        except DatabaseError, de:
            error, = de.args
            if error == 8177:
                raise OperationalError('database is locked')
            else:
                raise
        except Exception, error:
            trace("connection_raw_execute_error", self, raw_cursor,
                  statement, params or (), error)
            raise
        else:
            trace("connection_raw_execute_success", self, raw_cursor,
                  statement, params or ())
        return raw_cursor, rowid

    @staticmethod
    def to_database(params):
        for bind_var in params:
            if isinstance(bind_var, (RawStrVariable, PickleVariable)):
                yield oracle.Binary(bind_var.get(to_db=True))
            elif isinstance(bind_var, Variable):
                yield bind_var.get(to_db=True)
            else:
                yield  bind_var

            
    

def convert_to_sequential(statement):
    """Convert a query using ? bind variables to a query using
       sequential bind variables.  For example, SELECT ? FROM DUAL
       will be converted to SELECT :1 FROM DUAL"""
    param_no = 1
    tokens = statement.split("'")
    for i in range(0, len(tokens), 2):
        while True:
            old_tokens = tokens[i]
            new_tokens = old_tokens.replace('?', ':%s' % param_no, 1)
            if old_tokens == new_tokens:
                break
            else:
                tokens[i] = new_tokens
                param_no += 1
    return "'".join(tokens)

class _isolation_context(object):
    def __init__ (self, connection):
        self.connection = connection
    def __enter__(self):
        self.connection.commit()
        self.connection.execute('ALTER SESSION SET isolation_level = read committed')
            
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.execute('ALTER SESSION SET isolation_level = serializable')
        self.connection.commit()
            
class _type_converter(object):
    """This class wraps an input type handler and an output type handler.
       The reason being to allow for saving the encoding for the session."""
    def __init__(self, encoding):
        self.encoding = encoding

    def convert_unicode(self, value):
        if isinstance(value, Variable):
            value = value.get(to_db=True)
        if not isinstance(value, unicode):
            return unicode(value, 'utf8')
        else:
            return value
        
    def OutputTypeHandler(self, cursor, name, defaultType, size, precision, scale):
        """This function's purpose is to tell cx_Oracle how to convert an Oracle 
            datatype into a Python datatype."""
        if defaultType in (oracle.UNICODE, oracle.FIXED_UNICODE):
            return cursor.var(unicode, size, cursor.arraysize,
                              outconverter=self.convert_unicode)
        elif defaultType in (oracle.STRING, oracle.FIXED_CHAR):
            return cursor.var(str, size, cursor.arraysize)
    
    def InputTypeHandler(self, cursor, value, numElements):
        """This function does the opposite of OutputTypeHandler:  it tells cx_Oracle
            how to convert a Python datatype into an Oracle datatype."""
        if isinstance(value, unicode):
            return cursor.var(unicode, arraysize=numElements, 
                              inconverter=self.convert_unicode)
    
class Oracle(Database):

    connection_factory = OracleConnection
    converter_factory = _type_converter
    raw_connection_factory = oracle.connect

    def __init__(self, uri):
        if oracle is dummy:
            raise DatabaseModuleError("'cx_Oracle' failed to load")

        if not uri.port:
            uri.port = 1521

        isolation = uri.options.get("isolation", "serializable")
        isolation_mapping = {
            "serializable": 'SERIALIZABLE',
            "read-committed": 'READ COMMITTED',
        }
        try:
            self._isolation = isolation_mapping[isolation]
        except KeyError:
            raise ValueError(
                "Unknown serialization level %r: expected one of "
                "'serializable' or 'read-committed'" %
                (isolation,))
        
        # Optionally set ORACLE_HOME and TNS_ADMIN environment
        # variables for controlling tnsnames.ora lookup
        oracle_home = uri.options.get('oracle_home')
        if oracle_home:
            os.environ['ORACLE_HOME'] = oracle_home

        # If tns is specified in the options, treat the host part of the URI as
        # the TNS name, and therefore the DSN.
        if uri.options.get('tns', False): 
            self._dsn = uri.host
        else:
            self._dsn = oracle.makedsn(uri.host, uri.port, uri.database)

        self._username = uri.username
        self._password = uri.password

    def raw_connect(self):
        raw_connection = self.raw_connection_factory(self._username, self._password, self._dsn)

        c = raw_connection.cursor()
        c.execute('alter session set isolation_level=%s' % self._isolation)
        c.close()

        type_handler = self.converter_factory(raw_connection.nencoding)
        raw_connection.inputtypehandler = type_handler.InputTypeHandler
        raw_connection.outputtypehandler = type_handler.OutputTypeHandler

        return raw_connection

create_from_uri = Oracle
