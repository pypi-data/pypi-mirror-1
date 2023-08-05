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

import dejavu
from dejavu import storage, logic, errors
from dejavu.storage import db


class AdapterToMySQL(db.AdapterToSQL):
    
    escapes = [("'", "''"), ("\\", r"\\")]
    like_escapes = [("%", r"\%"), ("_", r"\_")]
    
    # TRUE and FALSE only work with 4.1 or better.
    bool_true = "1"
    bool_false = "0"
    
    def coerce_str_to_any(self, value, skip_encoding=False):
        if not skip_encoding and not isinstance(value, str):
            value = value.encode(self.encoding)
        return "'" + _mysql.escape_string(value) + "'"
    
    def coerce_bool_to_any(self, value):
        # TRUE and FALSE only work with 4.1 or better.
        if value:
            return '1'
        return '0'


class AdapterFromMySQL(db.AdapterFromDB):
    
    def coerce_any_to_bool(self, value):
        if isinstance(value, basestring):
            # either '0' or '1'
            value = (value == '1')
        return bool(value)


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


class TypeAdapterMySQL(db.TypeAdapter):
    
    numeric_max_precision = 16
    numeric_max_bytes = 8
    
    def float_type(self, precision):
        """Return a datatype which can handle the given precision."""
        # "p represents the precision in bits, but MySQL uses this value
        # only to determine whether to use FLOAT or DOUBLE for the
        # resulting data type. If p is from 0 to 24, the data type
        # becomes FLOAT with no M or D values. If p is from 25 to 53,
        # the data type becomes DOUBLE with no M or D values."
        return "FLOAT(%s)" % precision
    
    def coerce_str(self, col):
        bytes = int(col.hints.get('bytes', 255))
        
        if bytes:
            # MySQL VARBINARY/BLOBs will do case-sensitive comparisons.
            # They also won't truncate trailing spaces like VARCHAR does.
            if bytes <= 255:
                return "VARBINARY(%s)" % bytes
            elif bytes < 2 ** 16:
                return "BLOB"
            elif bytes < 2 ** 24:
                return "MEDIUMBLOB"
        return "LONGBLOB"
    
    def coerce_bool(self, col):
        # We could use BOOLEAN, but it wasn't introduced until 4.1.0.
        return "BOOL"
    
    def coerce_datetime_datetime(self, col):
        return "DATETIME"
    
    def coerce_int(self, col):
        bytes = int(col.hints.get('bytes', '4'))
        if bytes <= 2:
            return "SMALLINT"
        elif bytes == 3:
            return "MEDIUMINT"
        return "INTEGER"


class TypeAdapterMySQL41(TypeAdapterMySQL):
    
    def coerce_str(self, col):
        dbtype = TypeAdapterMySQL.coerce_str(self, col)
        if dbtype == "BLOB":
            dbtype = "BLOB(%s)" % col.hints['bytes']
        return dbtype


class MySQLIndexSet(db.IndexSet):
    
    def __delitem__(self, key):
        t = self.table
        t.db.lock("Dropping index. Transactions not allowed.")
        try:
            # MySQL might rename multiple-column indices to "PRIMARY"
            for i in t.db._get_indices(t.name):
                if i.colname == self[key].colname:
                    t.db.execute('DROP INDEX %s ON %s;' % (i.qname, t.qname))
        finally:
            t.db.unlock()


class MySQLTable(db.Table):
    
    indexsetclass = MySQLIndexSet
    
    def _rename(self, oldcol, newcol):
        self.db.execute("ALTER TABLE %s CHANGE %s %s %s;" %
                        (self.qname, oldcol.qname, newcol.qname,
                         oldcol.dbtype))


