try:
    import cPickle as pickle
except ImportError:
    import pickle

import thread

from dejavu import logic, UnitJoin
from dejavu.storage import StorageManager


class RAMStorage(StorageManager):
    """A Storage Manager which keeps all data in RAM."""
    
    def __init__(self, arena, allOptions={}):
        StorageManager.__init__(self, arena, allOptions)
        self._caches = {}       # id: pickled Unit
        self._cache_locks = {}
    
    def cachelen(self, cls):
        return len(self._caches.get(cls, {}))
    
    def cached_units(self, cls):
        return [pickle.loads(data) for data
                in self._caches.get(cls, {}).itervalues()]
    
    def _get_lock(self, cls):
        lock = self._cache_locks[cls]
        lock.acquire(True)
        return lock
    
    def recall(self, unitClass, expr=None):
        """Return a Unit iterator."""
        lock = self._get_lock(unitClass)
        try:
            cache = self._caches[unitClass]
            matches = {}
            
            for id, pickledUnit in cache.iteritems():
                unit = pickle.loads(pickledUnit)
                if expr is None or expr(unit):
                    matches[id] = unit
            
            return iter(matches.values())
        finally:
            lock.release()
    
    def multirecall(self, classes, expr):
        """multirecall(classes, expr) -> Full inner join units from each class."""
        if expr is None:
            expr = logic.Expression(lambda *args: True)
        
        firstcls = list(classes)[0]
        # TODO: deconstruct expr into a set of subexpr's, one for
        # each class in classes.
        filters = dict([(cls, None) for cls in classes])
        
        def combine(unitjoin):
            cls1, cls2 = unitjoin.class1, unitjoin.class2
            
            if isinstance(cls1, UnitJoin):
                table1 = combine(cls1)
                classlist1 = iter(cls1)
            else:
                table1 = [[x] for x in self.recall(cls1, filters[cls1])]
                classlist1 = [cls1]
            
            if isinstance(cls2, UnitJoin):
                table2 = combine(cls2)
                classlist2 = iter(cls2)
            else:
                table2 = [[x] for x in self.recall(cls2, filters[cls2])]
                classlist2 = [cls2]
            
            # Find an association between the two halves.
            ua = None
            for indexA, clsA in enumerate(classlist1):
                for indexB, clsB in enumerate(classlist2):
                    path = unitjoin.path or clsB.__name__
                    ua = clsA._associations.get(path, None)
                    if ua:
                        nearKey, farKey = ua.nearKey, ua.farKey
                        break
                    path = unitjoin.path or clsA.__name__
                    ua = clsB._associations.get(path, None)
                    if ua:
                        nearKey, farKey = ua.farKey, ua.nearKey
                        break
                if ua: break
            if ua is None:
                msg = ("No association found between %s and %s." % (cls1, cls2))
                raise errors.AssociationError(msg)
            
            unitrows = []
            if unitjoin.leftbiased is None:
                # INNER JOIN
                for row1 in table1:
                    nearVal = getattr(row1[indexA], nearKey)
                    for row2 in table2:
                        # Test against join constraint
                        farVal = getattr(row2[indexB], farKey)
                        if nearVal == farVal:
                            unitrows.append(row1 + row2)
            elif unitjoin.leftbiased is True:
                # LEFT JOIN
                for row1 in table1:
                    nearVal = getattr(row1[indexA], nearKey)
                    found = False
                    for row2 in table2:
                        # Test against join constraint
                        farVal = getattr(row2[indexB], farKey)
                        if nearVal == farVal:
                            unitrows.append(row1 + row2)
                            found = True
                    if not found:
                        unitrows.append(row1 + [unit.__class__() for unit in row2])
            else:
                # RIGHT JOIN
                for row2 in table2:
                    farVal = getattr(row2[indexB], farKey)
                    found = False
                    for row1 in table1:
                        # Test against join constraint
                        nearVal = getattr(row1[indexA], nearKey)
                        if nearVal == farVal:
                            unitrows.append(row1 + row2)
                            found = True
                    if not found:
                        unitrows.append([unit.__class__() for unit in row1] + row2)
            return unitrows
        
        for unitrow in combine(classes):
            if expr(*unitrow):
                yield unitrow
    
    def save(self, unit, forceSave=False):
        """save(unit, forceSave=False). -> Update storage from unit's data."""
        if unit.dirty() or forceSave:
            lock = self._get_lock(unit.__class__)
            try:
                unit.cleanse()
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
            try:
                del cache[id]
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
            
            for id, pickledUnit in cache.iteritems():
                unit = pickle.loads(pickledUnit)
                if expr is None or expr(unit):
                    seen.append(tuple([getattr(unit, f) for f in attrs]))
            
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
            if not unit.sequencer.valid_id(unit.identity()):
                unit.sequencer.assign(unit, cache.keys())
            # Pickle the Unit to discard extraneous attributes,
            # and avoid identity issues.
            cache[unit.identity()] = pickle.dumps(unit)
        finally:
            lock.release()
            unit.cleanse()
    
    def shutdown(self):
        self._caches = {}
        self._cache_locks = {}
    
    def create_database(self):
        pass
    
    drop_database = shutdown
    
    def create_storage(self, cls):
        self._caches[cls] = {}
        self._cache_locks[cls] = thread.allocate_lock()
    
    def has_storage(self, cls):
        return cls in self._caches
    
    def drop_storage(self, cls):
        self._caches.pop(cls, None)
        self._cache_locks.pop(cls, None)
    
    def add_property(self, cls, name):
        lock = self._get_lock(cls)
        try:
            cache = self._caches[cls]
            for id, pickledUnit in cache.items():
                unit = pickle.loads(pickledUnit)
                unit._properties[name] = None
                unit.cleanse()
                cache[id] = pickle.dumps(unit)
        finally:
            lock.release()
    
    def drop_property(self, cls, name):
        lock = self._get_lock(cls)
        try:
            cache = self._caches[cls]
            for id, pickledUnit in cache.items():
                unit = pickle.loads(pickledUnit)
                del unit._properties[name]
                unit.cleanse()
                cache[id] = pickle.dumps(unit)
        finally:
            lock.release()
    
    def rename_property(self, cls, oldname, newname):
        lock = self._get_lock(cls)
        try:
            cache = self._caches[cls]
            for id, pickledUnit in cache.items():
                unit = pickle.loads(pickledUnit)
                unit._properties[newname] = unit._properties[oldname]
                del unit._properties[oldname]
                unit.cleanse()
                cache[id] = pickle.dumps(unit)
        finally:
            lock.release()

