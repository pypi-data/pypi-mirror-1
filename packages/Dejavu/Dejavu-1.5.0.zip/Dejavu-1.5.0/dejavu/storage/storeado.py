import sys
# Put COM in free-threaded mode. This first thread will have
# CoInitializeEx called automatically when pythoncom is imported.
sys.coinit_flags = 0

import pythoncom
Empty = pythoncom.Empty
clsctx = pythoncom.CLSCTX_SERVER

import win32com.client

# InvokeTypes args (always pass as *args)
BOF = (1002, 0, 2, (11, 0), ())
EOF = (1006, 0, 2, (11, 0), ())
Recordset_Fields = (0, 0, 2, (9, 0), ())
# This assumes no arguments passed to GetRows
Recordset_GetRows = (1016, 0, 1, (12, 0), ((3, 49), (12, 17), (12, 17)), -1, Empty, Empty)
Recordset_Close = (1014, 0, 1, (24, 0), (),)
Fields_Count = (1, 0, 2, (3, 0), ())
Field_Name = (1100, 0, 2, (8, 0), ())
Field_Type = (1102, 0, 2, (3, 0), ())
Field_Properties = (500, 0, 2, (9, 0), ())
Property_Value = (0, 0, 2, (12, 0), ())

import pywintypes
import datetime
import time

try:
    import cPickle as pickle
except ImportError:
    import pickle

import threading
import warnings

import dejavu
from dejavu import errors, logic, storage
from dejavu.storage import db, isolation as _isolation

adOpenForwardOnly = 0
adOpenKeyset = 1
adOpenDynamic = 2
adOpenStatic = 3

adLockReadOnly = 1
adLockPessimistic = 2
adLockOptimistic = 3
adLockBatchOptimistic = 4

adSchemaColumns = 4
adSchemaIndexes = 12
adSchemaTables = 20
adSchemaPrimaryKeys = 28

adUseClient = 3

# 12/30/1899, the zero-Date for ADO = 693594
# "Sure, there are two 4-byte integers stored. But they are
# packed together into a BINARY(8). The first 4-byte being
# the elapsed number days since SQL Server's base date of
# 1900-01-01. The Second 4-bytes Store the Time of Day
# Represented as the Number of Milliseconds After Midnight."
# http://www.sql-server-performance.com/fk_datetime.asp
zeroHour = datetime.date(1899, 12, 30).toordinal()

# Note also that SQL Server allows DATETIME in the range:
# "1753-01-01 00:00:00.0" to "9999-12-31 23:59:59.997".

dbtypes = {
    0: 'EMPTY',                     2: 'SMALLINT',
    3: 'INTEGER',                   4: 'SINGLE',
    5: 'DOUBLE',                    6: 'CURRENCY',
    7: 'DATE',                      8: 'BSTR',
    9: 'IDISPATCH',                 10: 'ERROR',
    11: 'BOOLEAN',                  12: 'VARIANT',
    13: 'IUNKNOWN',                 14: 'DECIMAL',
    16: 'TINYINT',                  17: 'UNSIGNEDTINYINT',
    18: 'UNSIGNEDSMALLINT',         19: 'UNSIGNEDINT',
    20: 'BIGINT',                   21: 'UNSIGNEDBIGINT',
    72: 'GUID',                     128: 'BINARY',
    129: 'CHAR',                    130: 'WCHAR',
    131: 'NUMERIC',                 132: 'USERDEFINED',
    133: 'DBDATE',                  134: 'DBTIME',
    135: 'DBTIMESTAMP',             200: 'VARCHAR',
    201: 'LONGVARCHAR',             202: 'VARWCHAR',
    203: 'LONGVARWCHAR',            204: 'VARBINARY',
    205: 'LONGVARBINARY'
}

DBCOLUMNFLAGS_WRITE = 0x4
DBCOLUMNFLAGS_WRITEUNKNOWN = 0x8
DBCOLUMNFLAGS_ISFIXEDLENGTH = 0x10
DBCOLUMNFLAGS_ISNULLABLE = 0x20
DBCOLUMNFLAGS_MAYBENULL = 0x40
DBCOLUMNFLAGS_ISLONG = 0x80
DBCOLUMNFLAGS_ISROWID = 0x100
DBCOLUMNFLAGS_ISROWVER = 0x200
DBCOLUMNFLAGS_CACHEDEFERRED = 0x1000


def time_from_com(com_date):
    """Return a valid datetime.time from a COM date or time object."""
    hour, minute = divmod(86400 * (float(com_date) % 1), 3600)
    minute, second = divmod(minute, 60)
    # Must do both int() and round() or we'll be up to 1 second off.
    hour = int(round(hour))
    minute = int(round(minute))
    second = int(round(second))
    
    while second > 59:
        second -= 60
        minute += 1
    while second < 0:
        second += 60
        minute -= 1
    while minute > 59:
        minute -= 60
        hour += 1
    while minute < 0:
        minute += 60
        hour -= 1
    while hour > 23:
        hour -= 24
        day += 1
    while hour < 0:
        hour += 24
    
    return datetime.time(hour, minute, second)


