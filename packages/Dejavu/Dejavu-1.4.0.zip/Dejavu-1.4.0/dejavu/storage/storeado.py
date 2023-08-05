import sys
# Put COM in free-threaded mode. This first thread will have
# CoInitializeEx called automatically when pythoncom is imported.
sys.coinit_flags = 0
import pythoncom

import win32com.client
import pywintypes
import datetime

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import fixedpoint
except ImportError:
    pass

try:
    # Builtin in Python 2.5?
    decimal
except NameError:
    try:
        # Module in Python 2.3, 2.4
        import decimal
    except ImportError:
        pass

import warnings

import dejavu
from dejavu import storage, logic
from dejavu.storage import db

adOpenForwardOnly = 0
adOpenKeyset = 1
adOpenDynamic = 2
adOpenStatic = 3

adLockReadOnly = 1
adLockPessimistic = 2
adLockOptimistic = 3
adLockBatchOptimistic = 4

adSchemaColumns = 3
adSchemaTables = 20

adUseClient = 3

# 12/30/1899, the zero-Date for ADO = 693594
zeroHour = datetime.date(1899, 12, 30).toordinal()


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
    
    def coerce_datetime_datetime(self, value, coltype):
        # Illegal Date/Time values will crash the
        # app when using value.Format(). Therefore,
        # grab the value and figure the date ourselves.
        # Use 1-second resolution only.
        if isinstance(value, basestring):
            if value:
                try:
                    return datetime.datetime(int(value[0:4]), int(value[4:6]),
                                             int(value[6:8]))
                except Exception, x:
                    raise ValueError("'%s' %s" % (value, type(value)))
            else:
                return None
        else:
            # For some reason, we need both float and int.
            aDate = datetime.date.fromordinal(int(float(value)) + zeroHour)
            return datetime.datetime.combine(aDate, time_from_com(value))
    
    def coerce_datetime_date(self, value, coltype):
        # See coerce_datetime
        if isinstance(value, basestring):
            if value:
                try:
                    return datetime.date(int(value[0:4]), int(value[4:6]),
                                         int(value[6:8]))
                except Exception, x:
                    raise ValueError("'%s' %s" % (value, type(value)))
            else:
                return None
        else:
            return datetime.date.fromordinal(int(float(value)) + zeroHour)
    
    def coerce_datetime_time(self, value, coltype):
        # See coerce_datetime
        return time_from_com(value)
    
    def coerce_fixedpoint_FixedPoint(self, value, coltype):
        if coltype == 0x06:
            # Currency
            value = value[1] / 10000.0
        return fixedpoint.FixedPoint(value)
    
    def coerce_float(self, value, coltype):
        if coltype == 0x06:
            # Currency
            value = value[1] / 10000.0
        return float(value)
    
    def coerce_int(self, value, coltype):
        if coltype == 0x0b:
            # Boolean
            return value != 0
        return int(value)
    
    coerce_bool = coerce_int
    
    def coerce_unicode(self, value, coltype):
        if isinstance(value, unicode):
            # For some reason, inValue is already a unicode object.
            return value
        if isinstance(value, (basestring, buffer)):
            try:
                return unicode(value, "ISO-8859-1")
            except UnicodeError:
                raise StandardError(type(value))
        return unicode(value)



