# ingres/base.py
# 
"""Support for the Ingres Database

Versions
--------

This dialect was tested against Ingres 9.2.  Some features may not work on earlier versions.
The driver used during testing was ingresdbi, available from esd.ingres.com.  zxjdbc has been tried
but not fully tested.

Connection Strings
------------------

The argument "selectloops=y" should be used for all connections.  The format of the URL is similar
to that for the ingresdbi driver; refer to its documentation for further information.  In general:
ingres://server/database?uid=user;pwd=passwd;selectloops=y

where server is the remote server name, or (LOCAL) if local,
      database is the name of the database to connect to,
      user is the username to connect as, if necessary and
      passwd is the given user's password, if necessary. 

"""

from sqlalchemy import types, schema
from sqlalchemy.engine import default, reflection
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import compiler

ischema_names = {'ANSIDATE': types.Date,
           'BYTE': types.Binary,
           'BYTE VARYING': types.Binary,
           'C': types.TEXT,
           'CHAR': types.CHAR,
           'DATE': types.DateTime,
           'DECIMAL': types.DECIMAL,
           'FLOAT': types.Float,
           'INGRESDATE': types.DateTime,
           'INTEGER': types.Integer,
           'INTERVAL YEAR TO MONTH': types.Interval,
           'INTERVAL DAY TO SECOND': types.Interval,
           'LONG BYTE': types.Binary,
           'LONG NVARCHAR': types.UnicodeText,
           'LONG VARCHAR': types.CLOB,
           'MONEY': types.DECIMAL,
           'NCHAR': types.NCHAR,
           'NVARCHAR': types.NVARCHAR,
           #'OBJECT_KEY': types.,
           #'TABLE_KEY':,
           'TEXT': types.TEXT,
           'TIME WITH TIME ZONE': types.TIME,
           'TIME WITHOUT TIME ZONE': types.TIME,
           'TIME WITH LOCAL TIME ZONE': types.TIME,
           'TIMESTAMP WITH TIME ZONE': types.TIMESTAMP,
           'TIMESTAMP WITHOUT TIME ZONE': types.TIMESTAMP,
           'TIMESTAMP WITH LOCAL TIME ZONE': types.TIMESTAMP,
           'VARCHAR': types.VARCHAR}

class _IngresBoolean(types.Boolean):
    def get_dbapi_type(self, dbapi):
        return dbapi.TINYINT
    
    def result_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            return value and True or False
        return process

    def bind_processor(self, dialect):
        def process(value):
            if value is True:
                return 1
            elif value is False:
                return 0
            elif value is None:
                return None
            else:
                return value and True or False
        return process
    
class _IngresDateWithoutTime(types.Date):
    def get_dbapi_type(self, dbapi):
        return dbapi.DATE
    
    def result_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            
            
colspecs = {types.Boolean: _IngresBoolean}

class IngresTypeCompiler(compiler.GenericTypeCompiler):
    def visit_TIME(self, type_):
        if type_.tzinfo is None:
            return 'TIME WITHOUT TIME ZONE'
        else:
            return 'TIME WITH TIME ZONE'
        
    def visit_BOOLEAN(self, type_):
        return self.visit_TINYINT(type_)
    def visit_TINYINT(self, type_):
        return 'TINYINT'
    def visit_DATETIME(self, type_):
        return 'INGRESDATE'
    def visit_DATE(self, type_):
        return 'ANSIDATE'
    def visit_CLOB(self, type_):
        return 'LONG VARCHAR'
    def visit_NCLOB(self, type_):
        return 'LONG NVARCHAR'
    def visit_BLOB(self, type_):
        return "LONG BYTE"
    def visit_TEXT(self, type_):
        return self.visit_CLOB(type_)
    def visit_DECIMAL(self, type_):
        if type_.precision is None:
            return "DECIMAL"
        elif type_.scale is None:
            return "DECIMAL(%(precision)s)" % {'precision': type_.precision}
        else:
            return "DECIMAL(%{precision}s,%{scale}s)" % {'precision': type_.precision, 
                                                         'scale': type_.scale}
    def visit_unicode(self,type_):
        return self.visit_NVARCHAR(type_)
    def visit_unicode_text(self,type_):
        return self.visit_NCLOB(type_)
    