class AdapterFromADO(db.AdapterFromDB):
    """Coerce incoming values from ADO to Dejavu datatypes."""
    
    encoding = 'ISO-8859-1'
    
    def coerce_any_to_datetime_datetime(self, value):
        # Illegal Date/Time values will crash the
        # app when using value.Format(). Therefore,
        # grab the value and figure the date ourselves.
        # Use 1-second resolution only.
        if isinstance(value, basestring):
            if value:
                try:
                    return datetime.datetime(int(value[0:4]), int(value[4:6]),
                                             int(value[6:8]))
                except Exception:
                    raise ValueError("'%s' %s" % (value, type(value)))
            else:
                return None
        else:
            # For some reason, we need both float and int.
            aDate = datetime.date.fromordinal(int(float(value)) + zeroHour)
            return datetime.datetime.combine(aDate, time_from_com(value))
    
    def coerce_any_to_datetime_date(self, value):
        # See coerce_any_to_datetime
        if isinstance(value, basestring):
            if value:
                try:
                    return datetime.date(int(value[0:4]), int(value[4:6]),
                                         int(value[6:8]))
                except Exception:
                    raise ValueError("'%s' %s" % (value, type(value)))
            else:
                return None
        else:
            return datetime.date.fromordinal(int(float(value)) + zeroHour)
    
    def coerce_any_to_datetime_time(self, value):
        # See coerce_any_to_datetime
        return time_from_com(value)
    
    def coerce_any_to_decimal_Decimal(self, value):
        # pywin32 build 205 began support for returning
        # COM Currency objects as decimal objects.
        # See http://pywin32.cvs.sourceforge.net/pywin32/pywin32/CHANGES.txt?view=markup
        if not isinstance(value, db.decimal.Decimal):
            value = str(value)
            value = db.decimal.Decimal(value)
        return value
    
    def coerce_CURRENCY_to_float(self, value):
        if isinstance(value, tuple):
            # See http://groups.google.com/group/comp.lang.python/
            #           browse_frm/thread/fed03c64735c9e9c
            value = map(long, value)
            return ((value[1] & 0xFFFFFFFFL) | (value[0] << 32)) / 1e4
        return float(value)
    
    def coerce_CURRENCY_to_decimal_Decimal(self, value):
        # pywin32 build 205 began support for returning
        # COM Currency objects as decimal objects.
        # See http://pywin32.cvs.sourceforge.net/pywin32/pywin32/CHANGES.txt?view=markup
        if not isinstance(value, db.decimal.Decimal):
            # See http://groups.google.com/group/comp.lang.python/
            #           browse_frm/thread/fed03c64735c9e9c
            value = map(long, value)
            value = (value[1] & 0xFFFFFFFFL) | (value[0] << 32)
            return db.decimal.Decimal(value) / 10000
        return value
    
    def coerce_CURRENCY_to_fixedpoint_FixedPoint(self, value):
        if isinstance(value, db.decimal.Decimal):
            value = str(value)
            scale = 0
            atoms = value.rsplit(".", 1)
            if len(atoms) > 1:
                scale = len(atoms[-1])
            return db.fixedpoint.FixedPoint(value, scale)
        else:
            # See http://groups.google.com/group/comp.lang.python/
            #           browse_frm/thread/fed03c64735c9e9c
            value = map(long, value)
            value = (value[1] & 0xFFFFFFFFL) | (value[0] << 32)
            return db.fixedpoint.FixedPoint(value, 4) / 1e4
    
    def coerce_any_to_unicode(self, value):
        if isinstance(value, unicode):
            # For some reason, value is already a unicode object.
            return value
        
        if isinstance(value, (basestring, buffer)):
            try:
                return unicode(value, self.encoding)
            except UnicodeError, exc:
                exc.args += (type(value),)
        return unicode(value)



class ADOSQLDecompiler(db.SQLDecompiler):
    
    def visit_COMPARE_OP(self, lo, hi):
        op2, op1 = self.stack.pop(), self.stack.pop()
        if op1 is db.cannot_represent or op2 is db.cannot_represent:
            self.stack.append(db.cannot_represent)
            return
        
        op = lo + (hi << 8)
        if op in (6, 7):     # in, not in
            # Looking for text in a field. Use Like (reverse terms).
            # LIKE is case-insensitive in MS SQL Server (and there
            # doesn't seem to be a way around it). Use icontainedby
            # and just mark imperfect.
            value = self.dejavu_icontainedby(op1, op2)
            if op == 7:
                value = "NOT " + value
            self.stack.append(value)
            self.imperfect = True
        elif op1 == 'NULL':
            if op in (2, 8):    # '==', is
                self.stack.append(op2 + " IS NULL")
            elif op in (3, 9):  # '!=', 'is not'
                self.stack.append(op2 + " IS NOT NULL")
            else:
                raise ValueError("Non-equality Null comparisons not allowed.")
        elif op2 == 'NULL':
            if op in (2, 8):    # '==', 'is'
                self.stack.append(op1 + " IS NULL")
            elif op in (3, 9):  # '!=', 'is not'
                self.stack.append(op1 + " IS NOT NULL")
            else:
                raise ValueError("Non-equality Null comparisons not allowed.")
        else:
            if (isinstance(op2, db.ConstWrapper)
                and isinstance(op2.basevalue, basestring)):
                atom = self._compare_strings(op1, op, op2)
                if atom:
                    self.stack.append(atom)
                    return
            self.stack.append(op1 + " " + self.sql_cmp_op[op] + " " + op2)
    
    def _compare_strings(self, op1, op, op2):
        # ADO comparison operators for strings are case-insensitive
        # by default. Rather than determine which columns in the DB
        # might be case-sensitive, just flag them all as imperfect.
        # TODO: might be possible to cast both to varbinary, but
        # that may cause problems with unicode columns.
        self.imperfect = True
    
    
    # --------------------------- Dispatchees --------------------------- #
    
    def attr_startswith(self, tos, arg):
        self.imperfect = True
        return tos + " LIKE '" + self.adapter.escape_like(arg) + "%'"
    
    def attr_endswith(self, tos, arg):
        self.imperfect = True
        return tos + " LIKE '%" + self.adapter.escape_like(arg) + "'"
    
    def containedby(self, op1, op2):
        self.imperfect = True
        if isinstance(op1, ConstWrapper):
            # Looking for text in a field. Use Like (reverse terms).
            return op2 + " LIKE '%" + self.adapter.escape_like(op1) + "%'"
        else:
            # Looking for field in (a, b, c)
            atoms = [self.adapter.coerce(x) for x in op2.basevalue]
            if atoms:
                return op1 + " IN (" + ", ".join(atoms) + ")"
            else:
                # Nothing will match the empty list, so return none.
                return self.adapter.bool_false
    
    def dejavu_icontainedby(self, op1, op2):
        if isinstance(op1, db.ConstWrapper):
            # Looking for text in a field. Use Like (reverse terms).
            # LIKE is already case-insensitive in MS SQL Server;
            # so don't use LOWER().
            value = op2 + " LIKE '%" + self.adapter.escape_like(op1) + "%'"
        else:
            # Looking for field in (a, b, c)
            atoms = [self.adapter.coerce(x) for x in op2.basevalue]
            if atoms:
                return op1 + " IN (" + ", ".join(atoms) + ")"
            else:
                # Nothing will match the empty list, so return none.
                return self.adapter.bool_false
        return value
    
    def dejavu_istartswith(self, x, y):
        # Like is already case-insensitive in ADO; so don't use LOWER().
        return x + " LIKE '" + self.adapter.escape_like(y) + "%'"
    
    def dejavu_iendswith(self, x, y):
        # Like is already case-insensitive in ADO; so don't use LOWER().
        return x + " LIKE '%" + self.adapter.escape_like(y) + "'"
    
    def dejavu_ieq(self, x, y):
        # = is already case-insensitive in ADO.
        return x + " = " + y
    
    def dejavu_now(self):
        return "getdate()"
    
    def dejavu_today(self):
        return "DATEADD(dd, DATEDIFF(dd,0,getdate()), 0)"
    
    def dejavu_year(self, x):
        return "DATEPART(year, " + x + ")"
    
    def dejavu_month(self, x):
        return "DATEPART(month, " + x + ")"
    
    def dejavu_day(self, x):
        return "DATEPART(day, " + x + ")"
    
    def func__builtin___len(self, x):
        return "Len(" + x + ")"