class AdapterToADOFields(storage.Adapter):
    """Coerce outgoing values from Dejavu datatypes to ADO.Field types."""
    
    def noop(self, value):
        return value
    
    def coerce_bool(self, value):
        if value:
            return True
        return False
    
    def coerce_datetime_datetime(self, value):
        if value is None:
            return None
        return self.coerce_datetime_date(value) + self.coerce_datetime_time(value)
    
    def coerce_datetime_date(self, value):
        if value is None:
            return None
        return value.toordinal() - zeroHour
    
    def coerce_datetime_time(self, value):
        if value is None:
            return None
        return ((value.second + (value.minute * 60) + (value.hour * 3600))
                / 86400.0)
    
    def do_pickle(self, value):
        # We must not use a pickle format other than 0, because binary
        # strings are not safe for all DB string fields.
        return pickle.dumps(value)
    
    coerce_dict = do_pickle
    
    def coerce_fixedpoint_FixedPoint(self, value):
        if value is None:
            return None
        return float(value)
    
    coerce_float = noop
    coerce_int = noop
    
    coerce_list = do_pickle
    
    coerce_long = noop
    coerce_str = noop
    
    coerce_tuple = do_pickle
    
    coerce_unicode = noop


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
            if op == 2:
                self.stack.append(op2 + " IS NULL")
            elif op == 3:
                self.stack.append(op2 + " IS NOT NULL")
            else:
                raise ValueError("Non-equality Null comparisons not allowed.")
        elif op2 == 'NULL':
            if op == 2:
                self.stack.append(op1 + " IS NULL")
            elif op == 3:
                self.stack.append(op1 + " IS NOT NULL")
            else:
                raise ValueError("Non-equality Null comparisons not allowed.")
        else:
            if (isinstance(op2, db.ConstWrapper)
                and isinstance(op2.basevalue, basestring)):
                # ADO comparison operators for strings are case-insensitive
                # by default. Rather than determine which columns in the DB
                # might be case-sensitive, just flag them all as imperfect.
                # TODO: might be possible to cast both to varbinary, but
                # that may cause problems with unicode columns.
                self.imperfect = True
            self.stack.append(op1 + " " + self.sql_cmp_op[op] + " " + op2)
    
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
            return op1 + " IN (" + ", ".join(atoms) + ")"
    
    def dejavu_icontainedby(self, op1, op2):
        if isinstance(op1, db.ConstWrapper):
            # Looking for text in a field. Use Like (reverse terms).
            # LIKE is already case-insensitive in MS SQL Server;
            # so don't use LOWER().
            value = op2 + " LIKE '%" + self.adapter.escape_like(op1) + "%'"
        else:
            # Looking for field in (a, b, c)
            atoms = [self.adapter.coerce(x) for x in op2.basevalue]
            value = op1 + " IN (" + ", ".join(atoms) + ")"
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
    
    def func__builtin___len(self, x):
        return "Len(" + x + ")"


class StorageManagerADO(db.StorageManagerDB):
    """StoreManager to save and retrieve Units via ADO 2.7.
    
    You must run makepy on ADO 2.7 before installing.
    """
    
    close_connection_method = 'Close'
    decompiler = ADOSQLDecompiler
    fromAdapter = AdapterFromADO()
    
    def connatoms(self):
        atoms = {}
        for pair in self.connstring.split(";"):
            if pair:
                k, v = pair.split("=", 1)
                atoms[k.upper().strip()] = v.strip()
        return atoms
    
    def sql_name(self, name, quoted=True):
        if quoted:
            name = '[' + name + ']'
        return name
    
    def _get_conn(self):
        conn = win32com.client.Dispatch(r'ADODB.Connection')
        conn.Open(self.connstring)
        return conn
    
    def execute(self, query, conn=None):
        if conn is None:
            conn = self.connection()
        self.arena.log(query, dejavu.LOGSQL)
        try:
            conn.Execute(query)
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
                res = conn.OpenSchema(query)
            else:
                self.arena.log(query, dejavu.LOGSQL)
                res = win32com.client.Dispatch(r'ADODB.Recordset')
                if self.threaded:
                    # 'conn' will be a ConnectionWrapper object, which .Open
                    # won't accept. Pass the unwrapped connection instead.
                    res.Open(query, conn.conn, adOpenForwardOnly, adLockReadOnly)
                else:
                    res.Open(query, conn, adOpenForwardOnly, adLockReadOnly)
        except pywintypes.com_error, x:
            try:
                res.Close()
            except:
                pass
            x.args += (query, )
            conn = None
            # "raise x" here or we could get the traceback of the inner try.
            raise x
        
        columns = [(x.Name, x.Type) for x in res.Fields]
        
        data = []
        if not(res.BOF and res.EOF):
            # We tried .MoveNext() and lots of Fields.Item() calls.
            # Using GetRows() beats that time by about 2/3.
            data = res.GetRows()
            # Convert cols x rows -> rows x cols
            data = zip(*data)
        try:
            res.Close()
        except:
            pass
        conn = None
        
        return data, columns
    
    def version(self):
        adoconn = win32com.client.Dispatch(r'ADODB.Connection')
        return "ADO Version: %s" % adoconn.Version
    
    def get_tables(self, conn=None):
        return self.fetch(adSchemaTables, conn=conn, schema=True)
    
    def has_storage(self, cls):
        data, col_defs = self.get_tables()
        names = [x[2] for x in data]
        return self.table_name(cls.__name__, quoted=False) in names
    
    def get_columns(self, conn=None):
        return self.fetch(adSchemaColumns, conn=conn, schema=True)
    
    def rename_property(self, cls, oldname, newname):
        clsname = cls.__name__
        tblname = self.table_name(clsname, quoted=False)
        oldname = self.column_name(clsname, oldname, quoted=False)
        newname = self.column_name(clsname, newname, quoted=False)
         
        conn = self.connection()
        try:
            cat = win32com.client.Dispatch(r'ADOX.Catalog')
            cat.ActiveConnection = conn
            cat.Tables(tblname).Columns(oldname).Name = newname
        except pywintypes.com_error, x:
            conn = None
            cat = None
            raise


