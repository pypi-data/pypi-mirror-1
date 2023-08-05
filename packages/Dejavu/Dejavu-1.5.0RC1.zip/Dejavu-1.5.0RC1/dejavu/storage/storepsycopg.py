# Use _psycopg directly to avoid overhead.
try:
    # If possible, you should copy the _psycopg.pyd file into a top level
    # so this SM can avoid importing the entire package.
    import _psycopg
except ImportError:
    from psycopg2 import _psycopg


import datetime
try:
    import cPickle as pickle
except ImportError:
    import pickle
import re
seq_name = re.compile(r"nextval\('([^:]+)'.*\)")
escape_oct = re.compile(r"[\000-\037\177-\377]")
replace_oct = lambda m: r"\\%03o" % ord(m.group(0))
unescape_oct = re.compile(r"\\(\d\d\d)")
replace_unoct = lambda m: chr(int(m.group(1), 8))

import dejavu
from dejavu import errors
from dejavu.storage import db


class AdapterToPsycoPg(db.AdapterToSQL):
    
    like_escapes = [("%", r"\\%"), ("_", r"\\_")]
    
    # Do these need to know if "SHOW DateStyle;" != "ISO, MDY" ?
    def coerce_datetime_datetime_to_any(self, value):
        return ("'%04d-%02d-%02d %02d:%02d:%02d.%06d'" %
                (value.year, value.month, value.day,
                 value.hour, value.minute, value.second,
                 value.microsecond))
    
    def coerce_datetime_date_to_any(self, value):
        return "'%04d-%02d-%02d'" % (value.year, value.month, value.day)
    
    def coerce_datetime_time_to_any(self, value):
        return ("'%02d:%02d:%02d.%06d'" %
                (value.hour, value.minute, value.second, value.microsecond))
    
    def coerce_any_to_bytea(self, value):
        # See http://www.postgresql.org/docs/8.1/interactive/datatype-binary.html
        value = pickle.dumps(value, 2)
        def repl(char):
            o = ord(char)
            if o <= 31 or o == 39 or o == 92 or o >= 127:
                return r"\\%03d" % int(oct(o))
            return char
        return "'%s'::bytea" % "".join(map(repl, value))
    
    def do_pickle(self, value):
        value = pickle.dumps(value, 2)
        value = self.coerce_str_to_any(value, skip_encoding=False)
        return value
    coerce_dict_to_any = do_pickle
    coerce_list_to_any = do_pickle
    coerce_tuple_to_any = do_pickle
    
    def coerce_str_to_any(self, value, skip_encoding=False):
        if not skip_encoding and not isinstance(value, str):
            value = value.encode(self.encoding)
        for pat, repl in self.escapes:
            value = value.replace(pat, repl)
        
        # Escape octal sequences
        value = escape_oct.sub(replace_oct, value)
        return "'" + value + "'"


class AdapterFromPsycoPg(db.AdapterFromDB):
    
    def coerce_any_to_str(self, value):
        # Unescape octal sequences
        value = unescape_oct.sub(replace_unoct, value)
        if isinstance(value, unicode):
            return value.encode(self.encoding)
        else:
            return str(value)
    
    def coerce_any_to_datetime_datetime(self, value):
        return value
    
    def coerce_any_to_datetime_date(self, value):
        return value
    
    def coerce_any_to_datetime_time(self, value):
        return value


class PsycoPgDecompiler(db.SQLDecompiler):
    
    def dejavu_icontainedby(self, op1, op2):
        if isinstance(op1, db.ConstWrapper):
            # Looking for text in a field. Use ILike (reverse terms).
            return op2 + " ILIKE '%" + self.adapter.escape_like(op1) + "%'"
        else:
            # Looking for field in (a, b, c).
            # Force all args to lowercase for case-insensitive comparison.
            atoms = [self.adapter.coerce(x).lower() for x in op2.basevalue]
            return "LOWER(%s) IN (%s)" % (op1, ", ".join(atoms))
    
    def dejavu_istartswith(self, x, y):
        return x + " ILIKE '" + self.adapter.escape_like(y) + "%'"
    
    def dejavu_iendswith(self, x, y):
        return x + " ILIKE '%" + self.adapter.escape_like(y) + "'"
    
    def dejavu_ieq(self, x, y):
        # ILIKE with no wildcards should behave like ieq.
        return x + " ILIKE '" + self.adapter.escape_like(y) + "'"
    
    def dejavu_year(self, x):
        return "date_part('year', " + x + ")"
    
    def dejavu_month(self, x):
        return "date_part('month', " + x + ")"
    
    def dejavu_day(self, x):
        return "date_part('day', " + x + ")"