class ADOTable(db.Table):
    
    def _add_column(self, column):
        """Internal function to add the column to the database."""
        coldef = self.db.col_def(column)
        # SQL Server doesn't use the "COLUMN" keyword with "ADD"
        self.db.execute("ALTER TABLE %s ADD %s;" % (self.qname, coldef))
    
    def _rename(self, oldcol, newcol):
        conn = self.db.connection()
        try:
            cat = win32com.client.Dispatch(r'ADOX.Catalog')
            cat.ActiveConnection = conn
            cat.Tables(self.name).Columns(oldcol.name).Name = newcol.name
        finally:
            conn = None
            cat = None


def connatoms(connstring):
    atoms = {}
    for pair in connstring.split(";"):
        if pair:
            k, v = pair.split("=", 1)
            atoms[k.upper().strip()] = v.strip()
    return atoms


class ADODatabase(db.Database):
    
    decompiler = ADOSQLDecompiler
    adapterfromdb = AdapterFromADO()
    tableclass = ADOTable
    
    # the amount of time to try to close the db connection
    # before raising an exception
    shutdowntimeout = 1 # sec.
    
    
    #                              Discovery                              #
    
    def _get_tables(self, conn=None):
        # cols will be
        # [(u'TABLE_CATALOG', 202), (u'TABLE_SCHEMA', 202), (u'TABLE_NAME', 202),
        # (u'TABLE_TYPE', 202), (u'TABLE_GUID', 72), (u'DESCRIPTION', 203),
        # (u'TABLE_PROPID', 19), (u'DATE_CREATED', 7), (u'DATE_MODIFIED', 7)]
        data, _ = self.fetch(adSchemaTables, conn=conn, schema=True)
        return [self.tableclass(str(row[2]), self.quote(str(row[2])), self)
                for row in data
                # Ignore linked and system tables
                if row[3] == "TABLE"]
    
    def _get_table(self, tablename, conn=None):
        # cols will be
        # [(u'TABLE_CATALOG', 202), (u'TABLE_SCHEMA', 202), (u'TABLE_NAME', 202),
        # (u'TABLE_TYPE', 202), (u'TABLE_GUID', 72), (u'DESCRIPTION', 203),
        # (u'TABLE_PROPID', 19), (u'DATE_CREATED', 7), (u'DATE_MODIFIED', 7)]
        data, _ = self.fetch(adSchemaTables, conn=conn, schema=True)
        for row in data:
            name = str(row[2])
            if name == tablename:
                return self.tableclass(name, self.quote(name), self)
        raise errors.MappingError(tablename)
    
    def _get_columns(self, tablename, conn=None):
        # For some reason, adSchemaPrimaryKeys would only return a single
        # record for a PK that had multiple columns. Use adSchemaIndexes.
        # coldefs will be:
        # [(u'TABLE_CATALOG', 202), (u'TABLE_SCHEMA', 202), (u'TABLE_NAME', 202),
        # (u'INDEX_CATALOG', 202), (u'INDEX_SCHEMA', 202), (u'INDEX_NAME', 202),
        # (u'PRIMARY_KEY', 11), (u'UNIQUE', 11), (u'CLUSTERED', 11), (u'TYPE', 18),
        # (u'FILL_FACTOR', 3), (u'INITIAL_SIZE', 3), (u'NULLS', 3),
        # (u'SORT_BOOKMARKS', 11), (u'AUTO_UPDATE', 11), (u'NULL_COLLATION', 3),
        # (u'ORDINAL_POSITION', 19), (u'COLUMN_NAME', 202), (u'COLUMN_GUID', 72),
        # (u'COLUMN_PROPID', 19), (u'COLLATION', 2), (u'CARDINALITY', 21),
        # (u'PAGES', 3), (u'FILTER_CONDITION', 202), (u'INTEGRATED', 11)]
        data, _ = self.fetch(adSchemaIndexes, conn=conn, schema=True)
        pknames = [row[17] for row in data
                   if (tablename == row[2]) and row[6]]
        
        # columns will be
        # [(u'TABLE_CATALOG', 202), (u'TABLE_SCHEMA', 202), (u'TABLE_NAME', 202),
        # (u'COLUMN_NAME', 202), (u'COLUMN_GUID', 72), (u'COLUMN_PROPID', 19),
        # (u'ORDINAL_POSITION', 19), (u'COLUMN_HASDEFAULT', 11),
        # (u'COLUMN_DEFAULT', 203), (u'COLUMN_FLAGS', 19), (u'IS_NULLABLE', 11),
        # (u'DATA_TYPE', 18), (u'TYPE_GUID', 72), (u'CHARACTER_MAXIMUM_LENGTH', 19),
        # (u'CHARACTER_OCTET_LENGTH', 19), (u'NUMERIC_PRECISION', 18),
        # (u'NUMERIC_SCALE', 2), (u'DATETIME_PRECISION', 19),
        # (u'CHARACTER_SET_CATALOG', 202), (u'CHARACTER_SET_SCHEMA', 202),
        # (u'CHARACTER_SET_NAME', 202), (u'COLLATION_CATALOG', 202),
        # (u'COLLATION_SCHEMA', 202), (u'COLLATION_NAME', 202),
        # (u'DOMAIN_CATALOG', 202), (u'DOMAIN_SCHEMA', 202),
        # (u'DOMAIN_NAME', 202), (u'DESCRIPTION', 203)]
        data, _ = self.fetch(adSchemaColumns, conn=conn, schema=True)
        
        cols = []
        for row in data:
            # I tried passing criteria to OpenSchema, but passing None is
            # not the same as passing pythoncom.Empty (which errors).
            if row[2] != tablename:
                continue
            
            dbtype = dbtypes[row[11]]
            default = row[8]
            if default is not None:
                deftype = self.python_type(dbtype)
                if issubclass(deftype, (int, long)):
                    # We may have stuck extraneous quotes in the default
                    # value when using numeric defaults with MSAccess.
                    if default.startswith("'") and default.endswith("'"):
                        default = default[1:-1]
                default = deftype(default)
            
            name = str(row[3])
            c = db.Column(name, self.quote(name), dbtype, default,
                          key=(name in pknames))
            
            # This only works for SQL Server. The MSAccessDatabase will
            # wrap this method and override autoincrement.
            colflags = int(row[9])
            if ((colflags & DBCOLUMNFLAGS_ISFIXEDLENGTH)
                and not (colflags & DBCOLUMNFLAGS_WRITE)):
                c.autoincrement = True
            
            if dbtype in ("SMALLINT", "INTEGER", "TINYINT",
                          "UNSIGNEDTINYINT", "UNSIGNEDSMALLINT",
                          "UNSIGNEDINT", "BIGINT", "UNSIGNEDBIGINT"):
                c.hints['bytes'] = row[15]
            elif dbtype in ("SINGLE", "DOUBLE"):
                c.hints['precision'] = row[15]
                c.hints['scale'] = row[16]
            elif dbtype == "CURRENCY":
                # CURRENCY allows 15 places to the left of the decimal point,
                # and 4 places to the right.
                c.hints['precision'] = 19
                c.hints['scale'] = 4
            elif dbtype in ("DECIMAL", "NUMERIC"):
                c.hints['precision'] = row[15]
                c.hints['scale'] = row[16]
                c.dbtype = "%s(%s, %s)" % (dbtype, row[15], row[16])
            elif dbtype in ("BSTR", "VARIANT", "BINARY", "CHAR",
                            "VARCHAR", "VARBINARY", "WCHAR", "VARWCHAR"):
                if row[13]:
                    # row[13] will be a float
                    c.hints['bytes'] = b = int(row[13])
                else:
                    # I'm kinda guessing on this. If we use "MEMO" in an
                    # MSAccess CREATE statement, it comes back as "WCHAR",
                    # and seems to support over 65536 bytes.
                    c.hints['bytes'] = b = (2 ** 31) - 1
                c.dbtype = "%s(%s)" % (c.dbtype, b)
            elif dbtype in ("LONGVARCHAR", "LONGVARBINARY", "LONGVARWCHAR"):
                if row[13]:
                    # row[13] will be a float
                    c.hints['bytes'] = b = int(row[13])
                    c.dbtype = "%s(%s)" % (c.dbtype, b)
                else:
                    c.hints['bytes'] = 65535
            
            cols.append(c)
        return cols
    
    def _get_indices(self, tablename=None, conn=None):
        # cols will be
        # [(u'TABLE_CATALOG', 202), (u'TABLE_SCHEMA', 202), (u'TABLE_NAME', 202),
        # (u'INDEX_CATALOG', 202), (u'INDEX_SCHEMA', 202), (u'INDEX_NAME', 202),
        # (u'PRIMARY_KEY', 11), (u'UNIQUE', 11), (u'CLUSTERED', 11), (u'TYPE', 18),
        # (u'FILL_FACTOR', 3), (u'INITIAL_SIZE', 3), (u'NULLS', 3),
        # (u'SORT_BOOKMARKS', 11), (u'AUTO_UPDATE', 11), (u'NULL_COLLATION', 3),
        # (u'ORDINAL_POSITION', 19), (u'COLUMN_NAME', 202), (u'COLUMN_GUID', 72),
        # (u'COLUMN_PROPID', 19), (u'COLLATION', 2), (u'CARDINALITY', 21),
        # (u'PAGES', 3), (u'FILTER_CONDITION', 202), (u'INTEGRATED', 11)]
        data, _ = self.fetch(adSchemaIndexes, conn=conn, schema=True)
        indices = []
        for row in data:
            # I tried passing criteria to OpenSchema, but passing None is
            # not the same as passing pythoncom.Empty (which errors).
            if tablename and row[2] != tablename:
                continue
            i = db.Index(row[5], self.quote(row[5]), row[2], row[17], row[7])
            indices.append(i)
        return indices
    
    def python_type(self, dbtype):
        """Return a Python type which can store values of the given dbtype."""
        if dbtype in ("DATE", "DBDATE"):
            return datetime.date
        elif dbtype == "DBTIME":
            return datetime.time
        elif dbtype in ("DATETIME", "DBTIMESTAMP"):
            return datetime.datetime
        elif dbtype in ("SMALLINT", "INTEGER", "TINYINT",
                        "UNSIGNEDTINYINT", "UNSIGNEDSMALLINT",
                        "UNSIGNEDINT"):
            return int
        elif dbtype in ("BIT", "BOOLEAN"):
            return bool
        elif dbtype in ("BIGINT", "UNSIGNEDBIGINT", "LONG"):
            return long
        elif dbtype in ("SINGLE", "DOUBLE", "DOUBLE PRECISION", "REAL"):
            return float
        
        for t in ("DECIMAL", "NUMERIC", "CURRENCY"):
            if dbtype.startswith(t):
                if db.decimal:
                    return db.decimal.Decimal
                elif db.fixedpoint:
                    return db.fixedpoint.FixedPoint
        
        for t in ("BSTR", "VARIANT", "BINARY", "CHAR", "MEMO", "TEXT",
                  "VARCHAR", "LONGVARCHAR", "VARBINARY", "LONGVARBINARY"):
            if dbtype.startswith(t):
                return str
        
        for t in ("WCHAR", "VARWCHAR", "LONGVARWCHAR"):
            if dbtype.startswith(t):
                return unicode
        
        raise TypeError("Database type %r could not be converted "
                        "to a Python type." % dbtype)
    
    
    #                              Container                              #
    
    def _rename(self, oldtable, newtable):
        conn = self.connection()
        try:
            cat = win32com.client.Dispatch(r'ADOX.Catalog')
            cat.ActiveConnection = conn
            cat.Tables(oldtable.name).Name = newtable.name
        finally:
            conn = None
            cat = None
    
    #                               Naming                                #
    
    def quote(self, name):
        """Return name, quoted for use in an SQL statement."""
        return '[' + name + ']'
    
    #                             Connecting                              #
    
    ConnectionTimeout = None
    CommandTimeout = None
    
    def _get_conn(self):
        conn = win32com.client.Dispatch(r'ADODB.Connection')
        conn.Open(self.Connect)
        if self.ConnectionTimeout is not None:
            conn.ConnectionTimeout = self.ConnectionTimeout
        if self.CommandTimeout is not None:
            conn.CommandTimeout = self.CommandTimeout
        return conn
    
    def _del_conn(self, conn):
        for trial in xrange(self.shutdowntimeout * 10):
            try:
                # This may raise "Operation cannot be performed
                # while executing asynchronously"
                # if a prior operation has not yet completed.
                conn.Close()
                return
            except pywintypes.com_error, e:
                try:
                    ecode = e.args[2][-1]
                except IndexError:
                    ecode = None
                if ecode == -2146824577:
                    # "Operation cannot be performed while executing asynchronously"
                    # Try again...
                    time.sleep(0.1)
                    continue
                raise
    
    def execute(self, query, conn=None):
        if conn is None:
            conn = self.connection()
        if isinstance(query, unicode):
            query = query.encode(self.adaptertosql.encoding)
        
        self.log(query)
        try:
            if isinstance(conn, db.ConnectionWrapper):
                # 'conn' is a ConnectionWrapper object, which .Open
                # won't accept. Pass the unwrapped connection instead.
                conn = conn.conn
            
            # Call Execute directly, skipping win32com overhead.
            conn._oleobj_.InvokeTypes(6, 0, 1, (9, 0),
                                      ((8, 1), (16396, 18), (3, 49)),
                                      query, pythoncom.Missing, -1)
        except pywintypes.com_error, x:
            x.args += (query, )
            conn = None
            raise
    
    def fetch(self, query, conn=None, schema=False):
        """fetch(query, conn=None) -> rowdata, columns."""
        if conn is None:
            conn = self.connection()
        
        try:
            if schema:
                # Call OpenSchema(query) directly, skipping win32com overhead.
                res = conn._oleobj_.InvokeTypes(19, 0, 1, (9, 0),
                                                ((3, 1), (12, 17), (12, 17)),
                                                query, Empty, Empty)
            else:
                self.log(query)
                if isinstance(conn, db.ConnectionWrapper):
                    # 'conn' is a ConnectionWrapper object, which .Open
                    # won't accept. Pass the unwrapped connection instead.
                    conn = conn.conn
                
                # Call conn.Open(query) directly, skipping win32com overhead.
                res, rows_affected = conn._oleobj_.InvokeTypes(6, 0, 1, (9, 0),
                                                ((8, 1), (16396, 18), (3, 49)),
                                                # *args =
                                                query, pythoncom.Missing, -1)
        except pywintypes.com_error, x:
            try:
                # Close
                res.InvokeTypes(*Recordset_Close)
            except:
                pass
            res = None
            x.args += (query, )
            conn = None
            # "raise x" here or we could get the traceback of the inner try.
            raise x
        
        # Using xrange(Count) is slightly faster than "for x in resFields".
        resFields = res.InvokeTypes(*Recordset_Fields)
        fieldcount = resFields.InvokeTypes(*Fields_Count)
        columns = []
        for i in xrange(fieldcount):
            # Wow. Calling this directly (instead of resFields(i))
            # results in a 29% speedup for a 1-row fetch() of 48 fields.
            x = resFields.InvokeTypes(0, 0, 2, (9, 0), ((12, 1),), i)
            
            # Wow. Calling these directly (instead of x.Name, x.Type)
            # results in a 40% speedup for a 1-row fetch() of 48 fields.
            name = x.InvokeTypes(*Field_Name)
            typ = x.InvokeTypes(*Field_Type)
            columns.append((name, typ))
        
        data = []
        if not (res.InvokeTypes(*BOF) and res.InvokeTypes(*EOF)):
            # We tried .MoveNext() and lots of Fields.Item() calls.
            # Using GetRows() beats that time by about 2/3.
            # Inlining GetRows results in a 14% speedup for fetch().
            data = res.InvokeTypes(*Recordset_GetRows)
            
            # Convert cols x rows -> rows x cols
            data = zip(*data)
        try:
            # Close
            res.InvokeTypes(*Recordset_Close)
        except:
            pass
        conn = None
        
        return data, columns
    
    
    #                            Transactions                             #
    
    def start(self, isolation=None):
        """Start a transaction. Not needed if self.implicit_trans is True."""
        conn = self.get_transaction(new=True)
        self.execute("BEGIN TRANSACTION;", conn)
        self.isolate(conn, isolation)


