"""
References the MySQLdb package at:
http://sourceforge.net/projects/mysql-python

From the MySQL manual:

"If the server SQL mode has ANSI_QUOTES enabled, string literals can be
quoted only with single quotes. A string quoted with double quotes will be
interpreted as an identifier."

So use single quotes throughout.
"""

# Use _mysql directly to avoid all of the DB-API overhead.
import _mysql
import warnings
import datetime
from dejavu import storage, logic
from dejavu.storage import db


class AdapterToMySQL(db.AdapterToSQL):
    
    escapes = [("'", "''"), ("\\", r"\\")]
    like_escapes = [("%", r"\%"), ("_", r"\_")]
    
    # TRUE and FALSE only work with 4.1 or better.
    bool_true = "1"
    bool_false = "0"
    
    def coerce_str(self, value):
        return "'" + _mysql.escape_string(value) + "'"
    
    def coerce_bool(self, value):
        # TRUE and FALSE only work with 4.1 or better.
        if value:
            return '1'
        return '0'


class AdapterFromMySQL(db.AdapterFromDB):
    
    def coerce_bool(self, value, coltype):
        if isinstance(value, basestring):
            # either '0' or '1'
            value = (value == '1')
        return bool(value)
    
    def coerce_unicode(self, value, coltype):
        return unicode(value, "utf-8")


class MySQLDecompiler(db.SQLDecompiler):
    
    def dejavu_today(self):
        return "CURDATE()"


class MySQLDecompiler411(MySQLDecompiler):
    # Before MySQL 4.1.1, BINARY comparisons could use UPPER()
    # or LOWER() to perform case-insensitive comparisons. Newer
    # versions must use CONVERT() to obtain a case-sensitive
    # encoding, like utf8.
    
    def dejavu_icontainedby(self, op1, op2):
        if isinstance(op1, db.ConstWrapper):
            # Looking for text in a field. Use Like (reverse terms).
            return ("CONVERT("+ op2 + " USING utf8) LIKE '%" +
                    self.adapter.escape_like(op1) + "%'")
        else:
            # Looking for field in (a, b, c).
            atoms = [self.adapter.coerce(x) for x in op2.basevalue]
            return "CONVERT(%s USING utf8) IN (%s)" % (op1, ", ".join(atoms))
    
    def dejavu_istartswith(self, x, y):
        return ("CONVERT(" + x + " USING utf8) LIKE '" +
                self.adapter.escape_like(y) + "%'")
    
    def dejavu_iendswith(self, x, y):
        return ("CONVERT(" + x + " USING utf8) LIKE '%" +
                self.adapter.escape_like(y) + "'")
    
    def dejavu_ieq(self, x, y):
        return "CONVERT(" + x + " USING utf8) = " + y


class FieldTypeAdapterMySQL(db.FieldTypeAdapter):
    """Return the SQL typename of a DB column."""
    
    # This was determined through experimentation. Don't change it.
    numeric_max_precision = 253
    
    def coerce_str(self, cls, key):
        prop = getattr(cls, key)
        bytes = int(prop.hints.get(u'bytes', '0'))
        if bytes:
            # MySQL VARBINARY/BLOBs will do case-sensitive comparisons.
            # They also won't truncate trailing spaces like VARCHAR does.
            if bytes <= 255:
                return u"VARBINARY(%s)" % bytes
            elif bytes < 2 ** 16:
                return "BLOB"
            elif bytes < 2 ** 24:
                return "MEDIUMBLOB"
        return u"LONGBLOB"
    
    def coerce_bool(self, cls, key):
        # We could use BOOLEAN, but it wasn't introduced until 4.1.0.
        return u"BOOL"
    
    def coerce_datetime_datetime(self, cls, key):
        return u"DATETIME"


