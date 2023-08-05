
import ConfigParser
try:
    set
except NameError:
    from sets import Set as set
import threading
from types import ClassType

from dejavu.containers import Graph
from dejavu import logic, errors, storage, xray

__all__ = ['Arena', 'Sandbox', 'logflags',
           ]


class Enum(object):
    pass

# logging flags (see Arena.logflags)
logflags = Enum()
logflags.ERROR = 1
logflags.IO = 2
logflags.SQL = 4

logflags.MEMORIZE = 128
logflags.RECALL = 256
logflags.VIEW = 512
logflags.REPRESS = 1024
logflags.FORGET = 2048
logflags.SANDBOX = (logflags.MEMORIZE | logflags.RECALL | logflags.VIEW |
                    logflags.REPRESS | logflags.FORGET)


class Arena(object):
    """A namespace/workspace for a Dejavu application."""
    
    def __init__(self):
        self.stores = {}
        self._registered_classes = {}
        self.associations = Graph(directed=False)
        self.engine_functions = {}
        self.logflags = logflags.ERROR + logflags.IO
    
    def log(self, message):
        """Default logger (writes to stdout). Feel free to replace."""
        if isinstance(message, unicode):
            print message.encode('utf8')
        else:
            print message
    
    def load(self, configFileName):
        """Load StorageManagers from the given filename."""
        parser = ConfigParser.ConfigParser()
        # Make names case-sensitive by overriding optionxform.
        parser.optionxform = unicode
        parser.read(configFileName)
        
        stores = []
        for section in parser.sections():
            opts = dict(parser.items(section))
            stores.append((int(opts.get("Load Order", "0")), section, opts))
        stores.sort()
        
        for order, name, options in stores:
            self.add_store(name, options[u'Class'], options)
    
    def add_store(self, name, store, options=None):
        """Register a StorageManager.
        
        The 'store' argument may be a StorageManager class, an instance of
        that class, or the full importable dotted-package name of the class.
        """
        
        if isinstance(store, basestring):
            if store in storage.managers:
                store = storage.managers[store]
        
        if isinstance(store, basestring):
            store = xray.classes(store)(self, options or {})
        elif isinstance(store, (type, ClassType)):
            store = store(self, options or {})
        
        self.stores[name] = store
        return store
    
    def remove_store(self, name):
        """Remove (unregister) the named store.
        
        All classes associated to the given store will be disassociated,
        and will then be free to associate with another store (usually
        the default store).
        """
        if name in self.stores:
            store = self.stores[name]
            
            # Disassociate all registered classes with this store.
            for c in self._registered_classes.keys():
                if self._registered_classes[c] is store:
                    self._registered_classes[c] = None
            
            del self.stores[name]
    
    def map_all(self):
        """Map all registered classes to internal storage structures.
        
        Although classes are mapped automatically the first time they
        are accessed (see Arena.storage), in production it is often more
        useful to map all classes at application startup. Call this
        method to do so (but register all classes first).
        
        This method is idempotent, but that doesn't mean cheap. Try not
        to call it very often (once at app startup is usually enough).
        """
        storemap = {}
        
        # Don't use iteritems because self.storage may mutate the dict.
        for cls, store in self._registered_classes.items():
            if store is None:
                # Call _find_storage directly to skip the map()
                # call in Arena.storage.
                store = self._find_storage(cls)
                self._registered_classes[cls] = store
            bucket = storemap.setdefault(store, [])
            bucket.append(cls)
        
        storemap = [(s.loadOrder, s, c) for s, c in storemap.iteritems()]
        storemap.sort()
        for order, store, classes in storemap:
            store.map(classes)
    
    def shutdown(self):
        """Shutdown the arena and all its stores."""
        # Tell all stores to shut down.
        stores = [(v.shutdownOrder, v, k) for k, v in self.stores.iteritems()]
        stores.sort()
        for order, store, name in stores:
            store.shutdown()
    
    def new_sandbox(self):
        """Return a new sandbox object in this Arena."""
        return Sandbox(self)
    
    
    # --------------------- Unit Class Registration --------------------- #
    
    def register(self, cls):
        """Assert that Units of class 'cls' will be handled."""
        # We must allow modules to register classes before any stores have
        # been added, but not overwrite a store which has already been found.
        if cls not in self._registered_classes:
            self._registered_classes[cls] = None
            
            # Register any association(s) in an undirected graph.
            for ua in cls._associations.itervalues():
                if getattr(ua, "register", True):
                    self.associations.connect(cls, ua.farClass)
    
    def register_all(self, globals):
        """Register each subclass of Unit in the given globals."""
        import dejavu
        seen = {}
        for obj in globals.itervalues():
            if isinstance(obj, type) and issubclass(obj, dejavu.Unit):
                self.register(obj)
                seen[obj] = None
        return seen.keys()
    
    def class_by_name(self, classname):
        """Return the class object for the given classname."""
        for cls in self._registered_classes:
            if cls.__name__ == classname:
                return cls
        raise KeyError("No registered class found for '%s'." % classname)
    
    def storage(self, cls):
        """Return the StorageManager which handles Units of the given class.
        
        The results of this call will be cached for performance. Also, this
        will call store.map(cls) on first retrieval.
        """
        store = self._registered_classes.get(cls)
        if store:
            return store
        
        store = self._find_storage(cls)
        self._registered_classes[cls] = store
        store.map([cls])
        return store
    
    def _find_storage(self, cls):
        """Find the Storage Manager which handles Units of the given class.
        
        This method (unlike the 'storage' method) does no caching or mapping.
        """
        # Search all stores for the class name.
        default_store = None
        clsname = cls.__name__
        for store in self.stores.values():
            if not store.classnames:
                # This store has no "classnames" list, which signals that it
                # handles all classes which are not handled by other stores.
                default_store = store
            elif clsname in store.classnames:
                return store
        
        # Name not found in any store's classnames. Try a default store.
        if default_store:
            return default_store
        
        raise KeyError("No store found for '%s'." % clsname)
    
    def create_storage(self, cls):
        """Create storage space for cls."""
        # Skip the map() call inside storage().
        store = self._registered_classes.get(cls)
        if not store:
            store = self._find_storage(cls)
            self._registered_classes[cls] = store
        store.create_storage(cls)
    
    def has_storage(self, cls):
        """If storage space for cls exists, return True (False otherwise)."""
        try:
            return self.storage(cls).has_storage(cls)
        except errors.MappingError:
            return False
    
    def drop_storage(self, cls):
        """Remove storage space for cls."""
        self.storage(cls).drop_storage(cls)
    
    def add_property(self, cls, name):
        """Add storage space for the named property of the given cls."""
        self.storage(cls).add_property(cls, name)
    
    def drop_property(self, cls, name):
        """Drop storage space for the named property of the given cls."""
        self.storage(cls).drop_property(cls, name)
    
    def rename_property(self, cls, oldname, newname):
        """Rename storage space for the property of the given cls."""
        self.storage(cls).rename_property(cls, oldname, newname)
    
    def migrate_class(self, cls, new_store):
        """Copy all units of cls to new_store."""
        new_store.create_storage(cls)
        for unit in self.new_sandbox().xrecall(cls):
            new_store.reserve(unit)
            new_store.save(unit, True)
    
    def migrate(self, new_store, old_store=None, copy_only=False):
        """Copy all units (of old_store) to new_store."""
        for cls in self._registered_classes:
            store = self.storage(cls)
            if old_store is None or old_store is store:
                self.migrate_class(cls, new_store)
                if not copy_only:
                    self._registered_classes[cls] = new_store