class StorageManagerADO(db.StorageManagerDB):
    """StoreManager to save and retrieve Units via ADO 2.7.
    
    You must run makepy on ADO 2.7 before installing.
    """
    
    databaseclass = ADODatabase



###########################################################################
##                                                                       ##
##                             SQL Server                                ##
##                                                                       ##
###########################################################################


class ADOSQLDecompiler_SQLServer(ADOSQLDecompiler):
    
    def _compare_strings(self, op1, op, op2):
        # ADO comparison operators for strings are case-insensitive.
        if op < 6:
            # ('<', '<=', '==', '!=', '>', '>=')
            # Some operations on strings can be emulated with the
            # Convert function.
            return ("Convert(binary, %s) %s Convert(binary, %s)" %
                    (op1, self.sql_cmp_op[op], op2))
        else:
            return ADOSQLDecompiler._compare_strings(self, op1, op, op2)


class AdapterToADOSQL_SQLServer(db.AdapterToSQL):
    
    encoding = 'ISO-8859-1'
    
    escapes = [("'", "''")]
    like_escapes = [("[", "[[]"), ("%", "[%]"), ("_", "[_]"),
                    ("?", "[?]"), ("#", "[#]")]
    
    # These are not the same as coerce_bool_to_any (which is used on one side of 
    # a comparison). Instead, these are used when the whole (sub)expression
    # is True or False, e.g. "WHERE TRUE", or "WHERE TRUE and 'a'.'b' = 3".
    bool_true = "(1=1)"
    bool_false = "(1=0)"
    
    def coerce_bool_to_any(self, value):
        if value:
            return '1'
        return '0'