class IngresSQLCompiler(compiler.SQLCompiler):
    def visit_sequence(self, seq):
        return 'NEXT VALUE FOR %s' % self.preparer.format_sequence(seq)
    
    def limit_clause(self, select):
        text = ""
        
        if not self.is_subquery():
            if select._offset:
                text += '\nOFFSET %s' % select._offset
            if select._limit:
                text += '\nFETCH FIRST %s ROWS ONLY' % select._limit
        return text
    
    def get_select_precolumns(self, select):
        s = ""
        if select._distinct and not self.is_subquery():
            s = " DISTINCT "
        return s
        
    def visit_release_savepoint(self, savepoint_stmt):
        return ""
    
class _Modify(DDLElement):
    """Represents a MODIFY Statment"""
    
    __visit_name__ = "modify"
    
    def __init__(self, target, **kwargs):
        self.target = target
        self.kwargs = kwargs

class IngresDDLCompiler(compiler.DDLCompiler):

    def visit_drop_constraint(self, drop):
        table = drop.element.table
        constr = drop.element
        return 'ALTER TABLE %s DROP CONSTRAINT %s %s' % (
            self.preparer.format_table(table),
            self.preparer.format_constraint(constr),
            drop.cascade and 'CASCADE' or 'RESTRICT'
        )
    
    def get_column_default_string(self, column):
        if isinstance(column.server_default, schema.DefaultClause):
            if isinstance(column.server_default.arg, basestring):
                return "'%s'" % column.server_default.arg
            else:
                return unicode(self._compile(column.server_default.arg, None))
        elif isinstance(column.default, schema.Sequence):
            return 'NEXT VALUE FOR %s' % self.preparer.format_sequence(column.default)
        else:
            return None

    def visit_create_index(self, create):
        text = compiler.DDLCompiler.visit_create_index(self, create)
        index = create.element
        if 'ingres_structure' in index.kwargs:
            text += ' WITH STRUCTURE=%s' % (index.kwargs['ingres_structure'])
            if 'ingres_structure_keys' in index.kwargs:
                if 'ingres_structure_key_unique' in index.kwargs \
                and index.kwargs['ingres_structure_key_unique']:
                    text += ' UNIQUE '
                text += ' ON '
                text += ", ".join(["%s" % col for col in index.kwargs['ingres_structure_keys']])
                 
        return text
    
    def post_create_table(self, table):        
        if 'ingres_structure' in table.kwargs:
            _Modify(table, **(table.kwargs)).execute_at("after-create", 
                                                        table)
        return ''
    
    def visit_modify(self, modify):
        text = 'MODIFY %s TO ' % modify.target 
        if 'ingres_structure' in modify.kwargs:
            text += "%s" % modify.kwargs['ingres_structure']
            
            if 'ingres_structure_keys' in modify.kwargs:
                if 'ingres_structure_key_unique' in modify.kwargs \
                and modify.kwargs['ingres_structure_key_unique']:
                    text += ' UNIQUE '
                text += ' ON '
                text += ", ".join(["%s" % col for col in modify.kwargs['ingres_structure_keys']])
        return text
    
class IngresExecutionContext(default.DefaultExecutionContext):
    def __init__(self, *args, **kwargs):
        default.DefaultExecutionContext.__init__(self, *args, **kwargs)
        
    def fire_sequence(self, seq):
        return self._execute_scalar('SELECT NEXT VALUE FOR %s' \
                                   % self.dialect.identifier_preparer.format_sequence(seq))
    
