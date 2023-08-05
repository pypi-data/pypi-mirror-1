import os

import dejavu
from dejavu import storage, logic
from dejavu.storage import db

# Use _sqlite directly to avoid all of the DB-API overhead.
# This will import the "old API for SQLite 3.x", using e.g. pysqlite 1.1.7
import _sqlite
_version = storage.Version(_sqlite.sqlite_version())

# ESCAPE keyword was added Nov 2004, 1 month after 3.0.8 release.
_escape_support = (_version > storage.Version([3, 0, 8]))
if not _escape_support:
    _escape_warning = ("Version %s of sqlite does not support "
                       "wildcard literals." % _version)
    import warnings
    warnings.warn(_escape_warning, dejavu.StorageWarning)

_add_column_support = (_version >= storage.Version([3, 2, 0]))
_rename_table_support = (_version >= storage.Version([3, 1, 0]))


class AdapterToSQLite(db.AdapterToSQL):
    
    like_escapes = [("%", "\%"), ("_", "\_")]
    
    bool_true = "1"
    bool_false = "0"
    
    def coerce_bool(self, value):
        if value:
            return '1'
        return '0'


class AdapterFromSQLite(db.AdapterFromDB):
    
    def coerce_bool(self, value, coltype):
        # sqlite 2 will return a string, either '0' or '1'.
        if isinstance(value, basestring):
            return (value == '1')
        # sqlite 3 will return an int.
        return bool(value)


class SQLiteDecompiler(db.SQLDecompiler):
    
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
        self.imperfect = True
        return db.cannot_represent
    
    dejavu_today = dejavu_now
    
    def dejavu_year(self, x):
        self.imperfect = True
        return db.cannot_represent