class MySQLDatabase(db.Database):
    
    sql_name_max_length = 64
    # MySQL uses case-sensitive database and table names on Unix, but
    # not on Windows. Use all-lowercase identifiers to work around the
    # problem. "Column names, index names, and column aliases are not
    # case sensitive on any platform."
    # If deployers set lower_case_table_names to 1, it would help.
    sql_name_caseless = True
    encoding = "utf8"
    
    adaptertosql = AdapterToMySQL()
    adapterfromdb = AdapterFromMySQL()
    typeadapter = TypeAdapterMySQL()
    
    tableclass = MySQLTable
    indexsetclass = MySQLIndexSet
    
    # InnoDB default
    default_isolation = "REPEATABLE READ"
    
    def __init__(self, name, **kwargs):
        db.Database.__init__(self, name, **kwargs)
        
        self.decompiler = MySQLDecompiler
        
        # Get the version string from MySQL, to see if we need
        # a different decompiler.
        conn = self._template_conn()
        rowdata, cols = self.fetch("SELECT version();", conn)
        conn.close()
        v = rowdata[0][0]
        self._version = storage.Version(v)
        
        # decompiler
        if self._version > storage.Version("4.1.1"):
            self.decompiler = MySQLDecompiler411
        
        # type adapter
        if self._version >= storage.Version("4.1"):
            self.typeadapter = TypeAdapterMySQL41()
    
    def version(self):
        return "MySQL Version: %s" % self._version
    
    def col_def(self, column):
        """Return a clause for the given column for CREATE or ALTER TABLE.
        
        This will be of the form "name type [DEFAULT x] [AUTO_INCREMENT]"
        """
        dbtype = column.dbtype
        
        autoincr = ""
        if column.autoincrement:
            autoincr = " AUTO_INCREMENT"
        
        default = column.default or ""
        if default:
            default = self.adaptertosql.coerce(default, dbtype)
            default = " DEFAULT %s" % default
        
        return "%s %s%s%s" % (column.qname, dbtype, default, autoincr)
    
    def __setitem__(self, key, table):
        q = self.quote
        if key in self:
            del self[key]
        
        # Set table.db to self, which should "turn on"
        # any future ALTER TABLE statements.
        table.db = self
        
        fields = []
        incr_fields = []
        pk = []
        for colkey, col in table.iteritems():
            fields.append(self.col_def(col))
            
            if col.autoincrement:
                # INSERT INTO t (c) VALUES(0) doesn't work for some reason
                if col.initial > 1:
                    incr_fields.append(col)
            
            if col.key:
                qname = col.qname
                dbtype = col.dbtype
                if dbtype.endswith('BLOB') or dbtype == 'TEXT':
                    # MySQL won't allow indexes on a BLOB field without a
                    # specific index prefix length. We choose 255 just for fun.
                    qname = "%s(255)" % qname
                pk.append(qname)
        
        if pk:
            pk = ", PRIMARY KEY (%s)" % ", ".join(pk)
        else:
            pk = ""
        
        encoding = self.encoding
        if encoding:
            encoding = " CHARACTER SET %s" % encoding
        
        self.lock("Creating storage. Transactions not allowed.")
        try:
            self.execute('CREATE TABLE %s (%s%s)%s;' %
                         (table.qname, ", ".join(fields), pk, encoding))
            
            if incr_fields:
                # Wow, what a hack. We have to INSERT a dummy row to set the
                # autoincrement initial value(s), and we can't delete it until
                # after the CREATE INDEX statements (or the counter will revert).
                fields = ", ".join([col.qname for col in incr_fields])
                values = ", ".join([str(col.initial - 1) for col in incr_fields])
                self.execute("INSERT INTO %s (%s) VALUES (%s);"
                             % (table.qname, fields, values))
            
            for k, index in table.indices.iteritems():
                dbtype = table[k].dbtype
                if dbtype.endswith('BLOB') or dbtype == 'TEXT':
                    # MySQL won't allow indexes on a BLOB field without a
                    # specific index prefix length. We choose 255 just for fun.
                    self.execute('CREATE INDEX %s ON %s (%s(255));' %
                                 (index.qname, table.qname, q(index.colname)))
                else:
                    self.execute('CREATE INDEX %s ON %s (%s);' %
                                 (index.qname, table.qname, q(index.colname)))
            
            if incr_fields:
                self.execute("DELETE FROM %s" % table.qname)
        finally:
            self.unlock()
        
        dict.__setitem__(self, key, table)
    
    def _get_tables(self, conn=None):
        data, _ = self.fetch("SHOW TABLES FROM %s" % self.qname, conn=conn)
        return [self.tableclass(row[0], self.quote(row[0]), self)
                for row in data]
    
    def _get_table(self, tablename, conn=None):
        data, _ = self.fetch("SHOW TABLES FROM %s LIKE '%s'"
                             % (self.qname, tablename), conn=conn)
        for row in data:
            name = row[0]
            if name == tablename:
                return self.tableclass(name, self.quote(name), self)
        raise errors.MappingError(tablename)
    
    def _get_columns(self, tablename, conn=None):
        # cols are: Field, Type, Null, Key, Default, Extra.
        # See http://dev.mysql.com/doc/refman/4.1/en/describe.html
        data, _ = self.fetch("SHOW COLUMNS FROM %s.%s" %
                             (self.qname, self.quote(tablename)), conn=conn)
        cols = []
        for row in data:
            c = db.Column(row[0], self.quote(row[0]), None, None)
            
            dbtype = row[1].upper()
            parenpos = dbtype.find("(")
            if parenpos > -1:
                args = dbtype[parenpos+1:-1]
                baretype = dbtype[:parenpos]
                if baretype in ("DECIMAL", "NUMERIC"):
                    args = [x.strip() for x in args.split(",")]
                    c.hints['precision'], c.hints['scale'] = args
                else:
                    c.hints['bytes'] = args
            elif dbtype == "FLOAT":
                c.hints['precision'] = 24
            elif dbtype.startswith("DOUBLE"):
                c.hints['precision'] = 53
            elif dbtype in ("TINYBLOB", "TINYTEXT"):
                c.hints['bytes'] = (2 ** 8) - 1
            elif dbtype in ("BLOB", "TEXT"):
                c.hints['bytes'] = (2 ** 16) - 1
            elif dbtype in ("MEDIUMBLOB", "MEDIUMTEXT"):
                c.hints['bytes'] = (2 ** 24) - 1
            elif dbtype in ("LONGBLOB", "LONGTEXT"):
                c.hints['bytes'] = (2 ** 32) - 1
            
            c.key = (row[3] == "PRI")
            
            if row[4]:
                c.default = self.python_type(dbtype)(row[4])
            
            if "auto_increment" in row[5].lower():
                c.autoincrement = True
            
            c.dbtype = dbtype
            
            cols.append(c)
        return cols
    
    def _get_indices(self, tablename, conn=None):
        indices = []
        try:
            # cols are: Table, Non_unique, Key_name, Seq_in_index, Column_name,
            # Collation, Cardinality, Sub_part, Packed, Null, Index_type, Comment
            data, _ = self.fetch("SHOW INDEX FROM %s.%s"
                                 % (self.qname, self.quote(tablename)),
                                 conn=conn)
        except _mysql.ProgrammingError, x:
            if x.args[0] != 1146:
                raise
        else:
            for row in data:
                i = db.Index(row[2], self.quote(row[2]),
                             row[0], row[4], not row[1])
                indices.append(i)
        return indices
    
    def python_type(self, dbtype):
        """Return a Python type which can store values of the given dbtype."""
        dbtype = dbtype.upper()
        parenpos = dbtype.find("(")
        if parenpos > -1:
            dbtype = dbtype[:parenpos]
        
        if dbtype in ('TINYINT', 'SMALLINT', 'MEDIUMINT', 'INT', 'INTEGER'):
            return int
        elif dbtype == 'BIGINT':
            return long
        elif dbtype in ('BOOL', 'BOOLEAN'):
            return bool
        elif dbtype in ('FLOAT', 'DOUBLE', 'DOUBLE PRECISION', 'REAL'):
            return float
        elif dbtype in ('DECIMAL', 'NUMERIC'):
            if db.decimal:
                return db.decimal.Decimal
            elif db.fixedpoint:
                return db.fixedpoint.Fixedpoint
        elif dbtype == 'DATE':
            return datetime.date
        elif dbtype in ('DATETIME', 'TIMESTAMP'):
            return datetime.datetime
        elif dbtype == 'TIME':
            return datetime.time
        elif dbtype in ('CHAR', 'VARCHAR', 'BINARY', 'VARBINARY',
                        'TINYBLOB', 'TINYTEXT', 'BLOB', 'TEXT',
                        'MEDIUMBLOB', 'MEDIUMTEXT', 'LONGBLOB', 'LONGTEXT'):
            return str
        
        raise TypeError("Database type %r could not be converted "
                        "to a Python type." % dbtype)
    
    def quote(self, name):
        """Return name, quoted for use in an SQL statement."""
        return '`' + name.replace('`', '``') + '`'
    
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
    
    def execute(self, query, conn=None):
        """execute(query, conn=None) -> result set."""
        if conn is None:
            conn = self.connection()
        if isinstance(query, unicode):
            query = query.encode(self.adaptertosql.encoding)
        self.log(query)
        try:
            return conn.query(query)
        except _mysql.OperationalError, x:
            if x.args[0] == 1030 and x.args[1] == 'Got error 139 from storage engine':
                raise ValueError("row length exceeds 8000 byte limit")
            raise
    
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
        
        # The Python MySQLdb library swallows lock timeouts and returns []
        # (for example, when deadlocked during a SERIALIZABLE transaction).
        # Raise an error instead.
        # Oddly, although the deadlock will stall the conn.query() call,
        # the error message is only available after store_result().
        err = conn.error()
        if err == "Lock wait timeout exceeded; try restarting transaction":
            raise _mysql.OperationalError(1205, err)
        
        if res is None:
            return [], []
        return res.fetch_row(0, 0), res.describe()
    
    def create_database(self):
        self.lock("Creating database. Transactions not allowed.")
        try:
            # _mysql has create_db and drop_db commands, but they're deprecated.
            encoding = self.encoding
            if encoding:
                encoding = " CHARACTER SET %s" % encoding
            sql = 'CREATE DATABASE %s%s;' % (self.qname, encoding)
            conn = self._template_conn()
            self.execute(sql, conn)
            conn.close()
            self.clear()
        finally:
            self.unlock()
    
    def drop_database(self):
        self.lock("Dropping database. Transactions not allowed.")
        try:
            sql = 'DROP DATABASE %s;' % self.qname
            conn = self._template_conn()
            self.execute(sql, conn)
            conn.close()
            self.clear()
        finally:
            self.unlock()
    
    def is_lock_error(self, exc):
        # OperationalError: (1205, 'Lock wait timeout exceeded; try restarting transaction')
        if not isinstance(exc, _mysql.OperationalError):
            return False
        return exc.args[0] == 1205