class TypeAdapter_SQLServer(db.TypeAdapter):
    
    # Hm. Docs say 38, but I can't seem to get more than 12 working.
    # They must mean 38 binary digits; math.log(2 ** 38, 10) = 11.4+
    numeric_max_precision = 12
    numeric_max_bytes = 6
    
    def coerce_bool(self, col):
        return "BIT"
    
    def coerce_datetime_datetime(self, col):
        return "DATETIME"
    
    def coerce_datetime_date(self, col):
        return "DATETIME"
    
    def coerce_datetime_time(self, col):
        return "DATETIME"
    
    def int_type(self, bytes):
        """Return a datatype which can handle the given number of bytes."""
        if bytes <= 2:
            return "SMALLINT"
        elif bytes <= 4:
            return "INTEGER"
        elif bytes <= 8:
            # BIGINT is usually 8 bytes
            return "BIGINT"
        else:
            # Anything larger than 8 bytes, use decimal/numeric.
            return "NUMERIC(%s, 0)" % (bytes * 2)
    
    def coerce_str(self, col):
        # The bytes hint does not reflect the usual 4-byte base for varchar.
        bytes = int(col.hints.get('bytes', 255))
        
        if bytes == 0 or bytes > 8000:
            # Okay, what the @#$%& is wrong with Redmond??!?! We can't even
            # compare TEXT or NTEXT fields??!? Fine. We'll deny such, and
            # warn the deployer with less swearing and exclamation points.
            warnings.warn("You have defined a string property without "
                          "limiting its length. Microsoft SQL Server does "
                          "not allow comparisons on string fields larger "
                          "than 8000 characters. Some of your data may be "
                          "truncated.", errors.StorageWarning)
            bytes = 8000
        
        # 8000 *bytes* is the absolute upper limit, based on T_SQL docs for
        # varchar/varbinary. If there are further fields defined for the
        # class, or the codepage uses a double-byte character set, we still
        # might exceed the max size (8060) for a record. We could calc the
        # total requested record size, and adjust accordingly. Meh.
        return "VARCHAR(%s)" % bytes