class StorageManagerSQLite(db.StorageManagerDB):
    """StoreManager to save and retrieve Units via _sqlite."""
    
    sql_name_max_length = 0
    decompiler = SQLiteDecompiler
    toAdapter = AdapterToSQLite()
    fromAdapter = AdapterFromSQLite()
    
    def __init__(self, name, arena, allOptions={}):
        db.StorageManagerDB.__init__(self, name, arena, allOptions)
        
        dbfile = allOptions.get(u'Database', '')
        if not os.path.isabs(dbfile):
            dbfile = os.path.join(os.getcwd(), dbfile)
        self.database = dbfile
        
        self.mode = int(allOptions.get(u'Mode', '0755'), 8)
    
    def sql_name(self, name, quoted=True):
        """sql_name(name, quoted=True) -> return name as a legal SQL identifier.
        
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
        if quoted:
            name = "[" + name + "]"
        return name
    
    def _get_conn(self):
        # SQLite should create the DB if missing.
        return _sqlite.connect(self.database, self.mode)
    
    def version(self):
        return "SQLite Version: %s" % _version
    
    def execute(self, query, conn=None):
        try:
            if conn is None:
                conn = self.connection()
            self.arena.log(query, dejavu.LOGSQL)
            return conn.execute(query.encode('utf8'))
            #           ^^^^^^^
        except Exception, x:
            x.args += (query,)
            # Dereference the connection so that release() is called back.
            conn = None
            raise
    
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
        for clsA in classlist1:
            ua = clsA.association(classlist2)
            if ua:
                ua, nearClass, farClass = ua
                break
        if ua is None:
            msg = ("No association found between %s and %s." % (name1, name2))
            raise dejavu.AssociationError(msg)
        near = '%s.%s' % (nearClass, self.column_name(nearClass, ua.nearKey))
        far = '%s.%s' % (farClass, self.column_name(farClass, ua.farKey))
        
        on_clauses.append("%s = %s" % (near, far))
        return j, on_clauses
    
    def join(self, unitjoin):
        # SQLite doesn't do nested JOINs, but instead applies them
        # in order. Therefore, we need a single ON-clause at the
        # end of the list of tables. For example:
        # "From a LEFT JOIN b LEFT JOIN c ON a.ID = b.ID AND b.Name = c.Name
        joins, on_clauses = self._join(unitjoin)
        return joins + " ON " + " AND ".join(on_clauses)
    
    #                               Schemas                               #
    
    create_database = _get_conn
    
    def drop_database(self):
        self.shutdown()
        # This should accept relative or absolute paths
        os.remove(self.database)
    
    def create_storage(self, cls):
        clsname = cls.__name__
        tablename = self.table_name(clsname)
        
        # SQLite is typeless.
        fields = [self.column_name(clsname, key) for key in cls.properties()]
        
        self.execute(u'CREATE TABLE %s (%s);' % (tablename, ", ".join(fields)))
        for index in cls.indices():
            i = self.table_name("i" + clsname + index)
            self.execute(u'CREATE INDEX %s ON %s (%s);' %
                         (i, tablename, self.column_name(clsname, index)))
    
    def add_property(self, cls, name):
        clsname = cls.__name__
        
        if _add_column_support:
            self.execute("ALTER TABLE %s ADD COLUMN %s;" %
                         (self.table_name(clsname),
                          self.column_name(clsname, name)))
        else:
            tablename = self.table_name(clsname, quoted=False)
            
            # Create a temporary table with the new schema (no indices).
            # The schema should already be changed in the model layer.
            props = list(cls.properties())
            fields = ", ".join([self.column_name(clsname, key) for key in props])
            self.execute("CREATE TABLE [temp_%s] (%s);" % (tablename, fields))
            oldfields = []
            for key in props:
                if key == name:
                    oldfields.append(self.toAdapter.coerce(None))
                else:
                    oldfields.append(self.column_name(clsname, key))
            self.execute("INSERT INTO [temp_%s] SELECT %s FROM [%s];" %
                         (tablename, ", ".join(oldfields), tablename))
            
            # Drop and re-create the old table.
            self.execute("DROP TABLE [%s];" % tablename)
            self.create_storage(cls)
            self.execute("INSERT INTO [%s] SELECT * FROM [temp_%s];" %
                         (tablename, tablename))
            self.execute("DROP TABLE [temp_%s];" % tablename)
    
    def drop_property(self, cls, name):
        clsname = cls.__name__
        tablename = self.table_name(clsname, quoted=False)
        
        # Create a temporary table with the new schema (no indices).
        # The schema should already be changed in the model layer.
        fields = ", ".join([self.column_name(clsname, key)
                            for key in cls.properties()])
        self.execute("CREATE TABLE [temp_%s] (%s);" % (tablename, fields))
        self.execute("INSERT INTO [temp_%s] SELECT %s FROM [%s];" %
                     (tablename, fields, tablename))
        
        # Drop and re-create the old table.
        self.execute("DROP TABLE [%s];" % tablename)
        self.create_storage(cls)
        self.execute("INSERT INTO [%s] SELECT * FROM [temp_%s];" %
                     (tablename, tablename))
        self.execute("DROP TABLE [temp_%s];" % tablename)
    
    def rename_property(self, cls, oldname, newname):
        clsname = cls.__name__
        tablename = self.table_name(clsname, quoted=False)
        
        # Create a temporary table with the new schema (no indices).
        # The schema should already be changed in the model layer.
        props = list(cls.properties())
        fields = ", ".join([self.column_name(clsname, key) for key in props])
        self.execute("CREATE TABLE [temp_%s] (%s);" % (tablename, fields))
        oldfields = []
        for key in props:
            if key == newname:
                oldfields.append("%s AS %s" % (self.column_name(clsname, oldname),
                                               self.column_name(clsname, newname)))
            else:
                oldfields.append(self.column_name(clsname, key))
        self.execute("INSERT INTO [temp_%s] SELECT %s FROM [%s];" %
                     (tablename, ", ".join(oldfields), tablename))
        
        # Drop and re-create the old table.
        self.execute("DROP TABLE [%s];" % tablename)
        self.create_storage(cls)
        self.execute("INSERT INTO [%s] SELECT * FROM [temp_%s];" %
                     (tablename, tablename))
        self.execute("DROP TABLE [temp_%s];" % tablename)
