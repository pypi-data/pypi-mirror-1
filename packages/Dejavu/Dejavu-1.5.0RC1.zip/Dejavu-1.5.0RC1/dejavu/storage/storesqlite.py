import datetime
import os
import threading
import time

import dejavu
from dejavu import errors, logic, storage
from dejavu.storage import db, isolation as _isolation

try:
    # Use _sqlite3 directly to avoid all of the DB-API overhead.
    # This assumes the one built into Python 2.5+
    import _sqlite3 as _sqlite
    _version = storage.Version(_sqlite.sqlite_version)
    _cursor_required = True
    _fetchall_required = True
    _lastrowid_support = True
except ImportError:
    # Use _sqlite directly to avoid all of the DB-API overhead.
    # This will import the "old API for SQLite 3.x",
    # using e.g. pysqlite 1.1.7
    import _sqlite
    _version = storage.Version(_sqlite.sqlite_version())
    _cursor_required = False
    _fetchall_required = False
    _lastrowid_support = False


# ESCAPE keyword was added Nov 2004, 1 month after 3.0.8 release.
_escape_support = (_version > storage.Version([3, 0, 8]))
if not _escape_support:
    _escape_warning = ("Version %s of sqlite does not support "
                       "wildcard literals." % _version)
    import warnings
    warnings.warn(_escape_warning, errors.StorageWarning)

_add_column_support = (_version >= storage.Version([3, 2, 0]))
_rename_table_support = (_version >= storage.Version([3, 1, 0]))
_autoincrement_support = (_version >= storage.Version([3, 1, 0]))
_cast_support = (_version >= storage.Version([3, 2, 3]))

class AdapterToSQLite(db.AdapterToSQL):
    
    # C-style backslash escapes are not supported.
    # See http://www.sqlite.org/lang_expr.html
    escapes = [("'", "''")]
    like_escapes = [("%", "\%"), ("_", "\_")]
    
    bool_true = "1"
    bool_false = "0"
    
    # If you are using type adapters that support a "standard"
    # date/datetime format for SQLite, set the following flag to True
    using_perfect_dates = False
    
    def coerce_bool_to_any(self, value):
        if value:
            return '1'
        return '0'


class AdapterFromSQLite(db.AdapterFromDB):
    
    def coerce_any_to_bool(self, value):
        # sqlite 2 will return a string, either '0' or '1'.
        if isinstance(value, basestring):
            return (value == '1')
        # sqlite 3 will return an int.
        return bool(value)