class StorageManagerMySQL(db.StorageManagerDB):
    """StoreManager to save and retrieve Units via _mysql."""
    
    sql_name_max_length = 64
    # MySQL uses case-sensitive database and table names on Unix, but
    # not on Windows. Use all-lowercase identifiers to work around the
    # problem. "Column names, index names, and column aliases are not
    # case sensitive on any platform."
    # If deployers set lower_case_table_names to 1, it would help.
    sql_name_caseless = True
    
    typeAdapter = FieldTypeAdapterMySQL()
    toAdapter = AdapterToMySQL()
    fromAdapter = AdapterFromMySQL()
    
    def __init__(self, name, arena, allOptions={}):
        db.StorageManagerDB.__init__(self, name, arena, allOptions)
        
        connargs = ["host", "user", "passwd", "db", "port", "unix_socket",
                    "conv", "connect_time", "compress", "named_pipe",
                    "init_command", "read_default_file", "read_default_group",
                    "cursorclass", "client_flag",
                    ]
        self.connargs = dict([(k, v) for k, v in allOptions.iteritems()
                              if k in connargs])
        self.dbname = self.connargs['db']
        
        self.decompiler = MySQLDecompiler
        # Try to get the version string from MySQL, to see if we need
        # a different decompiler.
        conn = self._template_conn()
        data, columns = self.fetch("SELECT VERSION();", conn)
        if data:
            version = storage.Version(data[0][0])
            if version > storage.Version("4.1.1"):
                self.decompiler = MySQLDecompiler411
        conn.close()
    
    def sql_name(self, name, quoted=True):
        name = db.StorageManagerDB.sql_name(self, name, quoted)
        if quoted:
            name = '`' + name.replace('`', '``') + '`'
        return name
    
    def _get_conn(self):
        try:
            conn = _mysql.connect(**self.connargs)
        except _mysql.OperationalError, x:
            if x.args[0] == 1040:   # Too many connections
                raise db.OutOfConnectionsError
            raise
        return conn
    
    def _template_conn(self):
        tmplconn = self.connargs.copy()
        tmplconn['db'] = 'mysql'
        return _mysql.connect(**tmplconn)
    
    def fetch(self, query, conn=None):
        """fetch(query, conn=None) -> rowdata, columns.
        
        rowdata: a nested list (or tuples), column values within rows.
        columns: a series of 2-tuples (or more). The first tuple value
            will be the column name, the second value will be the column
            type.
        """
        if conn is None:
            conn = self.connection()
        self.execute(query, conn)
        # store_result uses a client-side cursor
        res = conn.store_result()
        return res.fetch_row(0, 0), res.describe()
    
    def destroy(self, unit):
        """destroy(unit). Delete the unit."""
        self.execute(u'DELETE FROM %s WHERE %s;' %
                     (self.table_name(unit.__class__.__name__),
                      self.id_clause(unit)))
    
    def version(self):
        conn = self._template_conn()
        rowdata, cols = self.fetch("SELECT version();", conn)
        conn.close()
        return "MySQL Version: %s" % rowdata[0][0]
    
    #                               Schemas                               #
    
    def create_database(self):
        # _mysql has create_db and drop_db commands, but they're deprecated.
        sql = 'CREATE DATABASE %s;' % self.sql_name(self.dbname)
        conn = self._template_conn()
        self.execute(sql, conn)
        conn.close()
    
    def drop_database(self):
        sql = 'DROP DATABASE %s;' % self.sql_name(self.dbname)
        conn = self._template_conn()
        self.execute(sql, conn)
        conn.close()
    
    def create_storage(self, cls):
        clsname = cls.__name__
        tablename = self.table_name(clsname)
        
        coerce = self.typeAdapter.coerce
        fields = []
        for key in cls.properties():
            fields.append(u'%s %s' % (self.column_name(clsname, key),
                                      coerce(cls, key)))
        self.execute(u'CREATE TABLE %s (%s);' % (tablename, ", ".join(fields)))
        
        for index in cls.indices():
            i = self.table_name("i" + clsname + index)
            
            dbtype = coerce(cls, index)
            if dbtype.endswith('BLOB') or dbtype == 'TEXT':
                # MySQL won't allow indexes on a BLOB field
                # without a specific length.
                self.execute(u'CREATE INDEX %s ON %s (%s(%s));' %
                             (i, tablename,
                              self.column_name(clsname, index), 255))
            else:
                self.execute(u'CREATE INDEX %s ON %s (%s);' %
                             (i, tablename,
                              self.column_name(clsname, index)))
    
    def rename_property(self, cls, oldname, newname):
        clsname = cls.__name__
        oldcolname = self.column_name(clsname, oldname)
        newcolname = self.column_name(clsname, newname)
        if oldcolname != newcolname:
            self.execute("ALTER TABLE %s CHANGE %s %s %s;" %
                         (self.table_name(clsname), oldcolname, newcolname,
                          self.typeAdapter.coerce(cls, newname)))