###########################################################################
##                                                                       ##
##                             SQL Server                                ##
##                                                                       ##
###########################################################################


class AdapterToADOSQL_SQLServer(db.AdapterToSQL):
    
    escapes = [("'", "''")]
    like_escapes = [("%", "[%]"), ("_", "[_]")]
    
    # These are not the same as coerce_bool (which is used on one side of 
    # a comparison). Instead, these are used when the whole (sub)expression
    # is True or False, e.g. "WHERE TRUE", or "WHERE TRUE and 'a'.'b' = 3".
    bool_true = "(1=1)"
    bool_false = "(1=0)"
    
    def coerce_bool(self, value):
        if value:
            return '1'
        return '0'


class FieldTypeAdapter_SQLServer(db.FieldTypeAdapter):
    
    numeric_max_precision = 38
    
    def coerce_bool(self, cls, key): return u"BIT"
    
    def coerce_datetime_datetime(self, cls, key):
        return u"DATETIME"
    
    def coerce_datetime_date(self, cls, key):
        return u"DATETIME"
    
    def coerce_datetime_time(self, cls, key):
        return u"DATETIME"
    
    def coerce_str(self, cls, key):
        # The bytes hint does not reflect the usual 4-byte base for varchar.
        prop = getattr(cls, key)
        bytes = int(prop.hints.get(u'bytes', '0'))
        if bytes == 0:
            # Okay, what the @#$%& is wrong with Redmond??!?! We can't even
            # compare TEXT or NTEXT fields??!? Fine. We'll deny such, and
            # warn the deployer with less swearing and exclamation points.
            warnings.warn("You have defined a string property without "
                          "limiting its length. Microsoft SQL Server does "
                          "not allow comparisons on string fields larger "
                          "than 8000 characters. Some of your data may be "
                          "truncated.", dejavu.StorageWarning)
            bytes = 8000
        # 8000 *bytes* is the absolute upper limit, based on T_SQL docs for
        # varchar/varbinary. If there are further fields defined for the
        # class, or the codepage uses a double-byte character set, we still
        # might exceed the max size (8060) for a record. We could calc the
        # total requested record size, and adjust accordingly. Meh.
        return u"VARCHAR(%s)" % bytes