class SQLiteDecompiler(db.SQLDecompiler):
    
    def visit_COMPARE_OP(self, lo, hi):
        if self.adapter.using_perfect_dates:
            op2, op1 = self.stack.pop(), self.stack.pop()
            
            # SQLite can do meaningful date/datetime comparisions with
            # Julian dates.  It has a function to convert a string date
            # to a Julian date.  In this case, if one of the operands in
            # a comparison is a date or datetime instance, we wrap both
            # operands in a call to julianday to provided a meaningful
            # comparison.
            for i, op in enumerate((op1, op2)):
                if (isinstance(op, db.ConstWrapper) and
                    isinstance(op.basevalue, (datetime.date, datetime.datetime))):
                    op1 = "julianday(" + op1 + ")"
                    op2 = "julianday(" + op2 + ")"
                    break
                if isinstance(op, basestring) and "julianday" in op:
                    if i == 0:
                        op2 = "julianday(" + op2 + ")"
                    else:
                        op1 = "julianday(" + op1 + ")"
                    break
            
            # Put the operands back on the stack so that the standard
            # visit_COMPARE_OP can have its way with them.
            self.stack.append(op1)
            self.stack.append(op2)
            
        db.SQLDecompiler.visit_COMPARE_OP(self, lo, hi)
    
    def attr_startswith(self, tos, arg):
        if _escape_support:
            return tos + " LIKE '" + self.adapter.escape_like(arg) + r"%' ESCAPE '\'"
        else:
            if "%" in arg or "_" in arg:
                raise ValueError(_escape_warning)
            else:
                return tos + " LIKE '" + arg.strip(r"'\"") + "%'"
    
    def attr_endswith(self, tos, arg):
        if _escape_support:
            return tos + " LIKE '%" + self.adapter.escape_like(arg) + r"' ESCAPE '\'"
        else:
            if "%" in arg or "_" in arg:
                raise ValueError(_escape_warning)
            else:
                return tos + " LIKE '%" + arg.strip(r"'\"") + "'"
    
    def containedby(self, op1, op2):
        if isinstance(op1, db.ConstWrapper):
            # Looking for text in a field. Use Like (reverse terms).
            if _escape_support:
                return op2 + " LIKE '%" + self.adapter.escape_like(op1) + r"%' ESCAPE '\'"
            else:
                if "%" in op1 or "_" in op1:
                    raise ValueError(_escape_warning)
                else:
                    return op2 + " LIKE '%" + op1.strip(r"'\"") + r"%'"
        else:
            # Looking for field in (a, b, c)
            atoms = [self.adapter.coerce(x) for x in op2.basevalue]
            return op1 + " IN (" + ", ".join(atoms) + ")"
    
    def dejavu_icontainedby(self, op1, op2):
        if isinstance(op1, db.ConstWrapper):
            # Looking for text in a field. Use Like (reverse terms).
            if _escape_support:
                return ("LOWER(" + op2 + ") LIKE '%" +
                        self.adapter.escape_like(op1).lower() + r"%' ESCAPE '\'")
            else:
                if "%" in op1 or "_" in op1:
                    raise ValueError(_escape_warning)
                else:
                    return ("LOWER(" + op2 + ") LIKE '%" +
                            op1.strip("'\"").lower() + r"%'")
        else:
            # Looking for field in (a, b, c).
            # Force all args to lowercase for case-insensitive comparison.
            atoms = [self.adapter.coerce(x).lower() for x in op2.basevalue]
            return "LOWER(%s) IN (%s)" % (op1, ", ".join(atoms))
    
    def dejavu_icontains(self, x, y):
        return self.dejavu_icontainedby(y, x)
    
    def dejavu_istartswith(self, x, y):
        if _escape_support:
            return ("LOWER(" + x + ") LIKE '" + self.adapter.escape_like(y)
                    + r"%' ESCAPE '\'")
        else:
            if "%" in y or "_" in y:
                raise ValueError(_escape_warning)
            else:
                return "LOWER(" + x + ") LIKE '" + y.strip("'\"") + r"%'"
    
    def dejavu_iendswith(self, x, y):
        if _escape_support:
            return ("LOWER(" + x + ") LIKE '%" + self.adapter.escape_like(y)
                    + r"%' ESCAPE '\'")
        else:
            if "%" in y or "_" in y:
                raise ValueError(_escape_warning)
            else:
                return "LOWER(" + x + ") LIKE '%" + y.strip("'\"") + r"%'"
    
    def dejavu_now(self):
        if self.adapter.using_perfect_dates and _cast_support:
            return "julianday('now')"
        else:
            self.imperfect = True
            return db.cannot_represent
    
    dejavu_today = dejavu_now
    
    def dejavu_year(self, x):
        if self.adapter.using_perfect_dates and _cast_support:
            return "CAST(strftime('%Y', " + x + ") AS NUMERIC)"
        else:
            self.imperfect = True
            return db.cannot_represent
    
    def dejavu_month(self, x):
        if self.adapter.using_perfect_dates and _cast_support:
            return "CAST(strftime('%m', " + x + ") AS NUMERIC)"
        else:
            self.imperfect = True
            return db.cannot_represent
    
    def dejavu_day(self, x):
        if self.adapter.using_perfect_dates and _cast_support:
            return "CAST(strftime('%d', " + x + ") AS NUMERIC)"
        else:
            self.imperfect = True
            return db.cannot_represent