class IngresDialect(default.DefaultDialect):
    name                  = 'ingres'
    default_paramstyle    = 'qmark'
    max_identifier_length = 32
    colspecs              = colspecs
    ischema_names         = ischema_names
    statement_compiler    = IngresSQLCompiler
    type_compiler         = IngresTypeCompiler
    statement_compiler    = IngresSQLCompiler
    ddl_compiler          = IngresDDLCompiler
    execution_ctx_cls     = IngresExecutionContext
    supports_sequences    = True
    supports_unicode_statements = False
    supports_empty_insert = False
    postfetch_lastrowid   = False
    requires_name_normalization = True
    sequences_optional    = False
    
    def __init__(self, **kwargs):
        default.DefaultDialect.__init__(self, **kwargs)

    @reflection.cache        
    def get_columns(self, connection, table_name, schema=None, **kw):
        sqltext = """
            SELECT
                column_name,
                column_datatype,
                column_nulls,
                column_default_val,
                column_length,
                column_scale
            FROM
                iicolumns
            WHERE
                table_name = ?"""
        params = [self.denormalize_name(table_name)]
        
        if schema:
            sqltext += """
                AND table_owner = ?"""
            params.append(self.denormalize_name(schema))
            
        sqltext += """
            ORDER BY
                column_sequence"""
            
        rs = None
        columns = []
        try:
            rs = connection.execute(sqltext, params)
            
            for row in rs.fetchall():
                coldata = {}
                coldata['name'] = row[0].rstrip()
                coltype = row[1].rstrip()
                coldata['nullable'] = row[2].upper() == 'Y'
                coldata['default'] = row[3]
                
                if coltype == 'C' \
                        or coltype == 'CHAR' \
                        or coltype == 'VARCHAR' \
                        or coltype == 'TEXT' \
                        or coltype == 'NVARCHAR' \
                        or coltype == 'NCHAR' \
                        or coltype == 'BYTE' \
                        or coltype == 'BYTE VARYING' \
                        or coltype == 'INTEGER' \
                        or coltype == 'FLOAT':
                    length = row[4]
                    coldata['type'] = ischema_names[coltype](length)
                    
                elif coltype == 'DECIMAL':
                    (precision, scale) = (row[4], row[5])
                    coldata['type'] = ischema_names[coltype](precision, scale)
                else:
                    coldata['type'] = ischema_names[coltype]
                
                columns.append(coldata)
                
            rs.close()
            return columns
        finally:
            if rs:
                rs.close()
                
    @reflection.cache
    def get_primary_keys(self, connection, table_name, schema=None, **kw):
        sqltext = """
            SELECT
                k.column_name
            FROM
                iikeys k,
                iiconstraints c
            WHERE
                k.constraint_name = c.constraint_name
            AND c.constraint_type = 'P'
            AND k.table_name = ?"""
        params = [self.denormalize_name(table_name)]
        
        if schema:
            sqltext += """
                AND k.schema_name = ?"""
            params.append(self.denormalize_name(schema))
        
        rs = None
        
        try:
            rs = connection.execute(sqltext, params)
            
            return [row[0].rstrip() for row in rs.fetchall()]
        finally:
            if rs:
                rs.close()
                
    @reflection.cache
    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        sqltext = """
            SELECT
                f.constraint_name AS name,
                f.column_name AS constrained_column,
                p.schema_name AS referred_schema,
                p.table_name AS referred_table,
                p.column_name AS referred_column
            FROM
                iikeys f,
                iikeys p,
                iiref_constraints rc,
                iiconstraints c
            WHERE
                c.constraint_type = 'R'
            AND c.constraint_name = rc.ref_constraint_name
            AND p.constraint_name = rc.unique_constraint_name
            AND f.constraint_name = rc.ref_constraint_name
            AND p.key_position = f.key_position
            AND f.table_name = ?"""
        params = [self.denormalize_name(table_name)]
        
        if schema:
            sqltext += """
                AND f.schema_name = ?"""
            params.append(self.denormalize_name(schema))
            
        sqltext += """
            ORDER BY 
                f.key_position"""
        
        rs = None
        foreign_keys = {}
        try:
            rs = connection.execute(sqltext, params)
            
            for row in rs.fetchall():
                name = row[0].rstrip()
                if name in foreign_keys:
                    constraint = foreign_keys[name]
                else:
                    constraint = {}
                    constraint['name'] = name
                    constraint['constrained_columns'] = []
                    constraint['referred_table'] = row[3].rstrip()
                    constraint['referred_columns'] = []
                    
                    ref_schema = row[2].rstrip()
                    def_schema = connection.default_schema_name
                    
                    if def_schema != ref_schema:
                        constraint['referred_schema'] = ref_schema
                    else:
                        constraint['referred_schema'] = None
                    #constraint['referred_schema'] = row[2].rstrip()
                
                constraint['constrained_columns'].append(row[1].rstrip())
                constraint['referred_columns'].append(row[4].rstrip())
                
                foreign_keys[name] = constraint
                
            rs.close()
            return foreign_keys.values()
        finally:
            if rs:
                rs.close()
    
    @reflection.cache
    def get_table_names(self, connection, schema=None, **kw):
        sqltext = """
            SELECT
                table_name
            FROM
                iitables
            WHERE
                table_type = 'T'"""
        params = None
                
        if schema:
            sqltext += """
                AND table_owner = ?"""
            params = [self.denormalize_name(schema)]
            
            if schema != "$ingres":
                sqltext += " AND table_name NOT LIKE 'ii%'"
        else:
            sqltext += """
                AND table_owner != '$ingres'
                AND table_name NOT LIKE 'ii%'"""
            
        rs = None
        
        try:
            rs = connection.execute(sqltext, params)
        
            return [row[0].rstrip() for row in rs.fetchall()]
        finally:
            if rs:
                rs.close()

    @reflection.cache                
    def get_schema_names(self, connection, **kw):
        sqltext = """
            SELECT
                schema_name
            FROM 
                iischema"""
                
        rs = None
        
        try:
            rs = connection.execute(sqltext)
            
            return [row[0].rstrip() for row in rs.fetchall()]
        finally:
            if rs:
                rs.close()
                
    def table_names(self, connection, schema=None, **kw):
        return self.get_table_names(connection, schema, **kw)
    
    @reflection.cache
    def get_view_names(self, connection, schema=None, **kw):
        sqltext = """
            SELECT
                table_name
            FROM
                iiviews"""
        params = None
        
        if schema:
            sqltext += """
                WHERE
                    table_owner = ?"""
            params = [self.denormalize_name(schema)]
        else:
            sqltext += """
                WHERE 
                    table_owner != '$ingres'"""
            
        rs = None
        
        try:
            rs = connection.execute(sqltext, params)
            
            return [row[0].rstrip() for row in rs.fetchall()]
        finally:
            if rs:
                rs.close()

    @reflection.cache
    def get_view_definition(self, connection, view_name, schema=None, **kw):
        sqltext = """
            SELECT
                text_segment
            FROM
                iiviews
            WHERE
                table_name = ?"""
        params = [self.denormalize_name(view_name)]
        
        if schema:
            sqltext += """
                AND table_owner = ?"""
            params.append(self.denormalize_name(schema))
        else:
            sqltext += """
                AND table_owner != '$ingres'"""
            
        sqltext += """
            ORDER BY
                text_sequence"""
                
        rs = None
        
        try:
            rs = connection.execute(sqltext, params)
            
            return "".join([row[0] for row in rs.fetchall()])
        finally:
            if rs:
                rs.close()
    
    @reflection.cache
    def get_indexes(self, connection, table_name, schema=None, **kw):
        sqltext = """
            SELECT
                i.index_name,
                c.column_name,
                i.unique_rule
            FROM
                iiindexes i,
                iiindex_columns c
            WHERE
                i.index_name = c.index_name
            AND i.index_owner = c.index_owner
            AND i.base_name = ?"""
        params = [self.denormalize_name(table_name)]
        
        if schema:
            sqltext += """
                AND i.index_owner = ?"""
            params.append(self.denormalize_name(schema))
            
        sqltext += """
            ORDER BY
                c.key_sequence"""
                
        rs = None
        indexes = {}
        
        try:
            rs = connection.execute(sqltext, params)
            
            for row in rs.fetchall():
                name = row[0].rstrip()
                if name in indexes:
                    index = indexes[name]
                else:
                    index = {}
                    index['name'] = name
                    index['column_names'] = []
                    index['unique'] = row[2] == 'U'
                    
                index['column_names'].append(row[1].rstrip())
                
                indexes[name] = index
                
            return indexes.values()
        finally:
            if rs:
                rs.close()
                    
    
    def normalize_name(self, name):
        if name is None:
            return None
        else:
            return name.decode('latin1')
        
    
    def denormalize_name(self, name):
        if name is None:
            return None
        else:
            return name.lower().encode('latin1')
        
    def has_table(self, connection, table_name, schema=None):
        sqltext = """
            SELECT 
                table_name
            FROM 
                iitables
            WHERE
                table_name = ?
            AND table_type = 'T'"""
        params = [self.denormalize_name(table_name)]
        
        if schema:
            sqltext += """
                AND table_owner = ?"""
            params.append(self.denormalize_name(schema))

        rs = None
        try:
            rs = connection.execute(sqltext, params)
            return len(rs.fetchall()) > 0
        finally:
            if rs:
                rs.close()
            
    def has_sequence(self, connection, sequence_name, schema=None):
        sqltext = """
            SELECT
                seq_name
            FROM
                iisequences
            WHERE
                seq_name = ?"""
        params = [self.denormalize_name(sequence_name)]
        
        if schema:
            sqltext += """
                AND seq_owner = ?"""
            params.append(self.denormalize_name(schema))
            
        rs = None
        
        try:
            rs = connection.execute(sqltext, params)
            return len(rs.fetchall()) > 0
        finally:
            if rs:
                rs.close()
    
    def get_default_schema_name(self, connection):
        sqltext = """SELECT dbmsinfo('username')"""
        
        rs = None
        try:
            rs = connection.execute(sqltext)
            return rs.fetchone()[0]
        finally:
            if rs:
                rs.close()
