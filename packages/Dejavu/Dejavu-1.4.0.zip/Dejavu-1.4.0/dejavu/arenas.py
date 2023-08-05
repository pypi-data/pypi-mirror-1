
import ConfigParser

from containers import Graph
import logic
import errors
import xray

__all__ = ['Arena', 'Sandbox',
           'LOGCONN', 'LOGFORGET', 'LOGMEMORIZE', 'LOGRECALL',
           'LOGREPRESS', 'LOGSANDBOX', 'LOGSQL', 'LOGVIEW',
           ]


# logging flags (see Arena.logflags)
LOGSQL = 4
LOGCONN = 8

LOGMEMORIZE = 128
LOGRECALL = 256
LOGVIEW = 512
LOGREPRESS = 1024
LOGFORGET = 2048
LOGSANDBOX = LOGMEMORIZE | LOGRECALL | LOGVIEW | LOGREPRESS | LOGFORGET


class Arena(object):
    """Arena(). A namespace/workspace for a Dejavu application."""
    
    def __init__(self):
        self.defaultStore = None
        self.stores = {}
        self._registered_classes = {}
        self.associations = Graph(directed=False)
        self.engine_functions = {}
        self.logflags = 0
    
    def log(self, message, flag):
        """Default logger (writes to stdout). Feel free to replace."""
        if flag & self.logflags:
            print message
    
    def load(self, configFileName):
        """Load StorageManagers."""
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
        """add_store(name, store, options=None). Register a StorageManager.
        
        The 'store' argument may be the name of a Storage Manager class;
        if so, it must be importable (that is, it must have the full dotted
        package name).
        """
        
        if isinstance(store, basestring):
            store = xray.classes(store)(name, self, options or {})
        
        self.stores[name] = store
        if not store.classnames:
            # This store has no "classnames" list, which signals that it
            # handles all classes which are not handled by other stores.
            self.defaultStore = store
        return store
    
    def remove_store(self, name):
        if name in self.stores:
            store = self.stores[name]
            
            # Disassociate all registered classes with this store.
            for c in self._registered_classes.keys():
                if self._registered_classes[c] is store:
                    self._registered_classes[c] = None
            
            del self.stores[name]
    
    def shutdown(self):
        """Shutdown the arena."""
        # Tell all stores to shut down.
        stores = [(v.shutdownOrder, v, k) for k, v in self.stores.iteritems()]
        stores.sort()
        for order, store, name in stores:
            store.shutdown()
    
    def new_sandbox(self):
        return Sandbox(self)
    
    ###########################################
    ##        Unit Class Registration        ##
    ###########################################
    
    def register(self, cls):
        """register(cls) -> Assert that Units of class 'cls' will be handled."""
        # We must allow modules to register classes before any stores have
        # been added, but not overwrite a store which has already been found.
        if cls not in self._registered_classes:
            self._registered_classes[cls] = None
        
        # Register any association(s) in an undirected graph.
        for ua in cls._associations.itervalues():
            if getattr(ua, "register", True):
                self.associations.connect(cls, ua.farClass)
    
    def register_all(self, globals):
        import dejavu
        for obj in globals.itervalues():
            if isinstance(obj, type) and issubclass(obj, dejavu.Unit):
                self.register(obj)
    
    def class_by_name(self, classname):
        for cls in self._registered_classes:
            if cls.__name__ == classname:
                return cls
        raise KeyError("No registered class found for '%s'." % classname)
    
    def storage(self, cls):
        """Return the StorageManager which handles Units of the given class."""
        found = self._registered_classes.get(cls)
        
        if found:
            return found
        
        # Search all stores for the class name.
        clsname = cls.__name__
        for store in self.stores.itervalues():
            if clsname in store.classnames:
                found = store
                break
        found = found or self.defaultStore
        if found is None:
            raise KeyError("No store found for '%s' and no "
                           "default store." % clsname)
        
        self._registered_classes[cls] = found
        return found
    
    def create_storage(self, cls):
        """create_storage(cls). Create storage space for cls."""
        self.storage(cls).create_storage(cls)
    
    def has_storage(self, cls):
        return self.storage(cls).has_storage(cls)
    
    def drop_storage(self, cls):
        self.storage(cls).drop_storage(cls)
    
    def add_property(self, cls, name):
        self.storage(cls).add_property(cls, name)
    
    def drop_property(self, cls, name):
        self.storage(cls).drop_property(cls, name)
    
    def rename_property(self, cls, oldname, newname):
        self.storage(cls).rename_property(cls, oldname, newname)
    
    def migrate_class(self, cls, new_store):
        """migrate_class(cls, new_store). Copy all units of cls to new_store."""
        new_store.create_storage(cls)
        for unit in self.new_sandbox().xrecall(cls):
            new_store.reserve(unit)
            new_store.save(unit, True)
    
    def migrate(self, new_store, old_store=None, copy_only=False):
        """migrate(new_store, old_store=None). Copy all units (of old_store) to new_store."""
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
    """Sandbox(arena). Data sandbox for Dejavu arenas.
    
    Each consumer (that is, each UI process) maintains a Sandbox for
    managing Units. Sandboxes populate themselves with Units on a lazy
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
    """
    
    def __init__(self, arena):
        self.arena = arena
        self._caches = {}
        self._magify()
    
    def _magify(self):
        """Add magic recaller methods to self."""
        # I haven't decided yet if this technique is too slow; it might be
        # better to memoize a base class in the arena, and just set the
        # magic methods on it once, rather than anew for each instance.
        for cls in self.arena._registered_classes.iterkeys():
            name = cls.__name__
            if not hasattr(self, name):
                def make_recaller(cls):
                    def recaller(*args, **kwargs):
                        # Allow identifiers to be supplied as args or kwargs
                        # (since the common case will be a single identifier).
                        for arg, id in zip(args, cls.identifiers):
                            kwargs[str(id.key)] = arg
                        expr = logic.filter(**kwargs)
                        try:
                            return self.xrecall(cls, expr).next()
                        except StopIteration:
                            return None
                    recaller.__doc__ = "A single %s Unit, else None." % name
                    return recaller
                setattr(self, name, make_recaller(cls))
    
    def memorize(self, unit):
        """memorize(unit). Persist unit in storage."""
        cls = unit.__class__
        unit.sandbox = self
        
        # Ask the store to accept the unit, assigning it primary key values
        # if necessary. The store should also call unit.cleanse() if it
        # saves the whole unit state on this call.
        self.arena.storage(cls).reserve(unit)
        
        # Insert the unit into the cache.
        id = unit.identity()
        self._cache(cls)[id] = unit
        self.arena.log("MEMORIZE %s: %s" % (cls.__name__, id), LOGMEMORIZE)
        
        # Do this at the end of the func, since most on_memorize
        # will want to have an identity when called.
        if hasattr(unit, "on_memorize"):
            unit.on_memorize()
    
    def forget(self, unit):
        """Destroy unit, both in the cache and storage."""
        cls = unit.__class__
        
        id = unit.identity()
        self.arena.log("FORGET %s: %s" % (cls.__name__, id), LOGFORGET)
        self.arena.storage(cls).destroy(unit)
        
        del self._cache(cls)[id]
        
        # This must be done after the destroy() call, so that a
        # related unit can poll all instances of this class.
        if hasattr(unit, "on_forget"):
            unit.on_forget()
        
        unit.sandbox = None
    
    def xrecall(self, classes, expr=None):
        """Iterator over units of cls which match expr."""
        if classes.__class__.__name__ == "UnitJoin":
            for unitrow in self.xmulti(classes, expr):
                yield unitrow
            return
        
        cls = classes
        self.arena.log("RECALL %s: %s" % (cls.__name__, expr), LOGRECALL)
        
        # Collect all registered subclasses of cls.
        # Note that cls is a subclass of itself.
        classes = [c for c in self.arena._registered_classes.iterkeys()
                   if issubclass(c, cls)]
        if not classes:
            # Even the requested class is not registered.
            raise errors.UnrecallableError("The '%s' class is not registered."
                                           % cls.__name__)
        
        for cls in classes:
            finished = False
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
                        finished = True
            
            if not finished:
                # Query the cache. We have to use a static copy of the
                # keys, to ensure that our cache doesn't change size
                # during iteration (due to overlapping xrecalls).
                keys = cache.keys()
                for id in keys:
                    unit = cache.get(id)
                    if unit and (expr is None) or expr.evaluate(unit):
                        # Do NOT call on_recall here. That should be called
                        # only at the Sandbox-SM boundary.
                        yield unit
                
                # Query Storage.
                for unit in self.arena.storage(cls).recall(cls, expr):
                    id = unit.identity()
                    # Don't offer up a unit that was already checked in our cache
                    # (whether it matched the expr() or not--we assume the cache 
                    # has the freshest data).
                    # A list is 2% to 4% faster than a dict, by the way (in Py 2.3).
                    if id not in keys:
                        # Very important that we check for existing unit, as its
                        # state may have changed in memory but not in storage.
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
    
    def recall(self, classes, expr=None):
        """List of units of class 'cls' which match expr."""
        return [x for x in self.xrecall(classes, expr)]
    
    def xmulti(self, classes, expr=None):
        """xmulti(classes, expr) -> [[unit, ...], [unit, ...], ...]
        Recall units of each cls if they together match the expr.
        
        Each yielded value will be a list of Units, in the same order as
        the classes arg. This facilitates unpacking in iterative consumer
        code like:
        
        for invoice, price in sandbox.xmulti(Invoice & Price, f):
            deal_with(invoice)
            deal_with(price)
        """
        
        self.arena.log("RECALL %s %s" %
                       (", ".join([c.__name__ for c in classes]), expr),
                       LOGRECALL)
        
        stores = [self.arena.storage(cls) for cls in classes]
        firststore = stores[0]
        for s in stores:
            if s is not firststore:
                raise ValueError(u"xmulti() does not support multiple"
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
    
    def unit(self, cls, **kwargs):
        """unit(cls, **kwargs) -> A single matching Unit, else None.
        
        **kwargs will be combined into an Expression via logic.filter.
            The first Unit matching that expression is returned; if no
            Units match, None is returned.
        
        If you need a single Unit which matches a more complex
            expression, use recall()[0] or xrecall().next().
        """
        expr = None
        if kwargs:
            expr = logic.filter(**kwargs)
        try:
            return self.xrecall(cls, expr).next()
        except StopIteration:
            return None
    
    def view(self, cls, attrs, expr=None):
        """view(cls, attrs, expr=None) -> Iterator of all Property tuples."""
        self.arena.log("VIEW %s [%s]: %s" % (cls.__name__, attrs, expr), LOGVIEW)
        
        cache = self._cache(cls)
        
        for unit in cache.itervalues():
            if expr is None or expr(unit):
                yield tuple([getattr(unit, attr) for attr in attrs])
        
        # Add the identity attribute(s) if not present. This is necessary
        # to avoid duplicating objects which are already in our cache.
        fields = list(attrs)
        indices = []
        added_fields = 0
        for prop in cls.identifiers:
            if prop.key not in fields:
                added_fields += 1
                fields.append(prop.key)
            indices.append(fields.index(prop.key))
        
        for row in self.arena.storage(cls).view(cls, fields, expr):
            id = tuple([row[x] for x in indices])
            if id not in cache:
                if added_fields:
                    # Remove the added identifier columns from the row.
                    row = row[:len(row) - added_fields]
                yield row
    
    def distinct(self, cls, attrs, expr=None):
        """distinct(cls, attrs, expr=None) -> List of distinct Property tuples.
        
        If only one attribute is specified, a list of values will be returned.
        If more than one attribute is specified, a zipped list will be returned.
        
        Notice that you can also use this function as a count() function
        (in fact it's the only way to do it) by using attrs = ['ID'].
        """
        self.arena.log("DISTINCT %s [%s]: %s" % (cls.__name__, attrs, expr), LOGVIEW)
        
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
        """count(cls, expr) -> Number of Units of class 'cls'."""
        idnames = [prop.key for prop in cls.identifiers]
        return len(self.distinct(cls, idnames, expr))
    
    ####################################
    ##        Cache Management        ##
    ####################################
    
    def _cache(self, cls):
        """cache(cls). Return the cache for the specified class.
        
        This base class creates a new cache for each cls per request.
        """
        if cls not in self._caches:
            self._caches[cls] = {}
        return self._caches[cls]
    
    def purge(self, cls):
        """purge(cls). Drop all cached Units of class 'cls'. Do not save."""
        del self._caches[cls]
    
    def repress(self, unit):
        """repress(unit). Remove unit from cache (but don't destroy)."""
        cls = unit.__class__
        id = unit.identity()
        self.arena.log("REPRESS %s: %s" % (cls.__name__, id), LOGREPRESS)
        
        if hasattr(unit, "on_repress"):
            unit.on_repress()
        
        # Save after on_repress in case on_repress modified the unit.
        self.arena.storage(cls).save(unit)
        
        del self._cache(cls)[id]
    
    def flush_all(self):
        """flush_all(). Repress all units."""
        
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
        
        for cls in self._caches.keys():
            cache = self._cache(cls)
            store = self.arena.storage(cls)
            while cache:
                unitid, unit = cache.popitem()
                self.arena.log("REPRESS %s: %s" % (cls.__name__, unitid), LOGREPRESS)
                store.save(unit)