class TypeAdapterSQLite(db.TypeAdapter):
    """For a column and Python type, return a database type.
    
    From http://www.sqlite.org/datatype3.html:
        
        "The type affinity of a column is determined by the declared
        type of the column, according to the following rules:
        1. If the datatype contains the string "INT" then it is
           assigned INTEGER affinity.
        2. If the datatype of the column contains any of the strings
           "CHAR", "CLOB", or "TEXT" then that column has TEXT affinity.
           Notice that the type VARCHAR contains the string "CHAR" and
           is thus assigned TEXT affinity.
        3. If the datatype for a column contains the string "BLOB" or
           if no datatype is specified then the column has affinity NONE.
        4. If the datatype for a column contains any of the strings
           "REAL", "FLOA", or "DOUB" then the column has REAL affinity.
        5. Otherwise, the affinity is NUMERIC."
    """
    
    # &^%$#@! SQLite tries to convert NUMERIC values to REAL, so e.g.
    # INSERT INTO x VALUES 1111.1111 will result in 1111.1111000000001
    # Therefore, we must *always* use TEXT.
    numeric_max_precision = 0
    numeric_max_bytes = 0
    
    def coerce_decimal_Decimal(self, col):
        return "TEXT"
    
    def coerce_fixedpoint_FixedPoint(self, col):
        return "TEXT"
    
    def float_type(self, precision):
        """Return a datatype which can handle floats of the given binary precision."""
        return "REAL"
    
    def coerce_str(self, col):
        # The bytes hint shall not reflect the usual 4-byte base for varchar.
        return "TEXT"
    
    def coerce_bool(self, col): return "INTEGER"
    
    def coerce_datetime_datetime(self, col): return "TEXT"
    def coerce_datetime_date(self, col): return "TEXT"
    def coerce_datetime_time(self, col): return "TEXT"
    
    # I was seriously disinterested in writing a parser for interval.
    def coerce_datetime_timedelta(self, col):
        return self.coerce_float(col)
    
    def int_type(self, bytes):
        """Return a datatype which can handle the given number of bytes."""
        return "INTEGER"


class TypeAdapterSQLiteTypeless(db.TypeAdapter):
    
    def coerce(self, col, pytype):
        # SQLite can be 'typeless' (but we lose the type introspection)
        # This will be returned inside _get_columns as NUMERIC.
        return ""


class SQLiteTable(db.Table):
    
    def _parent_key(self):
        """Return the key of this Table in its parent Database."""
        names = [x for x in self.db if self.db[x].name == self.name]
        return names[0]
    
    def _temp_copy(self):
        # Create the temporary table with the new fields (no indices).
        temptable = self.copy()
        tempkey = "temp_" + self._parent_key()
        temptable.name = self.db.table_name(tempkey)
        temptable.qname = self.db.quote(temptable.name)
        temptable.indices.clear()
        return tempkey, temptable
    
    def _copy_from_temp(self, temptable, thiskey, tempkey):
        """Copy data from a temp table to a new table for self."""
        
        # Drop the old table and create the new, final table.
        newtable = temptable.copy()
        newtable.name = self.name
        newtable.qname = self.qname
        self.db[thiskey] = newtable
        
        # Copy data from the temp table to the final table.
        # For some odd reason, using "SELECT *"
        # mixes up the fields (during rename, at least).
        selfields = ", ".join([c.qname for c in temptable.values()])
        self.db.execute("INSERT INTO %s (%s) SELECT %s FROM %s;" %
                        (newtable.qname, selfields, selfields,
                         temptable.qname))
        
        # Drop the intermediate table.
        del self.db[tempkey]
    
    if not _add_column_support:
        def __setitem__(self, key, column):
            db = self.db
            
            if db is None:
                dict.__setitem__(self, key, column)
                return
            
            if key in self:
                del self[key]
            
            if column.autoincrement:
                # This may or may not be a no-op, depending on the DB.
                db.create_sequence(self, column)
            
            db.lock("Adding property. Transactions not allowed.")
            try:
                # Make a temporary copy.
                tempkey, temptable = self._temp_copy()
                # Add the new column to the copy.
                dict.__setitem__(temptable, key, column)
                # Bind the temp table to the DB.
                db[tempkey] = temptable
                
                # Copy data from the old table to the temp table.
                selfields = []
                for k, c in temptable.iteritems():
                    qname = c.qname
                    if k == key:
                        # This is a new column. Populate with NULL.
                        qname = "NULL AS %s" % qname
                    selfields.append(qname)
                db.execute("INSERT INTO %s SELECT %s FROM %s;" %
                           (temptable.qname, ", ".join(selfields), self.qname))
                
                # Copy data from the temp table to a new table for self.
                self._copy_from_temp(temptable, self._parent_key(), tempkey)
            finally:
                db.unlock()
    
    def __delitem__(self, key):
        db = self.db
        
        if key in self.indices:
            del self.indices[key]
        
        if db is None:
            dict.__delitem__(self, key)
            return
        
        db.lock("Dropping property. Transactions not allowed.")
        try:
            column = self[key]
            
            # Make a temporary copy.
            tempkey, temptable = self._temp_copy()
            # Drop the column from the copy.
            dict.__delitem__(temptable, key)
            # Bind the temp table to the DB.
            db[tempkey] = temptable
            
            # Copy data from the old table to the temp table.
            selfields = []
            for k, c in temptable.iteritems():
                qname = c.qname
                selfields.append(qname)
            db.execute("INSERT INTO %s SELECT %s FROM %s;" %
                       (temptable.qname, ", ".join(selfields), self.qname))
            
            self._copy_from_temp(temptable, self._parent_key(), tempkey)
            
            if column.autoincrement:
                # This may or may not be a no-op, depending on the DB.
                db.drop_sequence(column)
        finally:
            db.unlock()
    
    def rename(self, oldkey, newkey):
        """Rename a Column."""
        oldcol = self[oldkey]
        oldname = oldcol.name
        db = self.db
        newname = db.column_name(self.name, newkey)
        
        if oldname != newname:
            db.lock("Renaming property. Transactions not allowed.")
            try:
                dict.__delitem__(self, oldkey)
                dict.__setitem__(self, newkey, oldcol)
                oldcol.name = newname
                oldcol.qname = db.quote(newname)
                
                # Make a temporary copy.
                tempkey, temptable = self._temp_copy()
                # Bind the temp table to the DB.
                db[tempkey] = temptable
                
                # Copy data from the old table to the temp table.
                selfields = []
                for k, c in temptable.iteritems():
                    qname = c.qname
                    if k == newkey:
                        qname = "%s AS %s" % (db.quote(oldname), qname)
                    selfields.append(qname)
                db.execute("INSERT INTO %s SELECT %s FROM %s;" %
                           (temptable.qname, ", ".join(selfields), self.qname))
                
                self._copy_from_temp(temptable, self._parent_key(), tempkey)
            finally:
                db.unlock()


