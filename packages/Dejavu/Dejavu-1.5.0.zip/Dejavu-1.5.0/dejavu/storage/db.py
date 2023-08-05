"""Base classes and tools for writing database Storage Managers.

DATA TYPES
==========
Database Storage Manager modules are mostly adapters to support round-trip
data coercion:

Unit type -> [SQL repr ->] DB -> incoming Python value -> Unit type

Since Dejavu relies on external database servers for its persistence,
Python datatypes must be converted to column types in the DB. When writing
a StorageManager, you should make sure that your type conversions can handle
at least the following limitations: If possible, implement the type with no
limits. Also, follow UnitProperty.hints['bytes'] where possible. A value
of zero for hints['bytes'] implies no limit. If no value is given, try to
assume no limit, although you may choose whatever default size you wish
(255 is common for strings).

ENCODING ISSUES
===============
All SQL sent to the database must be strings, not unicode. You can set the
encoding of the Adapters (I may add a more centralized encoding context in
the future). We must use encoded strings so that we can mix encodings
within the same string; for example, we might have a DB which understands
utf8, but a pickle value which will be encoded in raw-unicode-escape inline
with that. All values, therefore, must be coerced before we try to join
them into an SQL statement string.

"""


try:
    # Builtin in Python 2.5?
    decimal
except NameError:
    try:
        # Module in Python 2.3, 2.4
        import decimal
    except ImportError:
        decimal = None

try:
    import fixedpoint
except ImportError:
    fixedpoint = None

import threading
import warnings


import dejavu
from dejavu import logic, storage, logflags, xray
from dejavu.errors import *
from dejavu.storage.geniusql import *



# --------------------------- Storage Manager --------------------------- #


class UnitClassWrapper(object):
    """Unit class wrapper, for use in parsing multiselect joins."""
    
    def __init__(self, wclass, table):
        self.cls = wclass
        self.table = table
        # *quoted* alias
        self.alias = ""
    
    def columns(self):
        """Return [(wclass, UnitProperty.key), ...], ['"tbl"."col"', ...]."""
        # Place the identifier properties first
        # in case others depend upon them.
        wclass = self.cls
        keys = list(wclass.identifiers) + [k for k in wclass.properties
                                           if k not in wclass.identifiers]
        cols = [(wclass, k) for k in keys]
        colnames = ['%s.%s' % (self.alias or self.table.qname,
                               self.table[k].qname)
                    for k in keys]
        return cols, colnames
    
    def _joinname(self):
        if self.alias:
            return "%s AS %s" % (self.table.qname, self.alias)
        else:
            return self.table.qname
    joinname = property(_joinname, doc=("Quoted table name for use in "
                                        "JOIN clause (read-only)."))