class StorageManagerMySQL(db.StorageManagerDB):
    """StoreManager to save and retrieve Units via _mysql."""
    
    databaseclass = MySQLDatabase
    
    def __init__(self, arena, allOptions={}):
        connargs = ["host", "user", "passwd", "db", "port", "unix_socket",
                    "conv", "connect_time", "compress", "named_pipe",
                    "init_command", "read_default_file", "read_default_group",
                    "cursorclass", "client_flag",
                    ]
        connargs = dict([(k, v) for k, v in allOptions.iteritems()
                         if k in connargs])
        allOptions['connargs'] = connargs
        allOptions['name'] = connargs['db']
        db.StorageManagerDB.__init__(self, arena, allOptions)
    
    def _seq_UnitSequencerInteger(self, unit):
        """Reserve a unit using the table's AUTO_INCREMENT field."""
        cls = unit.__class__
        t = self.db[cls.__name__]
        
        fields = []
        values = []
        for key in cls.properties:
            col = t[key]
            if col.autoincrement:
                # Skip this field, since we're using a sequencer
                continue
            val = self.db.adaptertosql.coerce(getattr(unit, key), col.dbtype)
            fields.append(col.qname)
            values.append(val)
        
        fields = ", ".join(fields)
        values = ", ".join(values)
        
        conn = self.db.get_transaction()
        self.db.execute('INSERT INTO %s (%s) VALUES (%s);' %
                        (t.qname, fields, values), conn)
        
        # Grab the new ID. This is threadsafe because db.reserve has a mutex.
        setattr(unit, cls.identifiers[0], conn.insert_id())