class SQLiteDatabase(db.Database):
    
    sql_name_max_length = 0
    
    decompiler = SQLiteDecompiler
    adaptertosql = AdapterToSQLite()
    adapterfromdb = AdapterFromSQLite()
    typeadapter = TypeAdapterSQLite()
    
    tableclass = SQLiteTable
    
    def isrelatedtype(self, pytype1, pytype2):
        if (self.using_perfect_dates and
            issubclass(pytype1, (datetime.date, datetime.time, datetime.datetime)) and
            issubclass(pytype2, self.python_type(self.typeadapter.coerce(None, pytype1)))):
            return True
        return db.Database.isrelatedtype(self, pytype1, pytype2)
    
    def _get_tables(self, conn=None):
        data, _ = self.fetch("SELECT name FROM sqlite_master WHERE type = 'table';")
        # Note that we set Table.db here, since these already exist in the DB.
        return [self.tableclass(row[0], self.quote(row[0]), self)
                for row in data]
    
    def _get_table(self, tablename, conn=None):
        data, _ = self.fetch("SELECT name FROM sqlite_master WHERE "
                             "name = '%s' AND type = 'table';" % tablename)
        # Note that we set Table.db here, since these already exist in the DB.
        for name, in data:
            if name == tablename:
                return self.tableclass(name, self.quote(name), self)
        raise errors.MappingError(tablename)
    
    def _get_columns(self, tablename, conn=None):
        # cid, name, type, notnull, dflt_value, pk
        data, _ = self.fetch("PRAGMA table_info(%s);" % tablename, conn=conn)
        
        cols = []
        for row in data:
            c = db.Column(row[1], self.quote(row[1]), row[2].upper(),
                          default=row[4], key=bool(row[5]))
            
            # "A single row can hold up to 2 ** 30 bytes of data
            #   in the current implementation."
            if c.dbtype in ("TEXT", "INTEGER"):
                c.hints['bytes'] = 2 ** 30
                # Since we MUST use TEXT instead of NUMERIC
                # (see TypeAdapterSQLite)...
                c.hints['precision'] = 14
                c.hints['scale'] = 14
            elif c.dbtype.startswith("NUMERIC"):
                # numeric precision is in decimal digits
                # (SQLite uses 64-bit floats for all numbers)
                c.hints['precision'] = 14
                c.hints['scale'] = 14
            elif c.dbtype == "REAL":
                # float precision is in binary digits
                c.hints['precision'] = 53
            
            # !@#$%^&. SQLite actually FORCES any "INTEGER PRIMARY KEY"
            # column to autoincrement when you insert NULL.
            # See http://sqlite.org/faq.html#q1.
            if c.dbtype == "INTEGER" and c.key:
                c.autoincrement = True
            
            cols.append(c)
        
        return cols
    
    def _get_indices(self, tablename, conn=None):
        data, _ = self.fetch("SELECT name, tbl_name, sql FROM sqlite_master "
                             "WHERE type = 'index';")
        indices = []
        for row in data:
            if row[2]:
                colname = row[2].split("(")[-1]
                i = db.Index(row[0], self.quote(row[0]), row[1], colname[1:-2])
                indices.append(i)
        return indices
    
    def python_type(self, dbtype):
        """Return a Python type which can store values of the given dbtype."""
        if isinstance(self.typeadapter, TypeAdapterSQLiteTypeless):
            return str
        
        if dbtype == "REAL":
            return float
        elif dbtype == "NUMERIC":
            if db.decimal:
                return db.decimal.Decimal
            elif db.fixedpoint:
                return db.fixedpoint.FixedPoint
        elif dbtype.startswith("INTEGER"):
            return int
        elif dbtype == "NONE":
            return unicode
        
        return str
    
    def create_sequence(self, table, column):
        """Create a SEQUENCE for the given column and set its sequence_name."""
        sname = column.sequence_name
        if sname is None:
            column.sequence_name = sname = table.name
        
        # SQLite AUTOINCREMENT columns start at 1 by default.
        # Manhandle the special SQLITE_SEQUENCE table to include
        # the value of sequencer.initial - 1.
        prev = column.initial - 1
        data, coldefs = self.fetch("SELECT * FROM SQLITE_SEQUENCE "
                                   "WHERE name = '%s';" % sname)
        if data:
            self.execute("UPDATE SQLITE_SEQUENCE SET seq = %s "
                         "WHERE name = '%s';" % (prev, sname))
        else:
            self.execute("INSERT INTO SQLITE_SEQUENCE (seq, name) "
                         "VALUES (%s, '%s');" % (prev, sname))
    
    def drop_sequence(self, column):
        """Drop a SEQUENCE for the given column and remove its sequence_name."""
        if column.sequence_name is not None:
            self.execute("DELETE FROM SQLITE_SEQUENCE WHERE name = '%s';"
                         % column.sequence_name)
            column.sequence_name = None
    
    def col_def(self, column):
        """Return a clause for the given column for CREATE or ALTER TABLE.
        
        This will be of the form:
            "name type [DEFAULT x | PRIMARY KEY AUTOINCREMENT]"
        """
        dbtype = coldef = column.dbtype
        
        if column.autoincrement:
            coldef = "INTEGER PRIMARY KEY AUTOINCREMENT"
        else:
            default = column.default or ""
            if not isinstance(default, str):
                default = self.adaptertosql.coerce(default, dbtype)
            if default:
                coldef += " DEFAULT %s" % default
        
        return '%s %s' % (column.qname, coldef)
    
    def __setitem__(self, key, table):
        if key in self:
            del self[key]
        
        # Set table.db to self, which should "turn on"
        # any future ALTER TABLE statements.
        table.db = self
        
        fields = []
        pk = []
        autoincr_col = None
        for col in table.itervalues():
            fields.append(self.col_def(col))
            
            if col.autoincrement:
                # MUST create the sequence after the table is created,
                # or we get into a "no such table" loop inside execute.
                autoincr_col = col
            
            if col.key:
                pk.append(col.qname)
        
        if (autoincr_col is None) and pk:
            # Seems we can't have both an AUTOINCREMENT and another PK
            pk = ", PRIMARY KEY (%s)" % ", ".join(pk)
        else:
            pk = ""
        
        self.lock("Creating storage. Transactions not allowed.")
        try:
            self.execute('CREATE TABLE %s (%s%s);' %
                         (table.qname, ", ".join(fields), pk))
            
            for index in table.indices.itervalues():
                self.execute('CREATE INDEX %s ON %s (%s);' %
                             (index.qname, table.qname,
                              self.quote(index.colname)))
            
            if autoincr_col:
                self.create_sequence(table, autoincr_col)
            
            dict.__setitem__(self, key, table)
        finally:
            self.unlock()
    
    def _rename(self, oldtable, newtable):
        if _rename_table_support:
            self.execute("ALTER TABLE %s RENAME TO %s" %
                         (oldtable.qname, newtable.qname))
        else:
            raise NotImplementedError
    
    def quote(self, name):
        """Return name, quoted for use in an SQL statement.
        
        From the SQLite docs:
            Keywords can be used as identifiers in three ways:
            'keyword'   Interpreted as a literal string if it occurs in a
                        legal string context, otherwise as an identifier.
            "keyword"   Interpreted as an identifier if it matches a known
                        identifier and occurs in a legal identifier context,
                        otherwise as a string.
            [keyword]   Always interpreted as an identifier.
        
        ...we'll use the third option (square brackets).
        """
        return "[" + name + "]"
    
    def connect(self):
        if self.name == ":memory:":
            # "Multiple connections to ":memory:" within a single process
            # create a fresh database each time"
            # http://www.sqlite.org/cvstrac/wiki?p=InMemoryDatabase
            # So we need to give :memory: databases a SingleConnection.
            self.connection = db.SingleConnection(self._get_conn, self._del_conn)
        else:
            return db.Database.connect(self)
    
    if _cursor_required:
        def _get_conn(self):
            # SQLite should create the DB if missing.
            # valid _sqlite3 kwargs: "database", "timeout", "detect_types",
            # "isolation_level", "check_same_thread", "factory",
            # "cached_statements".
            # Instead of "timeout", we re-use the old
            # deadlock_timeout code inside execute.
            conn = _sqlite.connect(database=self.name, check_same_thread=False)
