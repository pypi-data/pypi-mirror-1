# See http://www.firebirdsql.org/index.php?op=devel&sub=engine&id=SQL_conformance&nosb=1
# for lots of conformance info.

import datetime
import os
import threading
import time

import dejavu
from dejavu import logic, errors
from dejavu.storage import db, isolation as _isolation

import kinterbasdb

# Use datetime instead of mxDateTime
kinterbasdb.init(type_conv=200)


class AdapterToFireBirdSQL(db.AdapterToSQL):
    
    # Notice these are ordered pairs. Escape \ before introducing new ones.
    # Values in these two lists should be strings encoded with self.encoding.
    escapes = [("'", "''")]
    like_escapes = [("\\", r"\\"), ("%", r"\%"), ("_", r"\_")]
    
    # Firebird doesn't have true or false keywords.
    bool_true = "1=1"
    bool_false = "1=0"
    
    def coerce_bool_to_any(self, value):
        if value:
            return '1'
        return '0'
    
    def _to_BLOB(self, value):
        return "'%s'" % str(value)
    
    coerce_decimal_to_BLOB = _to_BLOB
    coerce_decimal_Decimal_to_BLOB = _to_BLOB
    coerce_fixedpoint_FixedPoint_to_BLOB = _to_BLOB
    coerce_float_to_BLOB = _to_BLOB
    coerce_int_to_BLOB = _to_BLOB
    coerce_long_to_BLOB = _to_BLOB


_power_of_ten = [10 ** x for x in xrange(20)]
del x


class AdapterFromFirebirdDB(db.AdapterFromDB):
    
    def coerce_any_to_decimal(self, value):
        if isinstance(value, tuple):
            value, scale = value
            return decimal(value) / _power_of_ten[-scale]
        return decimal(str(value))
    
    def coerce_any_to_decimal_Decimal(self, value):
        if isinstance(value, tuple):
            value, scale = value
            return db.decimal.Decimal(value) / _power_of_ten[-scale]
        return db.decimal.Decimal(str(value))
    
    def coerce_any_to_fixedpoint_FixedPoint(self, value):
        if isinstance(value, tuple):
            value, scale = value
            return db.fixedpoint.FixedPoint(float(value) / _power_of_ten[-scale], -scale)
        elif isinstance(value, basestring):
            # Unicode really screws up fixedpoint; for example:
            # >>> fixedpoint.FixedPoint(u'111111111111111111111111111.1')
            # FixedPoint('111111111111111104952008704.00', 2)
            value = str(value)
            
            scale = 0
            atoms = value.rsplit(".", 1)
            if len(atoms) > 1:
                scale = len(atoms[-1])
            return db.fixedpoint.FixedPoint(value, scale)
        else:
            return db.fixedpoint.FixedPoint(value)
    
    def coerce_any_to_int(self, value):
        if isinstance(value, tuple):
            value, scale = value
            if scale:
                value = value / _power_of_ten[-scale]
        return int(value)
    
    def coerce_any_to_long(self, value):
        if isinstance(value, tuple):
            value, scale = value
            if scale:
                value = value / _power_of_ten[-scale]
        return long(value)
    
    # !!?!??! kinterbasdb already converts to datetime? Rapture!
    def coerce_any_to_datetime_datetime(self, value):
        return value
    
    def coerce_any_to_datetime_date(self, value):
        return value
    
    def coerce_any_to_datetime_time(self, value):
        return value


class TypeAdapterFirebird(db.TypeAdapter):
    """Return the SQL typename of a DB column."""
    
    # Max decimal precision for NUMERIC columns.
    numeric_max_precision = 18
    numeric_max_bytes = 9
    
    numeric_text_type = "BLOB"
    
    def coerce_str(self, col):
        # The bytes hint shall not reflect the usual 4-byte base for varchar.
        
        # Although Firebird allows VARCHAR of 32765, 255 is usually the max
        # for which an index can be created.
        default = 127
        
        bytes = int(col.hints.get('bytes', default))
        if 1 <= bytes <= 32765:
            return "VARCHAR(%s)" % bytes
        return "BLOB"
    
    def coerce_bool(self, col):
        return "SMALLINT"
    
    def int_type(self, bytes):
        """Return a datatype which can handle the given number of bytes."""
        if bytes <= 2:
            return "SMALLINT"
        elif bytes <= 4:
            return "INTEGER"
        else:
            # Anything larger than 8 bytes, use decimal/numeric.
            return "NUMERIC(%s, 0)" % (bytes * 2)