class StorageManagerDB(storage.StorageManager):
    """StoreManager base class to save and retrieve Units using a DB."""
    
    use_asterisk_to_get_all = False
    databaseclass = Database
    joinwrapper = UnitClassWrapper
    
    def __init__(self, arena, allOptions={}):
        storage.StorageManager.__init__(self, arena, allOptions)
        self.reserve_lock = threading.Lock()
        
        # Adapter Overrides
        def get_option(name):
            item = allOptions.get(name)
            if isinstance(item, basestring):
                item = xray.classes(item)
            return item
        
        adapter = get_option('Database Class')
        if adapter:
            self.databaseclass = adapter
        
        allOptions = dict([(str(k), v) for k, v in allOptions.iteritems()])
        
        name = allOptions.pop('name')
        self.db = self.databaseclass(name, **allOptions)
        
        def logger(msg):
            if self.arena.logflags & logflags.SQL:
                self.arena.log(msg)
        self.db.log = logger
        
        adapter = get_option('Type Adapter')
        if adapter:
            self.db.typeadapter = adapter()
    
    def version(self):
        return self.db.version()
    
    def shutdown(self):
        self.db.disconnect()
    
    def consume(self, unit, key, value, dbtype):
        """Set 'value' (of type 'dbtype') as a valid property on the unit."""
        try:
            prop = getattr(unit.__class__, key)
            cvalue = self.db.adapterfromdb.coerce(value, dbtype, prop.type)
            if prop.coerce:
                cvalue = prop.coerce(unit, cvalue)
            unit._properties[key] = cvalue
        except UnicodeDecodeError, x:
            x.reason += "[%s][%s][%s]" % (key, value, dbtype)
            raise
        except Exception, x:
            x.args += (key, value, dbtype)
            raise
    
    def recall(self, cls, expr=None):
        """Yield a sequence of Unit instances which satisfy the expression."""
        clsname = cls.__name__
        
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        sql, imperfect = self.db.select(cls.__name__, expr)
        data, col_defs = self.db.fetch(sql, self.db.get_transaction())
        if data:
            t = self.db[clsname]
            colnames = [col[0] for col in col_defs]
            
            # Get specs on properties. Put the identifier properties
            # first, in case other fields depend upon them.
            props = []
            idnames = list(cls.identifiers)
            for key in idnames + [x for x in cls.properties if x not in idnames]:
                col = t[key]
                prop = getattr(cls, key)
                props.append((key, colnames.index(col.name),
                              col.dbtype, prop.type, prop.coerce))
            coerce = self.db.adapterfromdb.coerce
            
            for row in data:
                unit = cls.__new__(cls)
                unit._zombie = True
                unit.__init__()
                for key, index, dbtype, pytype, propcoerce in props:
                    value = row[index]
                    # Inline the consume call for speed.
                    try:
                        cvalue = coerce(value, dbtype, pytype)
                        if propcoerce:
                            cvalue = propcoerce(unit, cvalue)
                        unit._properties[key] = cvalue
                    except UnicodeDecodeError, x:
                        x.reason += "[%s][%s][%s]" % (key, value, dbtype)
                        raise
                    except Exception, x:
                        x.args += (key, value, dbtype)
                        raise
                
                # If our SQL is imperfect, don't yield it to the
                # caller unless it passes expr(unit).
                if (not imperfect) or expr(unit):
                    unit.cleanse()
                    yield unit
    
    def reserve(self, unit):
        """reserve(unit). -> Reserve a persistent slot for unit."""
        self.reserve_lock.acquire()
        try:
            # First, see if our db subclass has a handler that
            # uses the DB to generate the appropriate identifier(s).
            seqclass = unit.sequencer.__class__.__name__
            seq_handler = getattr(self, "_seq_%s" % seqclass, None)
            if seq_handler:
                seq_handler(unit)
            else:
                self._manual_reserve(unit)
            unit.cleanse()
        finally:
            self.reserve_lock.release()
    
    def _manual_reserve(self, unit):
        """Use when the DB cannot automatically generate an identifier.
        The identifiers will be supplied by UnitSequencer.assign().
        """
        cls = unit.__class__
        t = self.db[cls.__name__]
        if not unit.sequencer.valid_id(unit.identity()):
            # Examine all existing IDs and grant the "next" one.
            id_cols = [t[key] for key in cls.identifiers]
            data, _ = self.db.fetch('SELECT %s FROM %s;' %
                                    (', '.join([x.qname for x in id_cols]),
                                     t.qname),
                                    self.db.get_transaction())
            if data:
                # sqlite 2, for example, has empty cols tuple if no data.
                coerce = self.db.adapterfromdb.coerce
                pytypes = [getattr(cls, key).type for key in cls.identifiers]
                coerced_data = []
                for row in data:
                    cdata = [coerce(cell, id_cols[x].dbtype, pytypes[x])
                             for x, cell in enumerate(row)]
                    coerced_data.append(cdata)
                cls.sequencer.assign(unit, coerced_data)
                del coerced_data
                del data
            else:
                cls.sequencer.assign(unit, [])
        
        fields = []
        values = []
        for key in cls.properties:
            col = t[key]
            val = self.db.adaptertosql.coerce(getattr(unit, key), col.dbtype)
            fields.append(col.qname)
            values.append(val)
        
        fields = ", ".join(fields)
        values = ", ".join(values)
        self.db.execute('INSERT INTO %s (%s) VALUES (%s);' %
                        (t.qname, fields, values),
                        self.db.get_transaction())
    
    def id_clause(self, unit):
        """Return an SQL expression for the identifiers of the given Unit."""
        cols = self.db[unit.__class__.__name__]
        c = self.db.adaptertosql.coerce
        pairs = []
        for key in unit.identifiers:
            col = cols[key]
            val = c(getattr(unit, key), col.dbtype)
            pairs.append("%s = %s" % (col.qname, val))
        return " AND ".join(pairs)
    
    def save(self, unit, forceSave=False):
        """save(unit, forceSave=False) -> Update storage from unit's data."""
        if unit.dirty() or forceSave:
            cls = unit.__class__
            t = self.db[cls.__name__]
            
            coerce = self.db.adaptertosql.coerce
            parms = []
            for key in cls.properties:
                if key not in cls.identifiers:
                    col = t[key]
                    val = getattr(unit, key)
                    val = coerce(val, col.dbtype)
                    parms.append('%s = %s' % (col.qname, val))
            
            if parms:
                sql = ('UPDATE %s SET %s WHERE %s;' %
                       (t.qname, ", ".join(parms), self.id_clause(unit)))
                self.db.execute(sql, self.db.get_transaction())
            unit.cleanse()
    
    def destroy(self, unit):
        """destroy(unit). Delete the unit."""
        if self.use_asterisk_to_get_all:
            star = " *"
        else:
            star = ""
        self.db.execute('DELETE%s FROM %s WHERE %s;' %
                        (star, self.db[unit.__class__.__name__].qname,
                         self.id_clause(unit)),
                        self.db.get_transaction())
    
    def _view(self, cls, fields, sql):
        data, _ = self.db.fetch(sql, self.db.get_transaction())
        t = self.db[cls.__name__]
        
        # Pre-calc inner loop data.
        metadata = []
        for i, f in enumerate(fields):
            prop = getattr(cls, f)
            metadata.append((i, t[f].dbtype, prop.type, prop.coerce))
        
        coerce = self.db.adapterfromdb.coerce
        # Use tuples for hashability
        for row in data:
            coerced_row = []
            for i, dbtype, ptype, propcoerce in metadata:
                val = coerce(row[i], dbtype, ptype)
                if propcoerce:
                    val = propcoerce(None, val)
                coerced_row.append(val)
            yield tuple(coerced_row)
    
    def view(self, cls, fields, expr=None):
        """view(cls, fields, expr=None) -> All value-tuples for given fields."""
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        sql, imperfect = self.db.select(cls.__name__, expr, fields)
        if imperfect:
            # ^%$#@! There's no way to handle imperfect queries without
            # creating all involved Units, which defeats the purpose of
            # view, which was a speed issue more than anything else.
            warnings.warn("The requested view() query for %s Units "
                          "cannot produce perfect SQL with a %s datasource. "
                          "It may take an absurd amount of time to run, "
                          "since each unit must be fully-formed. %s"
                          % (cls.__name__, self.__class__.__name__, expr),
                          StorageWarning)
            units = self.recall(cls, expr)
            # Use tuples for hashability
            return [tuple([getattr(unit, f) for f in fields]) for unit in units]
        else:
            return self._view(cls, fields, sql)
    
    def distinct(self, cls, fields, expr=None):
        """distinct(cls, fields, expr=None) -> Distinct values for given fields."""
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        sql, imperfect = self.db.select(cls.__name__, expr,
                                            fields, distinct=True)
        if imperfect:
            # ^%$#@! There's no way to handle imperfect queries without
            # creating all involved Units, which defeats the purpose of
            # distinct, which was a speed issue more than anything.
            warnings.warn("The requested distinct() query for %s Units "
                          "cannot produce perfect SQL with a %s datasource. "
                          "It may take an absurd amount of time to run, "
                          "since each unit must be fully-formed. %s"
                          % (cls.__name__, self.__class__.__name__, expr),
                          StorageWarning)
            vals = {}
            for unit in self.recall(cls, expr):
                # Must use tuples for hashability
                val = tuple([getattr(unit, f) for f in fields])
                vals[val] = None
            return vals.keys()
        else:
            return self._view(cls, fields, sql)
    
    def join(self, unitjoin):
        """Return an SQL FROM clause for the given unitjoin."""
        cls1, cls2 = unitjoin.class1, unitjoin.class2
        if isinstance(cls1, dejavu.UnitJoin):
            name1 = self.join(cls1)
            classlist1 = iter(cls1)
        else:
            # cls1 is a Unit class wrapper.
            name1 = cls1.joinname
            classlist1 = [cls1]
        
        if isinstance(cls2, dejavu.UnitJoin):
            name2 = self.join(cls2)
            classlist2 = iter(cls2)
        else:
            # cls2 is a Unit class wrapper.
            name2 = cls2.joinname
            classlist2 = [cls2]
        
        j = {None: "INNER", True: "LEFT", False: "RIGHT"}[unitjoin.leftbiased]
        
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
        
        return "(%s %s JOIN %s ON %s = %s)" % (name1, j, name2, near, far)
    
    def multiselect(self, classes, expr):
        """Return an SQL SELECT statement, an imperfect flag, and column names."""
        
        # Create a new unitjoin tree where each class is wrapped.
        # Then we can tag the wrappers with metadata with impunity.
        seen = {}
        aliascount = [0]
        q = lambda name: self.db.quote(self.db.table_name(name))
        
        def wrap(unitjoin):
            cls1, cls2 = unitjoin.class1, unitjoin.class2
            if isinstance(cls1, dejavu.UnitJoin):
                wclass1 = wrap(cls1)
            else:
                wclass1 = self.joinwrapper(cls1, self.db[cls1.__name__])
                if cls1 in seen:
                    aliascount[0] += 1
                    wclass1.alias = q("t%d" % aliascount[0])
                else:
                    seen[cls1] = None
            if isinstance(cls2, dejavu.UnitJoin):
                wclass2 = wrap(cls2)
            else:
                wclass2 = self.joinwrapper(cls2, self.db[cls2.__name__])
                if cls2 in seen:
                    aliascount[0] += 1
                    wclass2.alias = q("t%d" % aliascount[0])
                else:
                    seen[cls2] = None
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
        
        statement = ("SELECT %s FROM %s WHERE %s" %
                     (', '.join(colnames), joins, w))
        return statement, imp, cols
    
    def multirecall(self, classes, expr):
        """Yield Unit instance sets which satisfy the expression."""
        sql, imp, supplied_cols = self.multiselect(classes, expr)
        data, _ = self.db.fetch(sql, self.db.get_transaction())
        if data:
            # Get specs on properties.
            props = [(cls, key, self.db[cls.__name__][key].dbtype)
                     for cls, key in supplied_cols]
            
            for row in data:
                index = 0
                units = {}
                for cls, key, dbtype in props:
                    if cls in units:
                        unit = units[cls]
                    else:
                        units[cls] = unit = cls()
                    value = row[index]
                    self.consume(unit, key, value, dbtype)
                    index += 1
                
                unitset = []
                for cls in classes:
                    unit = units[cls]
                    unit.cleanse()
                    unitset.append(unit)
                
                # If our SQL is imperfect, don't yield units to the
                # caller unless they pass expr(unit).
                acceptable = True
                if imp:
                    acceptable = expr(*unitset)
                if acceptable:
                    yield unitset
    
    #                               Schemas                               #
    
    def create_database(self):
        self.db.create_database()
    
    def drop_database(self):
        self.db.drop_database()
    
    def _make_table(self, cls):
        """Create and return a Table object for the given class."""
        db = self.db
        clsname = cls.__name__
        
        # Make a Table object.
        name = db.table_name(clsname)
        t = db.tableclass(name, db.quote(name))
        
        indices = cls.indices()
        fields = []
        for key in cls.properties:
            t[key] = self._make_column(cls, key)
            if key in indices:
                i = db.make_index(clsname, key)
                t.indices[key] = i
        
        return t
    
    def create_storage(self, cls):
        """Create storage for the given class."""
        # Attach to self.db, which should call CREATE TABLE.
        self.db[cls.__name__] = self._make_table(cls)
    
    def _make_column(self, cls, key):
        prop = getattr(cls, key)
        col = self.db.make_column(cls.__name__, key, prop.type,
                                  prop.default, prop.hints)
        if key in cls.identifiers:
            col.key = True
            if isinstance(cls.sequencer, dejavu.UnitSequencerInteger):
                col.autoincrement = True
                col.initial = cls.sequencer.initial
        return col
    
    def has_storage(self, cls):
        return cls.__name__ in self.db
    
    def drop_storage(self, cls):
        del self.db[cls.__name__]
    
    def rename_storage(self, oldname, newname):
        self.db.rename(oldname, newname)
    
    def add_property(self, cls, name):
        if not self.has_property(cls, name):
            table = self.db[cls.__name__]
            table[name] = self._make_column(cls, name)
    
    def has_property(self, cls, name):
        return name in self.db[cls.__name__]
    
    def drop_property(self, cls, name):
        if self.has_property(cls, name):
            del self.db[cls.__name__][name]
    
    def rename_property(self, cls, oldname, newname):
        t = self.db[cls.__name__]
        
        # Sometimes, a schema will change a code model first, and then
        # change the database afterward. So it's possible that the
        # column we're trying to rename hasn't been loaded, because the
        # model layer no longer references it. So if table[oldname]
        # raises a KeyError, try to find a column that matches oldkey.
        tempcol = None
        try:
            t[oldname]
        except KeyError:
            c = [x for x in self.db._get_columns(t.name)
                 if x.name == self.db.column_name(cls.__name__, oldname)]
            if not c:
                raise KeyError("Rename failed. Old column %r not found in %r."
                               % (oldname, t.name))
            oldcol = c[0]
            pytype1 = self.db.python_type(oldcol.dbtype)
            # Note we use newname, which assumes that property is in the class.
            pytype2 = getattr(cls, newname).type
            oldcol.imperfect_type = not self.db.isrelatedtype(pytype1, pytype2)
            # Use the superclass call to avoid DROP COLUMN/ADD COLUMN.
            dict.__setitem__(t, oldname, oldcol)
        
        t.rename(oldname, newname)
    
    def add_index(self, cls, name):
        i = self.db.make_index(cls.__name__, name)
        self.db[cls.__name__].indices[name] = i
    
    def has_index(self, cls, name):
        return name in self.db[cls.__name__].indices
    
    def drop_index(self, cls, name):
        del self.db[cls.__name__].indices[name]
    
    auto_discover = True
    
    def map(self, classes, warn=False):
        """Map classes to Table objects (if not found).
        
        If self.auto_discover is True (the default), then Table/Column/Index
        objects will be formed by inspecting the underlying database.
        If auto_discover is False, then mock Table/Column/Index objects
        will be used instead; this provides a performance improvement
        in scenarios where the model maps perfectly to the database
        and changes to the database are not expected outside the model.
        
        If 'warn' is True, then any mapping errors are replaced by warnings.
        This allows you to see all errors at once, without having to stop
        and fix each one and then re-execute the process.
        """
        if self.auto_discover:
            self.sync(classes, warn)
        else:
            for cls in classes:
                clsname = cls.__name__
                if clsname in self.db:
                    # If our consumer-side key is already present, skip this cls.
                    # This allows arena.storage() to auto-sync class by class
                    # without making a new Table object each time.
                    continue
                
                t = self._make_table(cls)
                
                # Use the superclass call to avoid DROP/CREATE TABLE
                dict.__setitem__(self.db, clsname, t)
    
    def sync(self, classes, warn=False):
        """Map classes to existing Table objects (found via discovery).
        
        If a matching Table/Column/Index cannot be found, KeyError is raised.
        
        If 'warn' is True, then a warning is raised instead of an error.
        This allows you to see all errors at once, without having to stop
        and fix each one and then re-execute the process.
        """
        for cls in classes:
            clsname = cls.__name__
            
            if clsname in self.db:
                # If our consumer-side key is already present, skip this cls.
                # This allows arena.storage() to auto-sync class by class
                # without calling the expensive discover() func each time.
                continue
            
            # Try to find a matching Table object using the DB-side key.
            tablename = self.db.table_name(clsname)
            try:
                # Do we already have a map?
                table = self.db[tablename]
            except KeyError:
                # Can we create a map? Discover the DB table and try again.
                try:
                    table = self.db.discover(tablename)
                except MappingError:
                    msg = "%s: no such table %r." % (clsname, tablename)
                    if warn:
                        warnings.warn(msg)
                        continue
                    else:
                        raise MappingError(msg)
            
            self.db.alias(table.name, clsname)
            
            # Match Column objects with class properties.
            dbcols = dict([(c.name, c) for c in table.itervalues()])
            indices = cls.indices()
            for ckey in cls.properties:
                colname = self.db.column_name(clsname, ckey)
                try:
                    col = dbcols[colname]
                except KeyError, x:
                    msg = "%s: no matching column found for %r." % (clsname, ckey)
                    if warn:
                        warnings.warn(msg)
                        continue
                    else:
                        raise MappingError(msg)
                
                # Set imperfect_type
                pytype1 = self.db.python_type(col.dbtype)
                pytype2 = getattr(cls, ckey).type
                col.imperfect_type = not self.db.isrelatedtype(pytype1, pytype2)
                
                table.alias(col.name, ckey)
                
                # Try to find matching Index objects. Because index names are
                # so platform-specific, we match attributes rather than names.
                if ckey in indices:
                    for idx in table.indices.itervalues():
                        if idx.colname == colname:
                            a = self.db.table_name("i" + clsname + ckey)
                            table.indices.alias(idx.name, a)
                            break
                    else:
                        msg = ("%s: no matching index found for %r."
                               % (clsname, ckey))
                        if warn:
                            warnings.warn(msg)
                        else:
                            raise MappingError(msg)
    
    #                            Transactions                             #
    
    def start(self, isolation=None):
        """Start a transaction. Not needed if self.implicit_trans is True."""
        self.db.start(isolation)
    
    def rollback(self):
        """Roll back the current transaction."""
        self.db.rollback()
    
    def commit(self):
        """Commit the current transaction."""
        self.db.commit()