##            # None sets autocommit mode on.
##            conn.isolation_level = None
            conn.text_factory = str
            return conn.cursor()
    else:
        def _get_conn(self):
            return _sqlite.connect(self.name, self.mode)
    
    create_database = _get_conn
    
    def drop_database(self):
        self.disconnect()
        if self.name != ":memory:":
            # This should accept relative or absolute paths
            os.remove(self.name)
        self.clear()
    
    
    #                            Transactions                             #
    
    default_isolation = "SERIALIZABLE"
    isolation_levels = ["SERIALIZABLE"]
    
    def is_lock_error(self, exc):
        if not isinstance(exc, _sqlite.OperationalError):
            return False
        return exc.args[0] == 'database is locked'
    
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
            # This base class uses the four ANSI names as native values.
            isolation = isolation.name
        
        if isolation not in self.isolation_levels:
            raise ValueError("IsolationLevel %r not allowed by %s. "
                             "Try one of %r instead."
                             % (isolation, self.__class__.__name__,
                                self.isolation_levels))
        
        # Nothing to do here, since we only allow one level.
        pass
    
    def start(self, isolation=None):
        """Start a transaction."""
        conn = self.get_transaction(new=True)
        self.execute("BEGIN;", conn)
        self.isolate(conn, isolation)
    
    def rollback(self):
        """Roll back the current transaction."""
        key = self.transaction_key()
        if key in self.transactions:
            self.execute("ROLLBACK;", self.transactions[key])
            del self.transactions[key]
    
    def commit(self):
        """Commit the current transaction."""
        key = self.transaction_key()
        if key in self.transactions:
            self.execute("COMMIT;", self.transactions[key])
            del self.transactions[key]
    
    deadlock_timeout = 20
    
    def execute(self, query, conn=None):
        try:
            if conn is None:
                conn = self.connection()
            if isinstance(query, unicode):
                query = query.encode(self.adaptertosql.encoding)
            self.log(query)
            start = time.time()
            while True:
                try:
                    return conn.execute(query)
                except (_sqlite.OperationalError, _sqlite.DatabaseError), x:
                    msg = x.args[0]
                    if ((msg.startswith("no such") or
                         msg == "database schema has changed")):
                        tx = self.transactions.get(self.transaction_key())
                        if tx is None or isinstance(tx, db.TransactionLock):
                            # Bah. Shut down all connections and get a new one,
                            # since some previous connection changed the schema.
                            self.connection.shutdown()
                            conn = self.connection()
                            continue
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
        if _fetchall_required:
            res = self.execute(query, conn)
            data = res.fetchall()
            coldefs = [(c[0], c[1]) for c in res.description]
            return data, coldefs
        else:
            res = self.execute(query, conn)
            return res.row_list, res.col_defs