class FirebirdSQLDecompiler(db.SQLDecompiler):
    
    # --------------------------- Dispatchees --------------------------- #
    
    def attr_startswith(self, tos, arg):
        return tos + " STARTING WITH " + arg
    
    def attr_endswith(self, tos, arg):
        return tos + " LIKE '%" + self.adapter.escape_like(arg) + "' ESCAPE '\\'"
    
    def containedby(self, op1, op2):
        if isinstance(op1, db.ConstWrapper):
            # Looking for text in a field. Use Like (reverse terms).
            return op2 + " LIKE '%" + self.adapter.escape_like(op1) + "%' ESCAPE '\\'"
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
            return op2 + " CONTAINING " + op1
        else:
            # Looking for field in (a, b, c).
            # Force all args to uppercase for case-insensitive comparison.
            atoms = [self.adapter.coerce(x).upper() for x in op2.basevalue]
            return "UPPER(%s) IN (%s)" % (op1, ", ".join(atoms))
    
    def dejavu_icontains(self, x, y):
        return self.dejavu_icontainedby(y, x)
    
    # Firebird has no LOWER function, but it does have an UPPER. Funky.
    
    def dejavu_istartswith(self, x, y):
        return "UPPER(" + x + ") LIKE '" + self.adapter.escape_like(y) + "%' ESCAPE '\\'"
    
    def dejavu_iendswith(self, x, y):
        return "UPPER(" + x + ") LIKE '%" + self.adapter.escape_like(y) + "' ESCAPE '\\'"
    
    def dejavu_ieq(self, x, y):
        return "UPPER(" + x + ") = UPPER(" + y + ")"
    
    # Firebird 1.5 doesn't seem to have any date functions
    def dejavu_now(self):
        return "CURRENT_TIMESTAMP"
    
    dejavu_today = None
    dejavu_year = None
    dejavu_month = None
    dejavu_day = None
    
    # Firebird 1.5 has no LENGTH function
    func__builtin___len = None



class FirebirdTable(db.Table):
    
    def _add_column(self, column):
        """Internal function to add the column to the database."""
        coldef = self.db.col_def(column)
        # FB doesn't recognize the keyword "COLUMN" in "ADD".
        self.db.execute("ALTER TABLE %s ADD %s;" % (self.qname, coldef))
    
    def _drop_column(self, column):
        """Internal function to drop the column from the database."""
        # FB doesn't recognize the keyword "COLUMN" in "DROP".
        self.db.execute("ALTER TABLE %s DROP %s;" %
                        (self.qname, column.qname))
    
    def _rename(self, oldcol, newcol):
        # FB doesn't use the keyword "RENAME".
        self.db.execute("ALTER TABLE %s ALTER COLUMN %s TO %s;" %
                        (self.qname, oldcol.qname, newcol.qname))