class StorageManagerADO_SQLServer(StorageManagerADO):
    
    typeAdapter = FieldTypeAdapter_SQLServer()
    toAdapter = AdapterToADOSQL_SQLServer()
    
    def __init__(self, name, arena, allOptions={}):
        db.StorageManagerDB.__init__(self, name, arena, allOptions)
        
        self.connstring = allOptions[u'Connect']
        atoms = self.connatoms()
        self.dbname = atoms[u'INITIAL CATALOG']
    
    def create_database(self):
        # This method hasn't been tested yet for SQL server.
        adoconn = win32com.client.Dispatch(r'ADODB.Connection')
        atoms = self.connatoms()
        atoms['INITIAL CATALOG'] = "tempdb"
        adoconn.Open("; ".join(["%s=%s" % (k, v) for k, v in atoms.iteritems()]))
        adoconn.Execute("CREATE DATABASE %s" % self.sql_name(self.dbname))
        adoconn.Close()
    
    def drop_database(self):
        adoconn = win32com.client.Dispatch(r'ADODB.Connection')
        atoms = self.connatoms()
        atoms['INITIAL CATALOG'] = "tempdb"
        adoconn.Open("; ".join(["%s=%s" % (k, v) for k, v in atoms.iteritems()]))
        adoconn.Execute("DROP DATABASE %s;" % self.sql_name(self.dbname))
        adoconn.Close()
    
    def add_property(self, cls, name):
        clsname = cls.__name__
        # SQL Server doesn't use the "COLUMN" keyword with "ADD"
        self.execute("ALTER TABLE %s ADD %s %s;" %
                     (self.table_name(clsname),
                      self.column_name(clsname, name),
                      self.typeAdapter.coerce(cls, name),
                      ))
    
    def rename_property(self, cls, oldname, newname):
        clsname = cls.__name__
        oldname = self.column_name(clsname, oldname, quoted=False)
        newname = self.column_name(clsname, newname, quoted=False)
        if oldname != newname:
            self.execute("EXEC sp_rename '%s.%s', '%s', 'COLUMN'" %
                         (self.table_name(clsname), oldname, newname))


###########################################################################
##                                                                       ##
##                             MS Access                                 ##
##                                                                       ##
###########################################################################


class ADOSQLDecompiler_MSAccess(ADOSQLDecompiler):
    sql_cmp_op = ('<', '<=', '=', '<>', '>', '>=', 'in', 'not in')
    
    def dejavu_now(self):
        return "Now()"
    
    def dejavu_today(self):
        return "DateValue(Now())"
    
    def dejavu_year(self, x):
        return "Year(" + x + ")"


class FieldTypeAdapter_MSAccess(db.FieldTypeAdapter):
    
    numeric_max_precision = 15
    
    def coerce_bool(self, cls, key): return u"BIT"
    
    def coerce_datetime_datetime(self, cls, key): return u"DATETIME"
    def coerce_datetime_date(self, cls, key): return u"DATETIME"
    def coerce_datetime_time(self, cls, key): return u"DATETIME"
    
    def numeric_type(self, cls, key, precision, scale):
        if precision > self.numeric_max_precision:
            warnings.warn("Decimal precision %s > maximum %s for %s.%s, "
                          "using %s. Values may be stored incorrectly."
                          % (precision, self.numeric_max_precision,
                             cls.__name__, key, self.__class__.__name__),
                          dejavu.StorageWarning)
            precision = self.numeric_max_precision
        if scale > 4:
            warnings.warn("Decimal scale %s > maximum 4 for %s.%s, "
                          "using %s. Values may be stored incorrectly."
                          % (scale, cls.__name__, key,
                             self.__class__.__name__),
                          dejavu.StorageWarning)
        
        # MS Access doesn't let us control precision and scale directly.
        # From http://support.microsoft.com/?kbid=104977
        # ORACLE number            Microsoft Access data type
        # ---------------------------------------------------
        # Scale = 0 and
        #     precision <= 4       Integer
        #     precision <= 9       Long Integer
        #     precision <= 15      Double
        # Scale > 0 and  <= 4
        #     precision <= 15      Double
        # Scale > 4 and/or
        #     precision > 15       Text
        if scale == 0:
            if precision <= 4:
                return "INTEGER"
            elif precision <= 9:
                return "LONG"
        return "DOUBLE"
    
    def coerce_decimal_Decimal(self, cls, key):
        prop = getattr(cls, key)
        precision = int(prop.hints.get('precision', '0'))
        if precision == 0:
            precision = decimal.getcontext().prec
        # Assume most people use decimal for money; default scale = 2.
        scale = int(prop.hints.get(u'scale', 2))
        return self.numeric_type(cls, key, precision, scale)
    
    def coerce_fixedpoint_FixedPoint(self, cls, key):
        prop = getattr(cls, key)
        precision = int(prop.hints.get('precision', '0'))
        if precision == 0:
            precision = self.numeric_max_precision
        # Assume most people use decimal for money; default scale = 2.
        scale = int(prop.hints.get(u'scale', 2))
        return self.numeric_type(cls, key, precision, scale)
    
    def coerce_int(self, cls, key):
        prop = getattr(cls, key)
        bytes = int(prop.hints.get(u'bytes', '4'))
        if bytes == 1:
            return "BIT"
        else:
            return u"INTEGER"
    
    def coerce_long(self, cls, key):
        prop = getattr(cls, key)
        bytes = int(prop.hints.get(u'bytes', 0))
        return self.numeric_type(cls, key, precision, 0)
    
    def coerce_str(self, cls, key):
        # The bytes hint shall not reflect the usual 4-byte base for varchar.
        prop = getattr(cls, key)
        bytes = int(prop.hints.get(u'bytes', '0'))
        if bytes and bytes <= 255:
            # 255 chars is the upper limit for TEXT / VARCHAR in MS Access.
            return u"VARCHAR(%s)" % bytes
        else:
            # MEMO is 1 GB max when set programatically (only 64K when set
            # in Access UI). But then, 1 GB is the limit for the whole DB.
            for assoc in cls._associations.itervalues():
                if assoc.nearKey == key:
                    warnings.warn("Memo fields cannot be used as join keys. "
                                  "You should set %s.%s(hints={'bytes': 255})"
                                  % (cls.__name__, key),
                                  dejavu.StorageWarning)
            return u"MEMO"