class SQLServerTable(ADOTable):
    
    def _rename(self, oldcol, newcol):
        self.db.execute("EXEC sp_rename '%s.%s', '%s', 'COLUMN'" %
                        (self.name, oldcol.name, newcol.name))


class SQLServerDatabase(ADODatabase):
    
    decompiler = ADOSQLDecompiler_SQLServer
    tableclass = SQLServerTable
    adaptertosql = AdapterToADOSQL_SQLServer()
    typeadapter = TypeAdapter_SQLServer()
    
    def _template_conn(self):
        adoconn = win32com.client.Dispatch(r'ADODB.Connection')
        atoms = connatoms(self.Connect)
        atoms['INITIAL CATALOG'] = "tempdb"
        adoconn.Open("; ".join(["%s=%s" % (k, v) for k, v in atoms.iteritems()]))
        return adoconn
    
    def create_database(self):
        self.lock("Creating database. Transactions not allowed.")
        try:
            adoconn = self._template_conn()
            adoconn.Execute("CREATE DATABASE %s" % self.qname)
            adoconn.Close()
            self.clear()
        finally:
            self.unlock()
    
    def drop_database(self):
        self.lock("Dropping database. Transactions not allowed.")
        try:
            # Must shut down all connections to avoid
            # "being accessed by other users" error.
            self.connection.shutdown()
            
            adoconn = self._template_conn()
            adoconn.Execute("DROP DATABASE %s;" % self.qname)
            adoconn.Close()
            self.clear()
        finally:
            self.unlock()
    
    def col_def(self, column):
        """Return a clause for the given column for CREATE or ALTER TABLE.
        
        This will be of the form:
            name type [DEFAULT x|IDENTITY(initial, 1) NOT NULL]
        """
        dbtype = column.dbtype
        
        clause = ""
        if column.autoincrement:
            if dbtype not in ("BOOLEAN", "SMALLINT", "INTEGER", "BIGINT"):
                raise ValueError("SQL Server does not allow IDENTITY "
                                 "columns of type %r" % dbtype)
            clause = " IDENTITY(%s, 1) NOT NULL" % column.initial
        else:
            # SQL Server does not allow a column to have
            # both an IDENTITY clause and a DEFAULT clause.
            default = column.default or ""
            if default:
                clause = self.adaptertosql.coerce(default, dbtype)
                clause = " DEFAULT %s" % clause
        
        return '%s %s%s' % (column.qname, dbtype, clause)
    
    #                            Transactions                             #
    
    default_isolation = "READ COMMITTED"
    
    def is_lock_error(self, exc):
        """If the given exception instance is a lock timeout, return True.
        
        This should return True for errors which arise from transaction
        locking timeouts; for example, if the database prevents 'dirty
        reads' by raising an error.
        """
        # com_error: (-2147352567, 'Exception occurred.',
        #   (0, 'Microsoft OLE DB Provider for SQL Server',
        #    'Timeout expired', None, 0, -2147217871), None,
        #    "UPDATE [testVet] SET [City] = 'Tehachapi' ... ;")
        if not isinstance(exc, pywintypes.com_error):
            return False
        return exc.args[2][5] == -2147217871