class FirebirdDatabase(db.Database):
    
    decompiler = FirebirdSQLDecompiler
    adaptertosql = AdapterToFireBirdSQL()
    adapterfromdb = AdapterFromFirebirdDB()
    typeadapter = TypeAdapterFirebird()
    tableclass = FirebirdTable
    
    sql_name_max_length = 31
    encoding = 'utf8'
    
    def __init__(self, name, **kwargs):
        self._discover_lock = threading.Lock()
        
        dict.__init__(self)
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        
        # Here's where we differ from the superclass.
        # The Firebird "database name" is a filename, not an identifier,
        # so we don't set self.name = sql_name(name).
        self.name = name
        
        self.qname = self.quote(self.name)
        self.transactions = {}
        self.connect()
        self.discover_dbinfo()
    
    def _get_dbinfo(self, conn=None):
        return {}
    
    def _get_tables(self, conn=None):
        data, _ = self.fetch("SELECT RDB$RELATION_NAME FROM RDB$RELATIONS "
                             "WHERE RDB$SYSTEM_FLAG=0 AND RDB$VIEW_BLR IS NULL;",
                             conn=conn)
        return [self.tableclass(name.strip(), self.quote(name.strip()), self)
                for name, in data]
    
    def _get_table(self, tablename, conn=None):
        data, _ = self.fetch("SELECT RDB$RELATION_NAME FROM RDB$RELATIONS "
                             "WHERE RDB$SYSTEM_FLAG=0 AND RDB$VIEW_BLR IS NULL "
                             "AND RDB$RELATION_NAME = '%s';" % tablename,
                             conn=conn)
        for name, in data:
            name = name.strip()
            if name == tablename:
                return self.tableclass(name, self.quote(name), self)
        raise errors.MappingError(tablename)
    
    def _get_columns(self, tablename, conn=None):
        # FB pads table names to CHAR(31)
        tablename = tablename.ljust(31, " ")
        
        # Get Primary Key names first
        data, _ = self.fetch(
            "SELECT S.RDB$FIELD_NAME AS COLUMN_NAME "
            "FROM RDB$RELATION_CONSTRAINTS RC "
            "LEFT JOIN RDB$INDICES I ON (I.RDB$INDEX_NAME = RC.RDB$INDEX_NAME) "
            "LEFT JOIN RDB$INDEX_SEGMENTS S ON (S.RDB$INDEX_NAME = I.RDB$INDEX_NAME) "
            "WHERE (RC.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY') "
            "AND (I.RDB$RELATION_NAME = '%s')" % tablename,
            conn=conn
            )
        pks = [row[0].rstrip() for row in data]
        
        # Now get the rest of the col data
        data, _ = self.fetch("SELECT RF.RDB$FIELD_NAME, T.RDB$TYPE_NAME, "
                             "F.RDB$FIELD_LENGTH, RF.RDB$DEFAULT_SOURCE, "
                             "F.RDB$FIELD_PRECISION, F.RDB$FIELD_SCALE "
                             "FROM RDB$RELATION_FIELDS RF LEFT JOIN "
                             "RDB$FIELDS F ON F.RDB$FIELD_NAME = RF.RDB$FIELD_SOURCE "
                             "LEFT JOIN RDB$TYPES T ON T.RDB$TYPE = F.RDB$FIELD_TYPE "
                             "WHERE RF.RDB$RELATION_NAME='%s' AND "
                             "T.RDB$FIELD_NAME='RDB$FIELD_TYPE';" % tablename,
                             conn=conn)
        cols = []
        for name, dbtype, fieldlen, default, prec, scale in data:
            hints = {}
            if prec:
                hints['precision'] = prec
                if scale:
                    hints['scale'] = scale = abs(scale)
            else:
                hints['bytes'] = fieldlen
            
            # FB pads name and type values to 31 chars.
            name, dbtype = name.rstrip(), dbtype.rstrip()
            
            # Grr. INT64 may actually have been declared as NUMERIC.
            # See http://www.ibphoenix.com/main.nfs?a=ibphoenix&page=ibp_60_exact_num_fs
            if scale and (dbtype in ('SMALLINT', 'INTEGER', 'INT64')):
                dbtype = "NUMERIC"
            
            key = (name in pks)
            
            # RDB$RELATION_FIELDS.RDB$DEFAULT_SOURCE = None | "DEFAULT x"
            if default:
                default = default[len("DEFAULT "):]
                if dbtype in ("SHORT", "LONG"):
                    default = int(default)
                elif dbtype in ("FLOAT",):
                    default = float(default)
            
            # Column(name, qname, dbtype, default=None, hints=None, key=False)
            col = db.Column(name, self.quote(name), dbtype, default, hints, key)
            cols.append(col)
        return cols
    
    def _get_indices(self, tablename, conn=None):
        data, _ = self.fetch("SELECT I.RDB$INDEX_NAME, S.RDB$FIELD_NAME, "
                             "I.RDB$UNIQUE_FLAG "
                             "FROM RDB$INDICES I LEFT JOIN RDB$INDEX_SEGMENTS S "
                             "ON (S.RDB$INDEX_NAME = I.RDB$INDEX_NAME) "
                             "WHERE I.RDB$RELATION_NAME = '%s';"
                             % tablename.ljust(31, " "),
                             conn=conn)
        indices = []
        for name, colname, unique in data:
            name = name.rstrip()
            colname = colname.rstrip()
            unique = bool(unique)
            ind = db.Index(name, self.quote(name), tablename, colname, unique)
            indices.append(ind)
        
        return indices
    
    def python_type(self, dbtype):
        """Return a Python type which can store values of the given dbtype."""
        dbtype = dbtype.upper()
        
        if dbtype in ('INTEGER', 'SMALLINT', 'LONG', 'SHORT'):
            return int
        elif dbtype in ('BIGINT', 'INT64'):
            return long
        elif dbtype in ('FLOAT', 'DOUBLE', 'DOUBLE PRECISION', 'REAL'):
            return float
        elif dbtype.startswith('NUMERIC') or dbtype.startswith('DECIMAL'):
            if db.decimal:
                return db.decimal.Decimal
            elif db.fixedpoint:
                return db.fixedpoint.FixedPoint
        elif dbtype == 'DATE':
            return datetime.date
        elif dbtype == 'TIMESTAMP':
            return datetime.datetime
        elif dbtype == 'TIME':
            return datetime.time
        for t in ('CHAR', 'VARCHAR', 'BLOB', 'TEXT', 'VARYING'):
            if dbtype.startswith(t):
                return str
        for t in ('NCHAR', 'NATIONAL'):
            if dbtype.startswith(t):
                return unicode
        
        raise TypeError("Database type %r could not be converted "
                        "to a Python type." % dbtype)
    
    def col_def(self, column):
        """Return a clause for the given column for CREATE or ALTER TABLE.
        
        This will be of the form "name type [DEFAULT x] [NOT NULL]".
        
        Firebird needs the sequence created in a separate SQL statement.
        """
        dbtype = column.dbtype
        
        default = column.default or ""
        if default:
            default = self.adaptertosql.coerce(default, dbtype)
            default = " DEFAULT %s" % default
        
        notnull = ""
        if column.key:
            # Firebird PK's must be NOT NULL
            notnull = " NOT NULL"
        
        return '%s %s%s%s' % (column.qname, dbtype, default, notnull)
    
    def create_sequence(self, table, column):
        """Create a SEQUENCE for the given column and set its sequence_name."""
        sname = column.sequence_name
        if sname is None:
            sname = self.quote("%s_%s_seq" % (table.name, column.name))
            column.sequence_name = sname
        self.execute("CREATE GENERATOR %s;" % sname)
        self.execute("SET GENERATOR %s TO %s;" % (sname, column.initial - 1))
    
    def drop_sequence(self, column):
        """Drop a SEQUENCE for the given column and remove its sequence_name."""
        if column.sequence_name is not None:
            self.execute("DROP GENERATOR %s;" % column.sequence_name)
            column.sequence_name = None
    
    #                               Naming                               #
    
    def quote(self, name):
        """Return name, quoted for use in an SQL statement."""
        return '"' + name.replace('"', '""') + '"'
    
    def _get_conn(self):
        conn = kinterbasdb.connect(host=self.host,
                                   database=self.name,
                                   user=self.user,
                                   password=self.password,
                                   charset=self.encoding,
                                   )
        # Set the default TPB (for implicit transactions).
        conn.default_tpb = self._no_iso_tpb + self.default_isolation
        
        # Remove converters for FIXED so we can mix fixedpoint and decimal
        conn.set_type_trans_in({'FIXED': None})
        conn.set_type_trans_out({'FIXED': None})
        return conn
    
    deadlock_timeout = 10
    
    def execute(self, query, conn=None):
        try:
            if conn is None:
                conn = self.connection()
            if isinstance(query, unicode):
                query = query.encode(self.adaptertosql.encoding)
            self.log(query)
            cur = conn.cursor()
            
            start = time.time()
            while True:
                try:
                    cur.execute(query)
                    
                    # If we're not in a transaction, we need to auto-commit.
                    # This prevents "Previous transaction still active" errors.
                    key = self.transaction_key()
                    trans = self.transactions.get(key)
                    if trans is None or isinstance(trans, db.TransactionLock):
                        conn.commit()
                    
                    return
                except Exception, x:
                    if self.is_lock_error(x) and self.deadlock_timeout:
                        if time.time() - start < self.deadlock_timeout:
                            time.sleep(0.000001)
                            continue
                    raise
        except Exception, x:
            x.args += (query,)
            # Dereference the connection so that release() is called back.
            conn = None
            raise
    
    def fetch(self, query, conn=None):
        """Return rowdata, columns (name, type) for the given query.
        
        query should be a SQL query in string format
        rowdata will be an iterable of iterables containing the result values.
        columns will be an iterable of (column name, data type) pairs.
        """
        try:
            if conn is None:
                conn = self.connection()
            if isinstance(query, unicode):
                query = query.encode(self.adaptertosql.encoding)
            self.log(query)
            cur = conn.cursor()
            cur.execute(query)
            
            data = cur.fetchall()
            desc = cur.description
            cur.close()
            
            # If we're not in a transaction, we need to auto-commit.
            # This prevents "Previous transaction still active" errors.
            key = self.transaction_key()
            trans = self.transactions.get(key)
            if trans is None or isinstance(trans, db.TransactionLock):
                conn.commit()
            
        except Exception, x:
            x.args += (query,)
            # Dereference the connection so that release() is called back.
            conn = None
            raise
        return data, desc
    
    #                               Schemas                               #
    
    def create_database(self):
        self.lock("Creating database. Transactions not allowed.")
        try:
            # Firebird DB 'names' are actually filesystem paths.
            sql = ("CREATE DATABASE %s USER '%s' PASSWORD '%s';"
                   % (self.qname, self.user, self.password))
            
            # Use the kinterbasdb helper methods for cleaner create and drop.
            # We also use dialect 3 *always* to help with quoted identifiers.
            conn = kinterbasdb.create_database(sql, 3)
            conn.close()
            
            self.clear()
        finally:
            self.unlock()
    
    def drop_database(self):
        self.lock("Dropping database. Transactions not allowed.")
        try:
            # Must shut down all connections to avoid
            # "being accessed by other users" error.
            self.connection.shutdown()
            
            conn = self._get_conn()
            conn.drop_database()
            
            self.clear()
        finally:
            self.unlock()
    
    #                            Transactions                             #
    
    default_isolation = kinterbasdb.isc_tpb_read_committed
    _no_iso_tpb = (
        kinterbasdb.isc_tpb_version3
        + kinterbasdb.isc_tpb_shared
        + kinterbasdb.isc_tpb_nowait
        + kinterbasdb.isc_tpb_write
        + kinterbasdb.isc_tpb_rec_version
        )
    isolation_levels = ["READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"]
    
    def is_lock_error(self, exc):
        """If the given exception instance is a lock timeout, return True.
        
        This should return True for errors which arise from transaction
        locking timeouts; for example, if the database prevents 'dirty
        reads' by raising an error.
        """
        # ProgrammingError: (-901,
        # 'isc_dsql_execute: \n  lock conflict on no wait transaction',
        # 'UPDATE "testVet" SET "City" = \'Tehachapi\', ... ;')
        if not isinstance(exc, kinterbasdb.ProgrammingError):
            return False
        return "lock conflict" in exc.args[1]
    
    def isolate(self, isolation=None):
        """isolate() is not implemented for Firebird."""
        raise NotImplementedError("Firebird does not allow arbitrary re-isolation.")
    
    def start(self, isolation=None):
        """Start a transaction. Not needed if self.implicit_trans is True."""
        if isolation is None:
            isolation = self.default_isolation
        
        if isinstance(isolation, _isolation.IsolationLevel):
            # Map the given IsolationLevel object to a native value.
            # This base class uses the four ANSI names as native values.
            isolation = isolation.name
            if isolation not in self.isolation_levels:
                raise ValueError("IsolationLevel %r not allowed by %s. "
                                 "Try one of %r instead."
                                 % (isolation, self.__class__.__name__,
                                    self.isolation_levels))
            
            if isolation == "READ COMMITTED":
                isolation = kinterbasdb.isc_tpb_read_committed
            elif isolation == "REPEATABLE READ":
                isolation = kinterbasdb.isc_tpb_concurrency
            else:
                isolation = kinterbasdb.isc_tpb_consistency
        
        conn = self.get_transaction(new=True)
        conn.begin(self._no_iso_tpb + isolation)
    
    def rollback(self):
        """Roll back the current transaction, if any."""
        key = self.transaction_key()
        try:
            conn = self.transactions.pop(key)
        except KeyError:
            pass
        else:
            conn.rollback()
    
    def commit(self):
        """Commit the current transaction, if any."""
        key = self.transaction_key()
        try:
            conn = self.transactions.pop(key)
        except KeyError:
            pass
        else:
            conn.commit()



