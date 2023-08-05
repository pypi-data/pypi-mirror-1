"""Storage Managers for Dejavu."""

import re
import datetime
import threading
import thread
try:
    import cPickle as pickle
except ImportError:
    import pickle

from dejavu import logic, recur


class StorageManager(object):
    """A Manager base class for storing and retrieving Units.
    
    The base StorageManager class doesn't actually store anything;
    it needs to be subclassed.
    """
    
    def __init__(self, name, arena, allOptions={}):
        self.name = name
        self.arena = arena
        self.classnames = [x.strip() for x
                           in allOptions.get('Units', '').split(",")
                           if x.strip()]
        self.shutdownOrder = int(allOptions.get('Shutdown Order', '0'))
    
    def recall(self, unitClass, expr=None):
        """Return an iterable object which will populate Units."""
        raise NotImplementedError
    
    def save(self, unit, forceSave=False):
        """Store the object's data{} dictionary."""
        raise NotImplementedError
    
    def destroy(self, unit):
        """Delete the object."""
        raise NotImplementedError
    
    def reserve(self, unit):
        """Reserve storage space for the Unit."""
        raise NotImplementedError
    
    def shutdown(self):
        pass
    
    def view(self, cls, attrs, expr=None):
        """view(cls, attrs, expr=None) -> Iterator of all Property tuples."""
        raise NotImplementedError
    
    def distinct(self, cls, attrs, expr=None):
        """Distinct values for given attributes."""
        raise NotImplementedError
    
    def multirecall(self, classes, expr):
        """Full inner join units from each class."""
        raise NotImplementedError
    
    #                               Schemas                               #
    
    def create_database(self):
        raise NotImplementedError("%s has no create_database method."
                                  % self.__class__)
    
    def drop_database(self):
        raise NotImplementedError("%s has no drop_database method."
                                  % self.__class__)
    
    def create_storage(self, cls):
        raise NotImplementedError("%s has no create_storage method."
                                  % self.__class__)
    
    def has_storage(self, cls):
        raise NotImplementedError("%s has no has_storage method."
                                  % self.__class__)
    
    def drop_storage(self, cls):
        raise NotImplementedError("%s has no drop_storage method."
                                  % self.__class__)
    
    def add_property(self, cls, name):
        raise NotImplementedError("%s has no add_property method."
                                  % self.__class__)
    
    def drop_property(self, cls, name):
        raise NotImplementedError("%s has no drop_property method."
                                  % self.__class__)
    
    def rename_property(self, cls, oldname, newname):
        raise NotImplementedError("%s has no rename_property method."
                                  % self.__class__)


class ProxyStorage(StorageManager):
    """A Storage Manager which passes calls to another Storage Manager."""
    
    nextstore = None
    
    def __init__(self, name, arena, allOptions={}):
        StorageManager.__init__(self, name, arena, allOptions)
        
        nextstore = allOptions.get('Next Store')
        if nextstore:
            self.nextstore = arena.stores[nextstore]
    
    def recall(self, unitClass, expr=None):
        if self.nextstore:
            for unit in self.nextstore.recall(unitClass, expr):
                yield unit
    
    def save(self, unit, forceSave=False):
        """Store the unit."""
        if self.nextstore:
            self.nextstore.save(unit, forceSave)
    
    def destroy(self, unit):
        """Delete the unit."""
        if self.nextstore:
            self.nextstore.destroy(unit)
    
    def reserve(self, unit):
        """Reserve storage space for the Unit."""
        if self.nextstore:
            self.nextstore.reserve(unit)
    
    def view(self, cls, attrs, expr=None):
        """view(cls, attrs, expr=None) -> Iterator of all Property tuples."""
        if self.nextstore:
            return self.nextstore.view(cls, attrs, expr)
    
    def distinct(self, cls, attrs, expr=None):
        """distinct(cls, attrs, expr=None) -> Distinct values for given attributes."""
        if self.nextstore:
            return self.nextstore.distinct(cls, attrs, expr)
    
    def multirecall(self, classes, expr):
        """multirecall(classes, expr) -> Full inner join units from each class."""
        if self.nextstore:
            return self.nextstore.multirecall(classes, expr)
    
    #                               Schemas                               #
    
    def create_database(self):
        if self.nextstore:
            self.nextstore.create_database()
    
    def drop_database(self):
        if self.nextstore:
            self.nextstore.drop_database()
    
    def create_storage(self, cls):
        if self.nextstore:
            self.nextstore.create_storage(cls)
    
    def has_storage(self, cls):
        if self.nextstore:
            return self.nextstore.has_storage(cls)
        return False
    
    def drop_storage(self, cls):
        if self.nextstore:
            self.nextstore.drop_storage(cls)
    
    def add_property(self, cls, name):
        if self.nextstore:
            self.nextstore.add_property(cls, name)
    
    def drop_property(self, cls, name):
        if self.nextstore:
            self.nextstore.drop_property(cls, name)
    
    def rename_property(self, cls, oldname, newname):
        if self.nextstore:
            self.nextstore.rename_property(cls, oldname, newname)