class StorageManagerADO_SQLServer(StorageManagerADO):
    
    databaseclass = SQLServerDatabase
    
    def __init__(self, arena, allOptions={}):
        atoms = connatoms(allOptions['Connect'])
        allOptions['name'] = atoms.get('INITIAL CATALOG') or atoms.get('DSN')
        db.StorageManagerDB.__init__(self, arena, allOptions)
        
        if "2005" in self.version():
            self.db.isolation_levels.append("SNAPSHOT")
    
    def version(self):
        adoconn = self.db._template_conn()
        adov = adoconn.Version
        data, coldefs = self.db.fetch("SELECT @@VERSION;", adoconn)
        sqlv, = data[0]
        adoconn.Close()
        del adoconn
        return "ADO Version: %s\n%s" % (adov, sqlv)
    
    def _seq_UnitSequencerInteger(self, unit):
        """Reserve a unit using the table's AUTOINCREMENT field."""
        cls = unit.__class__
        t = self.db[cls.__name__]
        
        fields = []
        values = []
        for key in cls.properties:
            col = t[key]
            if col.autoincrement:
                # Skip this field, since we're using IDENTITY
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
        # For some reason, using SCOPE_IDENTITY or IDENTITY failed (returned
        # None) when retrieving ID's just after a 99-thread-test ran. Moving
        # the multithreading test fixed it. IDENT_CURRENT worked regardless.
        data, _ = self.db.fetch("SELECT IDENT_CURRENT('%s');" % t.qname,
                                transconn)
        setattr(unit, cls.identifiers[0], data[0][0])



###########################################################################
##                                                                       ##
##                             MS Access                                 ##
##                                                                       ##
###########################################################################


class ADOSQLDecompiler_MSAccess(ADOSQLDecompiler):
    sql_cmp_op = ('<', '<=', '=', '<>', '>', '>=', 'in', 'not in')
    
    def _compare_strings(self, op1, op, op2):
        # ADO comparison operators for strings are case-insensitive.
        if op < 6:
            # ('<', '<=', '==', '!=', '>', '>=')
            # Some operations on strings can be emulated with the
            # StrComp function. Oddly enough, "StrComp(x, y) op 0"
            # is the same as "x op y" in most cases.
            return "StrComp(%s, %s) %s 0" % (op1, op2, self.sql_cmp_op[op])
        else:
            return ADOSQLDecompiler._compare_strings(self, op1, op, op2)
    
    def dejavu_now(self):
        return "Now()"
    
    def dejavu_today(self):
        return "DateValue(Now())"
    
    def dejavu_year(self, x):
        return "Year(" + x + ")"
    
    def dejavu_month(self, x):
        return "Month(" + x + ")"
    
    def dejavu_day(self, x):
        return "Day(" + x + ")"


class TypeAdapter_MSAccess(db.TypeAdapter):
    # http://msdn2.microsoft.com/en-us/library/ms714540.aspx
    # http://office.microsoft.com/en-us/access/HP010322481033.aspx
    
    # Hm. Docs say 28/38, but I can't seem to get more than 12 working.
    numeric_max_precision = 12
    numeric_max_bytes = 6
    
    def coerce_bool(self, col): return "BIT"
    
    def coerce_datetime_datetime(self, col): return "DATETIME"
    def coerce_datetime_date(self, col): return "DATETIME"
    def coerce_datetime_time(self, col): return "DATETIME"
    
    def int_type(self, bytes):
        if bytes <= 2:
            return "INTEGER"
        elif bytes <= 4:
            return "LONG"
        else:
            # Anything larger than 4 bytes, use decimal/numeric.
            return "DECIMAL"
    
    def coerce_str(self, col):
        # The bytes hint shall not reflect the usual 4-byte base for varchar.
        bytes = int(col.hints.get('bytes', 255))
        
        # 255 chars is the upper limit for TEXT / VARCHAR in MS Access.
        if bytes == 0 or bytes > 255:
            # MEMO is 1 GB max when set programatically (only 64K when set
            # in Access UI). But then, 1 GB is the limit for the whole DB.
            # Note that OpenSchema will return a DATA_TYPE of "WCHAR".
            return "MEMO"
        
        return "VARCHAR(%s)" % bytes



class AdapterToADOSQL_MSAccess(db.AdapterToSQL):
    """Coerce Expression constants to ADO SQL."""
    
    encoding = 'ISO-8859-1'
    
    escapes = [("'", "''")]
    like_escapes = [("[", "[[]"), ("%", "[%]"), ("_", "[_]"),
                    ("?", "[?]"), ("#", "[#]")]
    
    def coerce_datetime_datetime_to_any(self, value):
        return ('#%s/%s/%s %02d:%02d:%02d#' %
                (value.month, value.day, value.year,
                 value.hour, value.minute, value.second))
    
    def coerce_datetime_date_to_any(self, value):
        return '#%s/%s/%s#' % (value.month, value.day, value.year)
    
    def coerce_datetime_time_to_any(self, value):
        return '#%02d:%02d:%02d#' % (value.hour, value.minute, value.second)