class Modeler(object):
    """Tool to automatically form Unit classes or source from existing DB's."""
    
    ignore = ['Unit', 'DeployedVersion',
              'UnitEngine', 'UnitEngineRule', 'UnitCollection',
              ]
    
    def __init__(self, db):
        self.db = db
        self.ignore = self.ignore[:]
    
    def all_classes(self):
        """Return a list of new classes for all tables in the Database."""
        self.db.discover_all()
        
        classes = []
        
        ignore = dict.fromkeys([self.db.table_name(x) for x in self.ignore]
                               + self.ignore).keys()
        
        seen = {}
        for key, table in self.db.items():
            if key not in ignore and table.name not in seen:
                cls = self.make_class(key)
                classes.append(cls)
                seen[table.name] = None
        return classes
    
    def make_class(self, tablename, newclassname=None):
        """Create a Unit class automatically from the named table."""
        if tablename not in self.db:
            self.db.discover(tablename)
        table = self.db[tablename]
        
        class AutoUnitClass(dejavu.Unit):
            sequencer = dejavu.UnitSequencer()
            identifiers = tuple([k for k in table if table[k].key])
        
        if newclassname is None:
            newclassname = table.name
            # The key is probably better than the table.name. Try it.
            for key, t in self.db.iteritems():
                if t.name == newclassname:
                    newclassname = key
                    break
        AutoUnitClass.__name__ = newclassname
        
        for cname, c in table.iteritems():
            ptype = self.db.python_type(c.dbtype)
            if ptype == int and c.hints.get('bytes') in (1, '1'):
                # This is probably a bool
                ptype = bool
                del c.hints['bytes']
            p = AutoUnitClass.set_property(cname, ptype)
            if c.autoincrement:
                AutoUnitClass.sequencer = dejavu.UnitSequencerInteger(int, c.initial)
            p.default = c.default
            p.hints = c.hints.copy()
            p.index = (cname in table.indices)
        
        return AutoUnitClass
    
    def all_source(self):
        """Return a list of strings, of Unit source code for all tables."""
        self.db.discover_all()
        
        allcode = []
        
        ignore = dict.fromkeys([self.db.table_name(x) for x in self.ignore]
                               + self.ignore).keys()
        
        seen = {}
        for key, table in self.db.items():
            if key not in ignore and table.name not in seen:
                code = self.make_source(key)
                allcode.append(code)
                seen[table.name] = None
        return allcode
    
    def make_source(self, tablename, newclassname=None):
        """Create source code for a Unit class from the named table."""
        if tablename not in self.db:
            self.db.discover(tablename)
        table = self.db[tablename]
        
        code = []
        
        if newclassname is None:
            newclassname = table.name
            # The key is probably better than the table.name. Try it.
            for key, t in self.db.iteritems():
                if t.name == newclassname:
                    newclassname = key
                    break
            # Make the name safe for use as a Python class name
            newclassname = newclassname.replace(".", "_")
        code.append("class %s(Unit):" % newclassname)
        
        sequencer = None
        for cname, c in table.iteritems():
            ptype = self.db.python_type(c.dbtype)
            if ptype == int and c.hints.get('bytes') in (0, '0', 1, '1'):
                # This is probably a bool
                ptype = bool
                del c.hints['bytes']
            
            mod = ptype.__module__
            if mod == '__builtin__':
                ptype = ptype.__name__
            else:
                ptype = mod + "." + ptype.__name__
            
            if c.autoincrement:
                sequencer = ("    sequencer = UnitSequencerInteger(int, %s)"
                             % c.initial)
            
            default = c.default
            if default is None:
                default = ""
            else:
                default = ", default=%r" % default
            
            index = ""
            if cname in table.indices:
                index = ", index=True"
            
            hints = ""
            if c.hints:
                hints = ", hints=%r" % c.hints
            
            prop = ("    %s = UnitProperty(%s%s%s%s)"
                    % (cname, ptype, index, hints, default))
            if not prop.startswith("    ID = UnitProperty(int"):
                code.append(prop)
        
        # Remove default ID property if necessary.
        if "ID" not in table:
            code.append("    # Remove the default 'ID' property.")
            code.append("    ID = None")
        
        pk = tuple([k for k in table if table[k].key])
        if pk not in [("ID",), ("id",)]:
            code.append("    identifiers = %s" % repr(pk))
        
        if sequencer:
            if sequencer != "    sequencer = UnitSequencerInteger(int, 1)":
                code.append(sequencer)
        else:
            code.append("    sequencer = UnitSequencer()")
        
        if len(code) == 1:
            code.append("    pass")
        
        return "\n".join(code)