class AdapterToADOSQL_MSAccess(db.AdapterToSQL):
    """Coerce Expression constants to ADO SQL."""
    
    escapes = [("'", "''")]
    like_escapes = [("%", "[%]"), ("_", "[_]")]
    
    def coerce_datetime_datetime(self, value):
        return (u'#%s/%s/%s %02d:%02d:%02d#' %
                (value.month, value.day, value.year,
                 value.hour, value.minute, value.second))
    
    def coerce_datetime_date(self, value):
        return u'#%s/%s/%s#' % (value.month, value.day, value.year)
    
    def coerce_datetime_time(self, value):
        return u'#%02d:%02d:%02d#' % (value.hour, value.minute, value.second)


class StorageManagerADO_MSAccess(StorageManagerADO):
    # Jet Connections and Recordsets are always free-threaded.
    
    use_asterisk_to_get_all = True
    
    decompiler = ADOSQLDecompiler_MSAccess
    typeAdapter = FieldTypeAdapter_MSAccess()
    toAdapter = AdapterToADOSQL_MSAccess()
    
    def __init__(self, name, arena, allOptions={}):
        db.StorageManagerDB.__init__(self, name, arena, allOptions)
        
        self.connstring = allOptions[u'Connect']
        atoms = self.connatoms()
        self.dbname = (atoms.get(u'DATA SOURCE') or
                       atoms.get(u'DATA SOURCE NAME') or
                       atoms.get(u'DBQ'))
        # MS Access can't use a pool, because there doesn't seem
        # to be a commit timeout.
        self.pool = None
        self.threaded = False
        self.debug_connections = True
    
    def create_database(self):
        # By not providing an Engine Type, it defaults to 5 = Access 2000.
        cat = win32com.client.Dispatch(r'ADOX.Catalog')
        cat.Create(self.connstring)
        cat.ActiveConnection.Close()
    
    def drop_database(self):
        import os
        # This should accept relative or absolute paths
        if os.path.exists(self.dbname):
            os.remove(self.dbname)


def gen_py():
    # Auto generate .py support for ADO 2.7+
    print 'Please wait while support for ADO 2.7+ is verified...'
    CLSID = '{EF53050B-882E-4776-B643-EDA472E8E3F2}'
    return win32com.client.gencache.EnsureModule(CLSID, 0, 2, 7)


if __name__ == '__main__':
    gen_py()