class FirebirdJoinWrapper(db.UnitClassWrapper):
    """Unit class wrapper, for use in parsing multiselect joins."""
    
    def _joinname(self):
        if self.alias:
            # Firebird doesn't use the "AS" keyword
            return "%s %s" % (self.table.qname, self.alias)
        else:
            return self.table.qname
    joinname = property(_joinname, doc=("Quoted table name for use in "
                                        "JOIN clause (read-only)."))


class StorageManagerFirebird(db.StorageManagerDB):
    """StoreManager to save and retrieve Units via Firebird 1.5."""
    
    databaseclass = FirebirdDatabase
    joinwrapper = FirebirdJoinWrapper
    
    def version(self):
        import kinterbasdb.services
        svcCon = kinterbasdb.services.connect(host=self.db.host,
                                              user=self.db.user,
                                              password=self.db.password)
        return ("KInterbasDB Version: %r\nServer Version: %r"
                % (kinterbasdb.__version__, svcCon.getServerVersion()))
    
    def multiselect(self, classes, expr):
        """Return an SQL SELECT statement, an imperfect flag, and column names."""
        
        # Create a new unitjoin tree where each class is wrapped.
        # Then we can tag the wrappers with metadata with impunity.
        
        # Firebird 1.5 won't accept the same table twice in a JOIN
        # unless *both* table names are aliased.
        # seen = {}
        aliascount = [0]
        q = lambda name: self.db.quote(self.db.table_name(name))
        
        def wrap(unitjoin):
            cls1, cls2 = unitjoin.class1, unitjoin.class2
            if isinstance(cls1, dejavu.UnitJoin):
                wclass1 = wrap(cls1)
            else:
                wclass1 = self.joinwrapper(cls1, self.db[cls1.__name__])
                aliascount[0] += 1
                wclass1.alias = q("t%d" % aliascount[0])
            if isinstance(cls2, dejavu.UnitJoin):
                wclass2 = wrap(cls2)
            else:
                wclass2 = self.joinwrapper(cls2, self.db[cls2.__name__])
                aliascount[0] += 1
                wclass2.alias = q("t%d" % aliascount[0])
            uj = dejavu.UnitJoin(wclass1, wclass2, unitjoin.leftbiased)
            # if the unitjoin had a custom association path, set it on
            # the new UnitJoin instance
            uj.path = unitjoin.path
            return uj
        classes = wrap(classes)
        
        joins = self.join(classes)
        
        if expr is None:
            expr = logic.Expression(lambda *args: True)
        
        wheretables = []
        for c in classes:
            alias = getattr(c, "alias", None)
            if alias is None:
                t = self.db[c.__name__]
                qname = t.qname
            else:
                # c is an instance of self.joinwrapper
                t = c.table
                qname = c.alias or t.qname
            
            wheretables.append((qname, t))
        
        w, imp = self.db.where(wheretables, expr)
        
        cols = []
        colnames = []
        for wrapper in classes:
            c, names = wrapper.columns()
            cols.extend(c)
            colnames.extend(names)
        
        statement = ("SELECT %s FROM %s WHERE %s;" %
                     (', '.join(colnames), joins, w))
        return statement, imp, cols
    
    def _seq_UnitSequencerInteger(self, unit):
        """Reserve a unit using the table's generator."""
        cls = unit.__class__
        t = self.db[cls.__name__]
        
        fields = []
        values = []
        for key in cls.properties:
            col = t[key]
            if col.autoincrement:
                # This advances the generator and returns its new value.
                data, _ = self.db.fetch("SELECT GEN_ID(%s, 1) FROM RDB$DATABASE;"
                                        % col.sequence_name)
                val, = data[0]
                setattr(unit, key, val)
            else:
                val = getattr(unit, key)
            val = self.db.adaptertosql.coerce(val, col.dbtype)
            fields.append(col.qname)
            values.append(val)
        
        fields = ", ".join(fields)
        values = ", ".join(values)
        self.db.execute('INSERT INTO %s (%s) VALUES (%s);' %
                        (t.qname, fields, values))