###########################################################################
##                                                                       ##
##                              Sandboxes                                ##
##                                                                       ##
###########################################################################


class Sandbox(object):
    """Data sandbox for Dejavu arenas.
    
    Each consumer (that is, each UI process or thread) maintains a Sandbox
    for managing Units. Sandboxes populate themselves with Units on a lazy
    basis, allowing UI code to request data as it's needed. However, once
    obtained, such Units are persisted (usually for the lifetime of the
    thread); this important detail means that multiple requests for the
    same Units result in multiple references to the same objects, rather
    than multiple objects. Sandboxes are basically what Fowler calls
    Identity Maps.
    
    The *REALLY* important thing to understand if you're customizing this
    is that Sandboxes won't survive sharing across threads--DON'T TRY IT.
    If you need to share unit data across requests, use or make an SM which
    persists the data, and chain it with another, more normal SM.
    
    _cache(), _caches, and _stores are private for a reason--don't access
    them from interface code--tell the Sandbox to do it for you.
    
    Starting with Python 2.5, each Sandbox instance is its own context
    manager, so you can have boxes automatically flush themselves
    when you're done, and automatically rollback on error. Example:
    
    # __future__ only needed for Python 2.5, not 2.6+
    from __future__ import with_statement
    
    with arena.new_sandbox() as box:
        WAP = box.unit(Zoo, Name='Wild Animal Park')
        WAP.Opens = now
    """
    
    def __init__(self, arena):
        self.arena = arena
        self._caches = {}
    
    def __getattr__(self, key):
        # Support "magic recaller" methods on self.
        for cls in self.arena._registered_classes.iterkeys():
            name = cls.__name__
            if name == key:
                def recaller(*args, **kwargs):
                    # Allow identifiers to be supplied as args or kwargs
                    # (since the common case will be a single identifier).
                    for arg, key in zip(args, cls.identifiers):
                        kwargs[str(key)] = arg
                    expr = logic.filter(**kwargs)
                    try:
                        return self.xrecall(cls, expr).next()
                    except StopIteration:
                        return None
                recaller.__doc__ = "A single %s Unit, else None." % name
                return recaller
        raise AttributeError("Sandbox object has no attribute '%s'" % key)
    
    def memorize(self, unit):
        """Persist the given unit in storage."""
        cls = unit.__class__
        unit.sandbox = self
        
        # Ask the store to accept the unit, assigning it primary key values
        # if necessary. The store should also call unit.cleanse() if it
        # saves the whole unit state on this call.
        self.arena.storage(cls).reserve(unit)
        
        # Insert the unit into the cache.
        id = unit.identity()
        self._cache(cls)[id] = unit
        if self.arena.logflags & logflags.MEMORIZE:
            self.arena.log("MEMORIZE %s: %s" % (cls.__name__, id))
        
        # Do this at the end of the func, since most on_memorize
        # will want to have an identity when called.
        if hasattr(unit, "on_memorize"):
            unit.on_memorize()
    
    def forget(self, unit):
        """Destroy the given unit, both in the cache and storage."""
        cls = unit.__class__
        
        id = unit.identity()
        if self.arena.logflags & logflags.FORGET:
            self.arena.log("FORGET %s: %s" % (cls.__name__, id))
        self.arena.storage(cls).destroy(unit)
        
        del self._cache(cls)[id]
        
        # This must be done after the destroy() call, so that a
        # related unit can poll all instances of this class.
        if hasattr(unit, "on_forget"):
            unit.on_forget()
        
        unit.sandbox = None
    
    def xrecall(self, classes, expr=None, inherit=False, **kwargs):
        """Iterator over units of the given class(es) which match expr.
        
        If inherit is True, units of the given class and all registered
        subclasses of the given class will be recalled.
        
        If the 'classes' arg is a UnitJoin, each yielded value will be a
        list of Units, in the same order as the classes arg.
        This facilitates unpacking in iterative consumer code like:
        
        for invoice, price in sandbox.xrecall(Invoice & Price, f):
            deal_with(invoice)
            deal_with(price)
        
        Recalling multiple classes is currently not well-isolated.
        If an expr argument is supplied, then the store may not return rows
        which our cache would, and those won't be included in the resultset.
        If you're using xrecall with joins, you should be safe if:
        
            * You pass no expr, or
            * You're using this sandbox as read-only, or
            * You call flush_all() after mutating Units but before recalling
                multiple classes.
        
        This also does not yet support multiple classes in separate stores.
        """
        if classes.__class__.__name__ == "UnitJoin":
            for unitrow in self._xmulti(classes, expr, **kwargs):
                yield unitrow
            return
        
        cls = classes
        
        if expr and not isinstance(expr, logic.Expression):
            expr = logic.Expression(expr)
        if kwargs:
            f = logic.filter(**kwargs)
            if expr:
                expr += f
            else:
                expr = f
        
        if self.arena.logflags & logflags.RECALL:
            self.arena.log("RECALL %s: %s" % (cls.__name__, expr))
        
        if inherit:
            # Collect all registered subclasses of cls.
            # Note that cls is a subclass of itself.
            classes = [c for c in self.arena._registered_classes.iterkeys()
                       if issubclass(c, cls)]
        else:
            classes = [cls]
        if not classes:
            # Even the requested class is not registered.
            raise errors.UnrecallableError("The '%s' class is not registered."
                                           % cls.__name__)
        
        for cls in classes:
            cache = self._cache(cls)
            
            # Special-case the scenario where one Unit is expected
            # and called by ID. We should be able to save a database hit.
            if expr:
                fc = expr.func.func_code
                if (fc.co_code == '|\x00\x00i\x01\x00d\x01\x00j\x02\x00S'
                    and fc.co_names[-1] == 'ID'):
                    ID = fc.co_consts[-1]
                    unit = cache.get((ID,))
                    if unit is not None:
                        # Do NOT call on_recall here. That should be called
                        # only at the Sandbox-SM boundary.
                        yield unit
                        return
            
            # Query the cache. We have to use a static copy of the
            # keys, to ensure that our cache doesn't change size
            # during iteration (due to overlapping xrecalls).
            keys = cache.keys()
            for id in keys:
                unit = cache.get(id)
                if unit and ((expr is None) or expr.evaluate(unit)):
                    # Do NOT call on_recall here. That should be called
                    # only at the Sandbox-SM boundary.
                    yield unit
            
            # Query Storage.
            for unit in self.arena.storage(cls).recall(cls, expr):
                id = unit.identity()
                # Don't offer up a unit that was already checked in our cache
                # (whether it matched the expr() or not--we assume the cache 
                # has the freshest data).
                if id not in keys:
                    # Very important that we check for existing unit, as its
                    # state may have changed in memory but not in storage
                    # (even between our cache yields and this yield).
                    # Make sure the cache lookup and get happens atomically.
                    existing = cache.get(id)
                    if existing:
                        yield existing
                    else:
                        unit.sandbox = self
                        confirmed = True
                        cache[id] = unit
                        if hasattr(unit, 'on_recall'):
                            try:
                                unit.on_recall()
                            except errors.UnrecallableError:
                                confirmed = False
                        if confirmed:
                            yield unit
    
    def recall(self, classes, expr=None, inherit=False, **kwargs):
        """List of units of the given class(es) which match expr.
        
        If inherit is True, units of the given class and all registered
        subclasses of the given class will be recalled.
        
        If the 'classes' arg is a UnitJoin, each yielded value will be a
        list of Units, in the same order as the classes arg.
        This facilitates unpacking in iterative consumer code like:
        
        for invoice, price in sandbox.recall(Invoice & Price, f):
            deal_with(invoice)
            deal_with(price)
        
        Recalling multiple classes is currently not well-isolated.
        If an expr argument is supplied, then the store may not return rows
        which our cache would, and those won't be included in the resultset.
        If you're using recall with joins, you should be safe if:
        
            * You pass no expr, or
            * You're using this sandbox as read-only, or
            * You call flush_all() after mutating Units but before recalling
                multiple classes.
        
        This also does not yet support multiple classes in separate stores.
        """
        return [x for x in self.xrecall(classes, expr, inherit, **kwargs)]
    
    def _xmulti(self, classes, expr=None, **kwargs):
        """Recall units of each cls if they together match the expr.
        
        The 'classes' arg must be a UnitJoin, and each yielded value
        will be a list of Units, in the same order as the classes arg.
        This facilitates unpacking in iterative consumer code like:
        
        for invoice, price in sandbox.recall(Invoice & Price, f):
            deal_with(invoice)
            deal_with(price)
        
        Recalling multiple classes is currently not well-isolated.
        If an expr argument is supplied, then the store may not return rows
        which our cache would, and those won't be included in the resultset.
        If you're using recall with joins, you should be safe if:
        
            * You pass no expr, or
            * You're using this sandbox as read-only, or
            * You call flush_all() after mutating Units but before recalling
                multiple classes.
        
        This also does not yet support multiple classes in separate stores.
        """
        
        if expr and not isinstance(expr, logic.Expression):
            expr = logic.Expression(expr)
        if kwargs:
            f = logic.filter(**kwargs)
            if expr:
                expr += f
            else:
                expr = f
        
        if self.arena.logflags & logflags.RECALL:
            self.arena.log("RECALL %s %s" %
                           (", ".join([c.__name__ for c in classes]), expr))
        
        stores = [self.arena.storage(cls) for cls in classes]
        firststore = stores[0]
        for s in stores:
            if s is not firststore:
                raise ValueError(u"(x)recall does not support multiple"
                                 u" classes in disparate stores.")
        
        # This is broken. If a filter expr is supplied, then the store may
        # not return rows which our cache would, and those won't be included
        # in the resultset. If you're using xmulti with no expr's, or
        # in read-only scripts, it should be OK for now. But if you mutate
        # Units and then call multirecall, expect inconsistent results.
        for unitset in firststore.multirecall(classes, expr):
            confirmed = True
            for index in xrange(len(unitset)):
                unit = unitset[index]
                id = unit.identity()
                cache = self._cache(unit.__class__)
                if id in cache:
                    # Keep the unit which is in our cache!
                    unitset[index] = cache[id]
                else:
                    cache[id] = unit
                    unit.sandbox = self
                    if hasattr(unit, 'on_recall'):
                        try:
                            unit.on_recall()
                        except errors.UnrecallableError:
                            confirmed = False
                            break
            if confirmed:
                yield unitset
    
    def unit(self, cls, expr=None, inherit=False, **kwargs):
        """A single Unit which matches the given expr, else None.
        
        If inherit is True, the given class and all registered subclasses
        of the given class will be searched for a matching Unit.
        
        **kwargs will be combined into an Expression via logic.filter.
        The first Unit matching that expression is returned; if no
        Units match, None is returned.
        """
        try:
            return self.xrecall(cls, expr, inherit, **kwargs).next()
        except StopIteration:
            return None
    
    def view(self, cls, attrs, expr=None, **kwargs):
        """Yield tuples of attrs for the given cls which match the expr.
        
        cls: The Unit subclass for which to yield property tuples.
        attrs: a sequence of strings; each should be the name of
            a UnitProperty on the given cls.
        expr: a lambda or logic.Expression. If provided, data will only
            be yielded for units of the given cls which match the expr.
        **kwargs: additional expr filters in name=value format.
        
        Each yielded value will be a list of values, in the same order as
        the attrs arg. This facilitates unpacking in iterative consumer
        code like:
        
        for id, name in sandbox.view(Invoice, ['ID', 'Name'], f):
            print id, ": ", name
        
        This is generally much faster than recall, and should be preferred
        for performance-sensitive code.
        """
        if expr and not isinstance(expr, logic.Expression):
            expr = logic.Expression(expr)
        if kwargs:
            f = logic.filter(**kwargs)
            if expr:
                expr += f
            else:
                expr = f
        
        if self.arena.logflags & logflags.VIEW:
            self.arena.log("VIEW %s [%s]: %s" % (cls.__name__, attrs, expr))
        
        cache = self._cache(cls)
        
        for unit in cache.itervalues():
            if expr is None or expr(unit):
                yield tuple([getattr(unit, attr) for attr in attrs])
        
        # Add the identity attribute(s) if not present. This is necessary
        # to avoid duplicating objects which are already in our cache.
        fields = list(attrs)
        indices = []
        added_fields = 0
        for key in cls.identifiers:
            if key not in fields:
                added_fields += 1
                fields.append(key)
            indices.append(fields.index(key))
        
        for row in self.arena.storage(cls).view(cls, fields, expr):
            id = tuple([row[x] for x in indices])
            if id not in cache:
                if added_fields:
                    # Remove the added identifier columns from the row.
                    row = row[:-added_fields]
                yield row
    
    def sum(self, cls, attr, expr=None, **kwargs):
        """Sum of all non-None values for the given cls.attr."""
        expr = logic.Expression(lambda x: getattr(x, attr) != None) + expr
        return sum([row[0] for row in self.view(cls, (attr,), expr, **kwargs)])
    
    def distinct(self, cls, attrs, expr=None, **kwargs):
        """List of distinct UnitProperty tuples for the given cls.
        
        If only one attribute is specified, a list of values will be returned.
        If more than one attribute is specified, a zipped list will be returned.
        
        Notice that you can also use this function as a count() function
        (in fact it's the only way to do it) by using attrs = ['ID'].
        """
        if expr and not isinstance(expr, logic.Expression):
            expr = logic.Expression(expr)
        if kwargs:
            f = logic.filter(**kwargs)
            if expr:
                expr += f
            else:
                expr = f
        
        if self.arena.logflags & logflags.VIEW:
            self.arena.log("DISTINCT %s [%s]: %s" % (cls.__name__, attrs, expr))
        
        seen = {}
        cache = self._cache(cls)
        for unit in cache.itervalues():
            if expr is None or expr(unit):
                row = tuple([getattr(unit, attr) for attr in attrs])
                if row not in seen:
                    seen[row] = None
        
        for row in self.arena.storage(cls).distinct(cls, attrs, expr):
            if row not in seen:
                seen[row] = None
        
        seen = seen.keys()
        seen.sort()
        if len(attrs) == 1:
            seen = [x[0] for x in seen]
        return seen
    
    def count(self, cls, expr):
        """Number of Units of the given cls which match the given expr."""
        return len(self.distinct(cls, cls.identifiers, expr))
    
    def range(self, cls, attr, expr=None, **kwargs):
        """Distinct, non-None attr values (ordered and continuous, if possible).
        
        If the given attribute is a known discrete, ordered type
        (like int, long, datetime.date), this returns the closed interval:
            
            [min(attr), ..., max(attr)]
        
        That is, all possible values will be output between min and max,
        even if they do not appear in the dataset.
        
        If the given attribute is not reasonably discrete (e.g., str,
        unicode, or float) then all distinct, non-None values are returned
        (sorted, if possible).
        """
        existing = [x for x in self.distinct(cls, [attr], expr, **kwargs)
                    if x is not None]
        if not existing:
            return []
        
        attr_type = getattr(cls, attr).type
        if issubclass(attr_type, (int, long)):
            return range(min(existing), max(existing) + 1)
        else:
            try:
                import datetime
            except ImportError:
                pass
            else:
                if issubclass(attr_type, datetime.date):
                    def date_gen():
                        start, end = min(existing), max(existing)
                        for d in range((end + 1) - start):
                            yield start + datetime.timedelta(d)
                    return date_gen()
        
        try:
            existing.sort()
        except TypeError:
            pass
        
        return existing
    
    #                           Cache Management                           #
    
    def _cache(self, cls):
        """Return the cache for the specified class.
        
        This base class creates a new cache for each cls per request.
        """
        if cls not in self._caches:
            self._caches[cls] = {}
        return self._caches[cls]
    
    def purge(self, cls):
        """Drop all cached Units of class 'cls'. Do not save."""
        del self._caches[cls]
    
    def repress(self, unit):
        """Remove unit from cache (but don't destroy)."""
        cls = unit.__class__
        id = unit.identity()
        if self.arena.logflags & logflags.REPRESS:
            self.arena.log("REPRESS %s: %s" % (cls.__name__, id))
        
        if hasattr(unit, "on_repress"):
            unit.on_repress()
        
        # Save after on_repress in case on_repress modified the unit.
        self.arena.storage(cls).save(unit)
        
        del self._cache(cls)[id]
        unit.sandbox = None
    
    def flush_all(self):
        """Repress all units and commit any open transaction."""
        
        for cls in self._caches.keys():
            # Call all on_repress methods first! There are truly horrible
            # interdependency chains in most on_repress methods, and
            # it's best to resolve them all at once BEFORE flushing
            # any units from the cache.
            # Note we use values instead of itervalues, since the
            # cache may change size during iteration.
            for unit in self._cache(cls).values():
                if hasattr(unit, "on_repress"):
                    unit.on_repress()
        
        seen_stores = {}
        for cls in self._caches.keys():
            cache = self._cache(cls)
            store = self.arena.storage(cls)
            seen_stores[store] = None
            while cache:
                unitid, unit = cache.popitem()
                if self.arena.logflags & logflags.REPRESS:
                    self.arena.log("REPRESS %s: %s" % (cls.__name__, unitid))
                store.save(unit)
        
        self.commit()
    
    #                        Transaction Management                        #
    
    def start(self, isolation=None):
        """Start a transaction."""
        for store in set(self.arena._registered_classes.values()):
            # If store is None, the class was never mapped to a store.
            if store:
                # By default, stores do not support transactions,
                # in which case 'start' will be None.
                if store.start:
                    store.start(isolation)
    
    def commit(self):
        """Commit the current transaction.
        
        If errors occur during this process, they are not trapped here.
        You must either call rollback yourself (or fix the problem and
        try to commit again).
        """
        for store in set(self.arena._registered_classes.values()):
            if store and store.commit:
                store.commit()
    
    def rollback(self):
        """Roll back the current transaction (all changes) and purge our cache."""
        for cls in self._caches.keys():
            # Dump all objects in this cache
            self.purge(cls)
        
        for store in set(self.arena._registered_classes.values()):
            if store and store.rollback:
                store.rollback()
    
    #                          Context Management                          #
    
    def __enter__(self):
        return self
    
    def __exit__ (self, type, value, tb):
        if tb is None:
            self.flush_all()
        else:
            self.rollback()