class CachingProxy(ProxyStorage):
    """A Proxy Storage Manager which recalls and keeps Units in memory."""
    
    def __init__(self, name, arena, allOptions={}):
        ProxyStorage.__init__(self, name, arena, allOptions)
        
        self._caches = {}       # id: pickled Unit
        self._cache_locks = {}
        self._recallTimes = {}
        
        self.timer = None
        
        # Create and motivate a worker to sweep out idle Units.
        lifetime = allOptions.get('Lifetime', '')
        if lifetime:
            
            class IdleSweeper(recur.Worker):
                """A worker to sweep out idle Units."""
                def work(me):
                    """Start a cycle of scheduled work."""
                    # Note that 'self' refers to the Proxy, not the Worker.
                    self.sweep_all()
            self.sweeper = IdleSweeper(lifetime)
    
    def cachelen(self, cls):
        return len(self._caches.get(cls, {}))
    
    def cached_units(self, cls):
        return [pickle.loads(data) for data
                in self._caches.get(cls, {}).itervalues()]
    
    def _get_lock(self, unitClass):
        if unitClass not in self._caches:
            self._caches[unitClass] = {}
            self._cache_locks[unitClass] = thread.allocate_lock()
        lock = self._cache_locks[unitClass]
        lock.acquire(True)
        return lock
    
    def recall(self, unitClass, expr=None):
        """Return a Unit iterator."""
        currentTime = datetime.datetime.now()
        lock = self._get_lock(unitClass)
        try:
            cache = self._caches[unitClass]
            matches = {}
            
            # Run through our cache first. Hopefully, this will save us
            # calling expr(unit) twice for each unit.
            for id, pickledUnit in cache.iteritems():
                unit = pickle.loads(pickledUnit)
                if expr is None or expr(unit):
                    matches[id] = unit
            
            if self.nextstore:
                for unit in self.nextstore.recall(unitClass, expr):
                    id = unit.identity()
                    if id not in cache:
                        # Pickle the Unit to discard extraneous attributes,
                        # and avoid identity issues.
                        cache[id] = pickle.dumps(unit)
                        self._recallTimes[id] = currentTime
                        
                        # Only add to matches if it wasn't already in our
                        # cache (because stored units may have stale data).
                        if id not in matches:
                            matches[id] = unit
            
            return iter(matches.values())
        finally:
            lock.release()
    
    def save(self, unit, forceSave=False):
        """Store the unit."""
        # Don't call nextstore.save(). Defer that to sweep().
        
        # Don't check .dirty()!! If a unit changes from state A to
        # to state B, then back again to *exactly* state A, dirty()
        # will be False, and the cached data will stay in state B.
##        if unit.dirty():
        
        lock = self._get_lock(unit.__class__)
        try:
            cache = self._caches[unit.__class__]
            cache[unit.identity()] = pickle.dumps(unit)
        finally:
            lock.release()
    
    def destroy(self, unit):
        """Delete the unit."""
        unitClass = unit.__class__
        lock = self._get_lock(unitClass)
        try:
            id = unit.identity()
            cache = self._caches[unitClass]
            if self.nextstore:
                self.nextstore.destroy(unit)
            try:
                del cache[id]
            except KeyError:
                pass
            try:
                del self._recallTimes[id]
            except KeyError:
                pass
        finally:
            lock.release()
    
    def view(self, cls, attrs, expr=None):
        """view(cls, attrs, expr=None) -> Iterator of all Property tuples."""
        
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        lock = self._get_lock(cls)
        try:
            cache = self._caches[cls]
            seen = []
            
            # Run through our cache first. Hopefully, this will save us
            # calling expr(unit) twice for each unit.
            for id, pickledUnit in cache.iteritems():
                unit = pickle.loads(pickledUnit)
                if expr is None or expr(unit):
                    seen.append(tuple([getattr(unit, f) for f in attrs]))
            
            if self.nextstore:
                
                # Add the identifier attributes if not present. This is
                # necessary to avoid duplicating objects which are
                # already in our cache.
                fields = list(attrs)
                indices = []
                added_fields = 0
                for prop in cls.identifiers:
                    if prop.key not in fields:
                        fields.append(prop.key)
                        added_fields += 1
                    indices.append(fields.index(prop.key))
                
                for row in self.nextstore.view(cls, fields, expr):
                    id = tuple([row[x] for x in indices])
                    if id not in cache:
                        if added_fields:
                            # Remove the identifier columns from the row.
                            row = row[:len(row) - added_fields]
                        seen.append(row)
            return iter(seen)
        finally:
            lock.release()
    
    def distinct(self, cls, attrs, expr=None):
        """distinct(cls, attrs, expr=None) -> Distinct values for given attributes."""
        
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        # Rather than repeat the logic in recall() where we mix cached
        # and uncached Units, just call recall itself.
        distvals = {}
        for unit in self.recall(cls, expr):
            val = tuple([getattr(unit, f) for f in attrs])
            distvals[val] = None
        return distvals.keys()
    
    def reserve(self, unit):
        """Reserve storage space for the Unit."""
        unitClass = unit.__class__
        lock = self._get_lock(unitClass)
        try:
            cache = self._caches[unitClass]
            if self.nextstore:
                self.nextstore.reserve(unit)
            else:
                if not unit.sequencer.valid_id(unit.identity()):
                    unit.sequencer.assign(unit, cache.keys())
            # Pickle the Unit to discard extraneous attributes,
            # and avoid identity issues.
            id = unit.identity()
            cache[id] = pickle.dumps(unit)
            self._recallTimes[id] = datetime.datetime.now()
        finally:
            lock.release()
    
    def sweep(self, unitClass, lastSweepTime=None):
        lock = self._get_lock(unitClass)
        try:
            cache = self._caches[unitClass]
            for id in cache.keys():
                lastRecall = self._recallTimes.setdefault(id, None)
                if (lastRecall is None or lastSweepTime is None
                    or lastRecall < lastSweepTime):
                    unit = pickle.loads(cache[id])
                    if unit.dirty():
                        self.nextstore.save(unit)
                    
                    del cache[id]
                    del self._recallTimes[id]
        finally:
            lock.release()
    
    def sweep_all(self, lastSweepTime=None):
        for cls in self._caches:
            self.sweep(cls, lastSweepTime)
    
    def shutdown(self):
        self.sweep_all()
        if self.timer:
            # .cancel does nothing if the thread is already finished.
            self.timer.cancel()
    
    def add_property(self, cls, name):
        self.sweep(cls)
        if self.nextstore:
            self.nextstore.add_property(cls, name)
    
    def drop_property(self, cls, name):
        self.sweep(cls)
        if self.nextstore:
            self.nextstore.drop_property(cls, name)
    
    def rename_property(self, cls, oldname, newname):
        self.sweep(cls)
        if self.nextstore:
            self.nextstore.rename_property(cls, oldname, newname)