class MSAccessDatabase(ADODatabase):
    
    decompiler = ADOSQLDecompiler_MSAccess
    adaptertosql = AdapterToADOSQL_MSAccess()
    typeadapter = TypeAdapter_MSAccess()
    
    def version(self):
        adoconn = win32com.client.Dispatch(r'ADODB.Connection')
        v = adoconn.Version
        del adoconn
        return "ADO Version: %s" % v
    
    def _get_columns(self, tablename, conn=None):
        cols = ADODatabase._get_columns(self, tablename, conn)
        if conn is None:
            conn = self.connection()
        
        try:
            # Horrible hack to get autoincrement property
            query = "SELECT * FROM %s WHERE FALSE" % self.quote(tablename)
            if isinstance(conn, db.ConnectionWrapper):
                # 'conn' is a ConnectionWrapper object, which .Open
                # won't accept. Pass the unwrapped connection instead.
                conn = conn.conn
            
            # Call conn.Open(query) directly, skipping win32com overhead.
            res, rows_affected = conn._oleobj_.InvokeTypes(6, 0, 1, (9, 0),
                                            ((8, 1), (16396, 18), (3, 49)),
                                            # *args =
                                            query, pythoncom.Missing, -1)
        except pywintypes.com_error, x:
            try:
                res.InvokeTypes(*Recordset_Close)
            except:
                pass
            res = None
            x.args += (query, )
            conn = None
            
            try:
                if "no read permission" in x.args[2][2]:
                    conn = None
                    return []
            except IndexError:
                pass
            
            # "raise x" here or we could get the traceback of the inner try.
            raise x
        
        resFields = res.InvokeTypes(*Recordset_Fields)
        for c in cols:
            f = resFields.InvokeTypes(0, 0, 2, (9, 0), ((12, 1),), c.name)
            fprops = f.InvokeTypes(*Field_Properties)
            fprop = fprops.InvokeTypes(0, 0, 2, (9, 0), ((12, 1), ), "ISAUTOINCREMENT")
            c.autoincrement = fprop.InvokeTypes(*Property_Value)
        
        try:
            res.InvokeTypes(*Recordset_Close)
        except:
            pass
        conn = None
        
        return cols
    
    def python_type(self, dbtype):
        if dbtype == "LONG":
            return int
        return ADODatabase.python_type(self, dbtype)
    
    def col_def(self, column):
        """Return a clause for the given column for CREATE or ALTER TABLE.
        
        This will be of the form:
            name type [DEFAULT x|AUTOINCREMENT(initial, 1)]
        """
        dbtype = column.dbtype
        
        if column.autoincrement:
            # MS Access does not allow a column to have
            # both an AUTOINCREMENT clause and a DEFAULT clause.
            # It also needs no type in this case.
            dbtype = "AUTOINCREMENT(%s, 1)" % column.initial
        else:
            default = column.default or ""
            if default:
                defspec = self.adaptertosql.coerce(default, dbtype)
                if isinstance(default, (int, long)):
                    # Crazy quote hack to get a numeric default to work.
                    defspec = "'%s'" % defspec
                dbtype = "%s DEFAULT %s" % (dbtype, defspec)
        
        return '%s %s' % (column.qname, dbtype)
    
    #                             Connecting                              #
    
    poolsize = 0
    
    def connect(self):
        # MS Access can't use a pool, because there doesn't seem
        # to be a commit timeout. See http://support.microsoft.com/kb/200300
        # for additional synchronization issues.
        self.connection = db.SingleConnection(self._get_conn, self._del_conn)
    
    def create_database(self):
        self.lock("Creating database. Transactions not allowed.")
        try:
            # By not providing an Engine Type, it defaults to 5 = Access 2000.
            cat = win32com.client.Dispatch(r'ADOX.Catalog')
            cat.Create(self.Connect)
            cat.ActiveConnection.Close()
            self.clear()
        finally:
            self.unlock()
    
    def drop_database(self):
        self.lock("Dropping database. Transactions not allowed.")
        try:
            # Must shut down our only connection to avoid
            # "Permission denied" error on os.remove call below.
            self.connection.shutdown()
            
            import os
            # This should accept relative or absolute paths
            if os.path.exists(self.name):
                os.remove(self.name)
            self.clear()
        finally:
            self.unlock()
    
    default_isolation = "READ UNCOMMITTED"
    isolation_levels = ["READ UNCOMMITTED",]
    
    def isolate(self, conn, isolation=None):
        """Set the isolation level of the given connection.
        
        If 'isolation' is None, our default_isolation will be used for new
        connections. Valid values for the 'isolation' argument may be native
        values for your particular database. However, it is recommended you
        pass items from the global 'levels' list instead; these will be
        automatically replaced with native values.
        
        For many databases, this must be executed after START TRANSACTION.
        """
        if isolation is None:
            isolation = self.default_isolation
        
        if isinstance(isolation, _isolation.IsolationLevel):
            # Map the given IsolationLevel object to a native value.
            isolation = isolation.name
            if isolation not in self.isolation_levels:
                raise ValueError("IsolationLevel %r not allowed by %s."
                                 % (isolation, self.__class__.__name__))
        
        # No action to take, since you can't actually set iso level.
        pass


class StorageManagerADO_MSAccess(StorageManagerADO):
    # Jet Connections and Recordsets are always free-threaded.
    
    use_asterisk_to_get_all = True
    databaseclass = MSAccessDatabase
    
    def __init__(self, arena, allOptions={}):
        atoms = connatoms(allOptions['Connect'])
        allOptions['name'] = (atoms.get('DATA SOURCE') or
                              atoms.get('DATA SOURCE NAME') or
                              atoms.get('DBQ'))
        db.StorageManagerDB.__init__(self, arena, allOptions)
    
    def _seq_UnitSequencerInteger(self, unit):
        """Reserve a unit using the table's AUTOINCREMENT field."""
        cls = unit.__class__
        t = self.db[cls.__name__]
        
        fields = []
        values = []
        for key in cls.properties:
            col = t[key]
            if col.autoincrement:
                # Skip this field, since we're using AUTOINCREMENT
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
        data, _ = self.db.fetch("SELECT @@IDENTITY;", transconn)
        setattr(unit, cls.identifiers[0], data[0][0])
    
    def _make_column(self, cls, key):
        col = StorageManagerADO._make_column(self, cls, key)
        if col.dbtype == "MEMO":
            for assoc in cls._associations.itervalues():
                if assoc.nearKey == key:
                    warnings.warn("Memo fields cannot be used as join keys. "
                                  "You should set %s.%s(hints={'bytes': 255})"
                                  % (cls.__name__, key), errors.StorageWarning)
        return col


def gen_py():
    """Auto generate .py support for ADO 2.7+"""
    print 'Please wait while support for ADO 2.7+ is verified...'
    
    # Microsoft ActiveX Data Objects 2.8 Library
    result = win32com.client.gencache.EnsureModule('{2A75196C-D9EB-4129-B803-931327F72D5C}', 0, 2, 8)
    if result is not None:
        return
    
    # Microsoft ActiveX Data Objects 2.7 Library
    result = win32com.client.gencache.EnsureModule('{EF53050B-882E-4776-B643-EDA472E8E3F2}', 0, 2, 7)
    if result is not None:
        return
    
    raise ImportError("ADO 2.7 support could not be imported/cached")


if __name__ == '__main__':
    gen_py()