class StorageManagerSQLite(db.StorageManagerDB):
    """StoreManager to save and retrieve Units via _sqlite."""
    
    databaseclass = SQLiteDatabase
    
    def __init__(self, arena, allOptions={}):
        allOptions = allOptions.copy()
        dbfile = allOptions.pop('Database', '')
        if dbfile != ':memory:':
            if not os.path.isabs(dbfile):
                dbfile = os.path.join(os.getcwd(), dbfile)
        allOptions['name'] = dbfile
        allOptions['mode'] = int(allOptions.pop('Mode', '0755'), 8)
        db.StorageManagerDB.__init__(self, arena, allOptions)
        pd = str(allOptions.get('Perfect Dates', 'False')).lower() == "true"
        self.databaseclass.using_perfect_dates = pd
        self.databaseclass.adaptertosql.using_perfect_dates = pd
    
    def version(self):
        return "SQLite Version: %s" % _version
    
    def _join(self, unitjoin):
        on_clauses = []
        
        cls1, cls2 = unitjoin.class1, unitjoin.class2
        if isinstance(cls1, dejavu.UnitJoin):
            name1, oc = self._join(cls1)
            on_clauses.extend(oc)
            classlist1 = iter(cls1)
        else:
            # cls1 is a Unit class wrapper.
            name1 = cls1.joinname
            classlist1 = [cls1]
        
        if isinstance(cls2, dejavu.UnitJoin):
            name2, oc = self._join(cls2)
            on_clauses.extend(oc)
            classlist2 = iter(cls2)
        else:
            # cls2 is a Unit class wrapper.
            name2 = cls2.joinname
            classlist2 = [cls2]
        
        if unitjoin.leftbiased is None:
            j = "%s INNER JOIN %s" % (name1, name2)
        elif unitjoin.leftbiased is True:
            j = "%s LEFT JOIN %s" % (name1, name2)
        else:
            # My version (3.0.8) of SQLite says:
            # "RIGHT and FULL OUTER JOINs are not currently supported".
            j = "%s LEFT JOIN %s" % (name2, name1)
        
        # Find an association between the two halves.
        ua = None
        for wrapperA in classlist1:
            for wrapperB in classlist2:
                path = unitjoin.path or wrapperB.cls.__name__
                ua = wrapperA.cls._associations.get(path, None)
                if ua:
                    nearTable, farTable = wrapperA, wrapperB
                    break
                path = unitjoin.path or wrapperA.cls.__name__
                ua = wrapperB.cls._associations.get(path, None)
                if ua:
                    nearTable, farTable = wrapperB, wrapperA
                    break
            if ua:
                break
        if ua is None:
            raise AssociationError("No association found between %s and %s."
                                   % (name1, name2))
        
        near = '%s.%s' % (nearTable.alias or nearTable.table.qname,
                          nearTable.table[ua.nearKey].qname)
        far = '%s.%s' % (farTable.alias or farTable.table.qname,
                         farTable.table[ua.farKey].qname)
        
        on_clauses.append("%s = %s" % (near, far))
        return j, on_clauses
    
    def join(self, unitjoin):
        # SQLite doesn't do nested JOINs, but instead applies
        # them in order. Therefore, we need a single ON-clause
        # at the end of the list of tables. For example:
        # "From a LEFT JOIN b LEFT JOIN c ON a.ID = b.ID AND b.Name = c.Name"
        joins, on_clauses = self._join(unitjoin)
        return joins + " ON " + " AND ".join(on_clauses)
    
    def reserve(self, unit):
        """reserve(unit). -> Reserve a persistent slot for unit."""
        self.reserve_lock.acquire()
        try:
            # First, see if our db subclass has a handler that
            # uses the DB to generate the appropriate identifier(s).
            seqclass = unit.sequencer.__class__.__name__
            if seqclass == "UnitSequencerInteger" and _autoincrement_support:
                self._seq_UnitSequencerInteger(unit)
            else:
                self._manual_reserve(unit)
            unit.cleanse()
        finally:
            self.reserve_lock.release()
    
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
        
        fields = ", ".join(fields)
        values = ", ".join(values)
        
        # Use the same conn for INSERT and last row id
        conn = self.db.get_transaction()
        self.db.execute('INSERT INTO %s (%s) VALUES (%s);' %
                        (t.qname, fields, values), conn)
        
        # Grab the new ID. This is safe because db.reserve has a mutex.
        if _lastrowid_support:
            new_id = conn.lastrowid
        else:
            new_id = conn.sqlite_last_insert_rowid()
        setattr(unit, cls.identifiers[0], new_id)
    
    #                               Schemas                               #
    
    def _make_column(self, cls, key):
        col = db.StorageManagerDB._make_column(self, cls, key)
        if col.autoincrement and not _autoincrement_support:
            col.autoincrement = False
            col.initial = 0
        return col