class PsycoPgIndexSet(db.IndexSet):
    
    def __delitem__(self, key):
        """Drop the specified index."""
        t = self.table
        t.db.lock("Dropping index. Transactions not allowed.")
        try:
            # PG doesn't use DROP INDEX .. ON ..
            t.db.execute('DROP INDEX %s;' % self[key].qname)
        finally:
            t.db.unlock()


class PsycoPgTable(db.Table):
    
    indexsetclass = PsycoPgIndexSet


class PsycoPgDatabase(db.Database):
    
    sql_name_max_length = 63
    quote_all = True
    poolsize = 10
    encoding = 'SQL_ASCII'
    
    decompiler = PsycoPgDecompiler
    adaptertosql = AdapterToPsycoPg()
    adapterfromdb = AdapterFromPsycoPg()
    tableclass = PsycoPgTable
    
    def _get_dbinfo(self, conn=None):
        dbinfo = {}
        try:
            data, _ = self.fetch("SELECT pg_encoding_to_char(encoding) "
                                 "FROM pg_database;", conn=conn)
            dbinfo['encoding'] = data[0][0]
        except _psycopg.DatabaseError, x:
            if "does not exist" not in x.args[0]:
                raise
        return dbinfo
    
    def _get_tables(self, conn=None):
        data, _ = self.fetch("SELECT tablename FROM pg_tables WHERE schemaname"
                             " not in ('information_schema', 'pg_catalog')",
                             conn=conn)
        return [self.tableclass(row[0], self.quote(row[0]), self)
                for row in data]
    
    def _get_table(self, tablename, conn=None):
        data, _ = self.fetch("SELECT tablename FROM pg_tables WHERE "
                             "tablename = '%s'" % tablename,
                             conn=conn)
        for name, in data:
            if name == tablename:
                return self.tableclass(name, self.quote(name), self)
        raise errors.MappingError(tablename)
    
    def _get_columns(self, tablename, conn=None):
        # Get the OID of the table
        data, _ = self.fetch("SELECT oid FROM pg_class WHERE relname = '%s'"
                             % tablename, conn=conn)
        table_OID = data[0][0]
        
        # Get index data so we can set col.key if pg_index.indisprimary
        data, _ = self.fetch("SELECT indkey FROM pg_index WHERE indrelid "
                             "= %s AND indisprimary" % table_OID, conn=conn)
        if data:
            # indkey is an "array" (we get a space-separated string of ints).
            # These will equal pg_attribute.attnum, below.
            indices = map(int, data[0][0].split(" "))
        else:
            indices = []
        
        # Get column data
        sql = ("SELECT attname, atttypid, attnum, attlen, atttypmod "
               "FROM pg_attribute WHERE attisdropped = False AND "
               "attrelid = %s" % table_OID)
        data, _ = self.fetch(sql, conn=conn)
        cols = []
        for row in data:
            name = row[0]
            if name in ('tableoid', 'cmax', 'xmax', 'cmin', 'xmin',
                        'oid', 'ctid'):
                # This is a column which PostgreSQL defines automatically
                continue
            
            # Data type
            dbtype, _ = self.fetch("SELECT typname, typlen FROM pg_type "
                                   "WHERE oid = %s" % row[1])
            if dbtype:
                dbtype = dbtype[0][0].upper()
            else:
                dbtype = None
            c = db.Column(row[0], self.quote(row[0]), dbtype,
                          key=row[2] in indices)
            
            if dbtype in ('FLOAT4', 'FLOAT8'):
                c.hints['precision'] = row[3]
            elif dbtype in ('MONEY', 'NUMERIC'):
                c.hints['precision'] = (row[4] >> 16) & 65535
                c.hints['scale'] = (row[4] & 65535) - 4
            
            # Default value
            default, _ = self.fetch("SELECT adsrc FROM pg_attrdef "
                                    "WHERE adnum = %s AND adrelid = %s"
                                    % (row[2], table_OID))
            if default:
                default = default[0][0]
                if default.startswith("nextval("):
                    # Grab seqname from "nextval(seqname::[text|regclass])"
                    c.autoincrement = True
                    c.sequence_name = seq_name.search(default).group(1)
                    c.initial = self.fetch("SELECT min_value FROM %s" %
                                           c.sequence_name)[0][0]
                    c.default = None
                else:
                    # adsrc is always a string, so we must cast
                    # it using our guessed type.
                    c.default = self.python_type(dbtype)(default)
            else:
                c.default = None
            
            if dbtype.startswith('BPCHAR') or dbtype.startswith('VARCHAR'):
                # See http://archives.postgresql.org/pgsql-interfaces/2004-07/msg00021.php
                c.hints['bytes'] = row[4] - 4
            else:
                bytes = row[3]
                if bytes > 0:
                    c.hints['bytes'] = bytes
                elif dbtype == 'TEXT':
                    c.hints['bytes'] = 0
            
            cols.append(c)
        return cols
    
    def _get_indices(self, tablename, conn=None):
        # Get the OID of the parent table.
        data, _ = self.fetch("SELECT oid FROM pg_class WHERE relname = '%s'"
                             % tablename, conn=conn)
        if not data:
            return []
        
        table_OID = data[0][0]
        indices = []
        data, _ = self.fetch("SELECT pg_class.relname, indkey, indisprimary, "
                             "indisunique FROM pg_index LEFT JOIN pg_class "
                             "ON pg_index.indexrelid = pg_class.oid WHERE "
                             "pg_index.indrelid = %s" % table_OID, conn=conn)
        for row in data:
            # indkey is an "array" (we get a space-separated string of ints).
            cols = map(int, row[1].split(" "))
            for col in cols:
                d, _ = self.fetch("SELECT attname FROM pg_attribute "
                                  "WHERE attrelid = %s AND attnum = %s"
                                  % (table_OID, col), conn=conn)
                i = db.Index(row[0], self.quote(row[0]), tablename,
                             d[0][0], bool(row[3]))
                indices.append(i)
        
        return indices
    
    def python_type(self, dbtype):
        """Return a Python type which can store values of the given dbtype."""
        dbtype = dbtype.upper()
        if dbtype in ('INT2', 'INT4', 'INTEGER', 'SMALLINT'):
            return int
        elif dbtype in ('BOOL', 'BOOLEAN'):
            return bool
        elif dbtype in ('INT8', 'BIGINT'):
            return long
        elif dbtype in ('FLOAT4', 'FLOAT8', 'MONEY', 'DOUBLE PRECISION', 'REAL'):
            return float
        elif dbtype.startswith('NUMERIC'):
            if db.decimal:
                return db.decimal.Decimal
            elif db.fixedpoint:
                return db.fixedpoint.FixedPoint
        elif dbtype == 'DATE':
            return datetime.date
        elif dbtype in ('TIMESTAMP', 'TIMESTAMPTZ'):
            return datetime.datetime
        elif dbtype in ('TIME', 'TIMETZ'):
            return datetime.time
        elif dbtype in ('BYTEA'):
            return str
        for t in ('CHAR', 'VARCHAR', 'BPCHAR', 'TEXT'):
            if dbtype.startswith(t):
                return str
        
        raise TypeError("Database type %r could not be converted "
                        "to a Python type." % dbtype)
    
    def col_def(self, column):
        """Return a clause for the given column for CREATE or ALTER TABLE.
        
        This will be of the form "name type [DEFAULT [x | nextval('seq')]]".
        
        PostgreSQL creates the sequence in a separate statement.
        """
        if column.autoincrement:
            default = "nextval('%s')" % column.sequence_name
        else:
            default = column.default or ""
            if not isinstance(default, str):
                default = self.adaptertosql.coerce(default, column.dbtype)
        
        if default:
            default = " DEFAULT %s" % default
        
        return '%s %s%s' % (column.qname, column.dbtype, default)
    
    def create_sequence(self, table, column):
        """Create a SEQUENCE for the given column and set its sequence_name."""
        sname = column.sequence_name
        if sname is None:
            sname = self.quote("%s_%s_seq" % (table.name, column.name))
            column.sequence_name = sname
        self.execute("CREATE SEQUENCE %s START %s;" % (sname, column.initial))
    
    def drop_sequence(self, column):
        """Drop a SEQUENCE for the given column and remove its sequence_name."""
        if column.sequence_name is not None:
            self.execute("DROP SEQUENCE %s;" % column.sequence_name)
            column.sequence_name = None
    
    def quote(self, name):
        if self.quote_all:
            name = '"' + name.replace('"', '""') + '"'
        return name
    
    def sql_name(self, name):
        name = db.Database.sql_name(self, name)
        if not self.quote_all:
            name = name.lower()
        return name
    
    default_isolation = "READ COMMITTED"
    
    def _get_conn(self):
        try:
            c = _psycopg.connect(self.Connect)
            c.set_isolation_level(0)
            return c
        except _psycopg.DatabaseError, x:
            if x.args[0].startswith('could not connect'):
                raise db.OutOfConnectionsError()
            raise
    
    def _del_conn(self, conn):
        conn.close()
    
    def _template_conn(self):
        atoms = self.Connect.split(" ")
        tmplconn = ""
        for atom in atoms:
            k, v = atom.split("=", 1)
            if k == 'dbname': v = 'template1'
            tmplconn += "%s=%s " % (k, v)
        c = _psycopg.connect(tmplconn)
        # Allow statements like CREATE DATABASE to run outside a transaction.
        c.set_isolation_level(0)
        return c
    
    def execute(self, query, conn=None):
        """execute(query, conn=None) -> result set."""
        if conn is None:
            conn = self.connection()
        if isinstance(query, unicode):
            query = query.encode(self.adaptertosql.encoding)
        self.log(query)
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        finally:
            cursor.close()
    
    def fetch(self, query, conn=None):
        """fetch(query, conn=None) -> rowdata, columns."""
        if conn is None:
            conn = self.connection()
        if isinstance(query, unicode):
            query = query.encode(self.adaptertosql.encoding)
        self.log(query)
        
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            data = cursor.fetchall()
            coldefs = cursor.description
        finally:
            cursor.close()
        
        return data, coldefs
    
    def create_database(self):
        self.lock("Creating database. Transactions not allowed.")
        try:
            # Must shut down all connections to avoid
            # "being accessed by other users" error.
            self.connection.shutdown()
            
            c = self._template_conn()
            encoding = self.encoding
            if encoding:
                encoding = " WITH ENCODING '%s'" % encoding
            self.execute("CREATE DATABASE %s%s" % (self.qname, encoding), c)
            c.close()
            del c
            self.clear()
        finally:
            self.unlock()
    
    def drop_database(self):
        self.lock("Dropping database. Transactions not allowed.")
        try:
            # Must shut down all connections to avoid
            # "being accessed by other users" error.
            self.connection.shutdown()
            
            c = self._template_conn()
            self.execute("DROP DATABASE %s;" % self.qname, c)
            c.close()
            del c
            self.clear()
        finally:
            self.unlock()
    
    def version(self):
        c = self._template_conn()
        data, _ = self.fetch("SELECT version();", c)
        v, = data[0]
        c.close()
        return "%s\npsycopg version: %s" % (v, _psycopg.__version__)



class StorageManagerPsycoPg(db.StorageManagerDB):
    """StoreManager to save and retrieve Units via psycopg2."""
    
    databaseclass = PsycoPgDatabase
    
    def __init__(self, arena, allOptions={}):
        for atom in allOptions['Connect'].split(" "):
            k, v = atom.split("=", 1)
            if k == "dbname":
                allOptions['name'] = v
        db.StorageManagerDB.__init__(self, arena, allOptions)
    
    def _seq_UnitSequencerInteger(self, unit):
        """Reserve a unit using the table's SERIAL field."""
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
        
        transconn = self.db.get_transaction()
        
        fields = ", ".join(fields)
        values = ", ".join(values)
        self.db.execute('INSERT INTO %s (%s) VALUES (%s);' %
                        (t.qname, fields, values), transconn)
        
        # Grab the new ID. This is threadsafe because db.reserve has a mutex.
        idcol = cls.identifiers[0]
        seqname = t[idcol].sequence_name
        data, col_defs = self.db.fetch("SELECT last_value FROM %s;" % seqname,
                                       transconn)
        setattr(unit, idcol, data[0][0])