class BurnedProxy(CachingProxy):
    """A Caching Proxy Storage Manager which recalls and caches ALL Units.
    
    The big performance difference for a burned cache is that, once _any_
    Units have been recalled, further recalls won't hit the next store.
    Notice we didn't say "performance _benefit_" ;) That would depend to
    a great extent on the proxied store.
    """
    
    def _icached_units(self, cache, expr=None):
        if expr is None:
            for data in cache.itervalues():
                yield pickle.loads(data)
        else:
            for data in cache.itervalues():
                unit = pickle.loads(data)
                if expr(unit):
                    yield unit
    
    def recall(self, unitClass, expr=None):
        """Return a Unit iterator."""
        lock = self._get_lock(unitClass)
        try:
            cache = self._caches[unitClass]
            
            if (not cache) and self.nextstore:
                # Read ALL units from storage.
                now = datetime.datetime.now()
                for unit in self.nextstore.recall(unitClass, None):
                    id = unit.identity()
                    cache[id] = pickle.dumps(unit)
                    self._recallTimes[id] = now
            
            return self._icached_units(cache, expr)
        finally:
            lock.release()


class Adapter(object):
    """Transform values according to their type. Must be subclassed.
    
    In order for your subclass to work, you need to provide functions
    named 'coerce_' + type, where 'type' refers to the type you wish to
    support. Replace dots in the type name by underscores. For example,
    to coerce datetime.date objects, you must provide a function in your
    subclass named 'coerce_datetime_date'. For builtins, do not include
    the module name '__builtin__', just use 'coerce_unicode', for example.
    
    If you try to coerce a value for whose type you have not provided a
    coercion function, a TypeError is raised.
    
    When writing Adapters for Storage Managers, you should at least
    provide coerce_* functions for: bool, dict, float, int, list, long,
    NoneType, str, tuple, and unicode. For most applications, you should
    also provide:
        datetime.datetime
                .date
                .time
                .timedelta
    and:
        fixedpoint.FixedPoint or decimal.Decimal (preferably both)
    """
    
    def coerce(self, value, valuetype=None):
        """coerce(value, valuetype=None) -> value, coerced by valuetype."""
        if valuetype is None:
            valuetype = type(value)
        
        mod = valuetype.__module__
        if mod == "__builtin__":
            xform = "coerce_%s" % valuetype.__name__
        else:
            xform = "coerce_%s_%s" % (mod, valuetype.__name__)
        xform = xform.replace(".", "_")
        try:
            xform = getattr(self, xform)
        except AttributeError:
            raise TypeError("'%s' is not handled by %s." %
                            (valuetype, self.__class__))
        return xform(value)


class Version(object):
    
    def __init__(self, atoms):
        if isinstance(atoms, basestring):
            self.atoms = re.split(r'\W', atoms)
        else:
            self.atoms = [str(x) for x in atoms]
    
    def __str__(self):
        return ".".join([str(x) for x in self.atoms])
    
    def __cmp__(self, other):
        index = 0
        while index < len(self.atoms) and index < len(other.atoms):
            mine, theirs = self.atoms[index], other.atoms[index]
            if mine.isdigit() and theirs.isdigit():
                mine, theirs = int(mine), int(theirs)
            if mine < theirs:
                return -1
            if mine > theirs:
                return 1
            index += 1
        if index < len(other.atoms):
            return -1
        if index < len(self.atoms):
            return 1
        return 0

