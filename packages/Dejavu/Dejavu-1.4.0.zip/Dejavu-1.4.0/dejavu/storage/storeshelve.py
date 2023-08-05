try:
    from bsddb._db import DBNoSuchFileError
except ImportError:
    DBNoSuchFileError = object()

import os

try:
    import cPickle as pickle
except ImportError:
    import pickle

import shelve
import threading

import dejavu
from dejavu import storage, logic


class StorageManagerShelve(storage.StorageManager):
    """StoreManager to save and retrieve Units via stdlib shelve."""
    
    def __init__(self, name, arena, allOptions={}):
        storage.StorageManager.__init__(self, name, arena, allOptions)
        
        path = allOptions['Path']
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        if not os.path.exists(path):
            raise IOError(2, "No such directory: '%s'" % path)
        self.shelvepath = path
        
        # A dictionary whose keys are classnames and whose
        # values are objects returned by shelve.open().
        # Those values are dict-like objects with keys of type 'str'.
        self.shelves = {}
        
        self.locks = {}
    
    def shutdown(self):
        while self.shelves:
            clsname, shelf = self.shelves.popitem()
            shelf.close()
    
    def shelf(self, cls):
        clsname = cls.__name__
        if clsname not in self.locks:
            lock = self.locks[clsname] = threading.Lock()
        else:
            lock = self.locks[clsname]
        lock.acquire()
        
        s = self.shelves.get(clsname)
        if s is None:
            s = shelve.open(self.filename(clsname), 'w')
            self.shelves[clsname] = s
        
        return s, lock
    
    def recall(self, cls, expr=None):
        units = []
        data, lock = self.shelf(cls)
        try:
            if data:
                for unitdict in data.itervalues():
                    unit = cls()
                    # Set the attribute directly to avoid __set__ overhead.
                    unit._properties = unitdict
                    if expr is None or expr(unit):
                        unit.cleanse()
                        units.append(unit)
        finally:
            lock.release()
        
        for unit in units:
            yield unit
    
    def key(self, arg):
        return pickle.dumps(arg)
    
    def reserve(self, unit):
        """reserve(unit). -> Reserve a persistent slot for unit."""
        data, lock = self.shelf(unit.__class__)
        try:
            if not unit.sequencer.valid_id(unit.identity()):
                ids = [[row[prop.key] for prop in unit.identifiers]
                       for row in data.itervalues()]
                unit.sequencer.assign(unit, ids)
            data[self.key(unit.identity())] = unit._properties
        finally:
            lock.release()
            unit.cleanse()
    
    def save(self, unit, forceSave=False):
        """save(unit, forceSave=False). -> Update storage from unit's data."""
        if unit.dirty() or forceSave:
            data, lock = self.shelf(unit.__class__)
            try:
                # Replace the entire value to get around writeback issues.
                # See the docs on "shelve" for more info.
                data[self.key(unit.identity())] = unit._properties
            finally:
                lock.release()
                unit.cleanse()
    
    def destroy(self, unit):
        """Delete the unit."""
        data, lock = self.shelf(unit.__class__)
        try:
            del data[self.key(unit.identity())]
        finally:
            lock.release()
    
    def version(self):
        import sys
        return "Shelve version: %s" % sys.version
    
    def view(self, cls, fields, expr=None):
        """view(cls, fields, expr=None) -> All value-tuples for given fields."""
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        data, lock = self.shelf(cls)
        try:
            globs = []
            for unitdict in data.itervalues():
                unit = cls()
                # Set the attributes directly to avoid __set__ overhead.
                unit._properties = unitdict
                if expr is None or expr(unit):
                    globs.append(tuple([getattr(unit, field) for field in fields]))
            return globs
        finally:
            lock.release()
    
    def distinct(self, cls, fields, expr=None):
        """distinct(cls, fields, expr=None) -> Distinct values for given fields."""
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        data, lock = self.shelf(cls)
        try:
            globs = {}
            for unitdict in data.itervalues():
                unit = cls()
                # Set the attributes directly to avoid __set__ overhead.
                unit._properties = unitdict
                if expr is None or expr(unit):
                    key = tuple([getattr(unit, field) for field in fields])
                    globs[key] = None
            return globs.keys()
        finally:
            lock.release()
    
    def multirecall(self, classes, expr):
        """multirecall(classes, expr) -> Full inner join units."""
        if expr is None:
            expr = logic.Expression(lambda *args: True)
        
        firstcls = list(classes)[0]
        # TODO: deconstruct expr into a set of subexpr's, one for
        # each class in classes.
        filters = dict([(cls, None) for cls in classes])
        
        def combine(unitjoin):
            cls1, cls2 = unitjoin.class1, unitjoin.class2
            
            if isinstance(cls1, dejavu.UnitJoin):
                table1 = combine(cls1)
                classlist1 = iter(cls1)
            else:
                table1 = [[x] for x in self.recall(cls1, filters[cls1])]
                classlist1 = [cls1]
            
            if isinstance(cls2, dejavu.UnitJoin):
                table2 = combine(cls2)
                classlist2 = iter(cls2)
            else:
                table2 = [[x] for x in self.recall(cls2, filters[cls2])]
                classlist2 = [cls2]
            
            # Find an association between the two halves.
            ua = None
            for indexA, clsA in enumerate(classlist1):
                for indexB, clsB in enumerate(classlist2):
                    ua = clsA._associations.get(clsB.__name__, None)
                    if ua:
                        nearKey, farKey = ua.nearKey, ua.farKey
                        break
                    ua = clsB._associations.get(clsA.__name__, None)
                    if ua:
                        nearKey, farKey = ua.farKey, ua.nearKey
                        break
                if ua: break
            if ua is None:
                msg = ("No association found between %s and %s." % (cls1, cls2))
                raise dejavu.AssociationError(msg)
            
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
    
    ext = ".djv"
    
    def filename(self, clsname):
        if not isinstance(clsname, basestring):
            clsname = clsname.__name__
        return os.path.join(self.shelvepath, clsname + self.ext)
        
    #                               Schemas                               #
    
    def create_database(self):
        if not os.path.exists(self.shelvepath):
            os.makedirs(self.shelvepath)
    
    def drop_database(self):
        while self.shelves:
            clsname, shelf = self.shelves.popitem()
            shelf.close()
        
        for name in os.listdir(self.shelvepath):
            name = os.path.join(self.shelvepath, name)
            if not os.path.isdir(name) and name.endswith(self.ext):
                os.remove(name)
    
    def create_storage(self, cls):
        clsname = cls.__name__
        if clsname not in self.locks:
            lock = self.locks[clsname] = threading.Lock()
        else:
            lock = self.locks[clsname]
        lock.acquire()
        
        try:
            s = shelve.open(self.filename(clsname), 'n')
            self.shelves[clsname] = s
        finally:
            lock.release()
    
    def has_storage(self, cls):
        return os.path.exists(self.filename(cls))
    
    def drop_storage(self, cls):
        clsname = cls.__name__
        try:
            shelf = self.shelves.pop(clsname)
        except KeyError:
            pass
        else:
            shelf.close()
        os.remove(self.filename(clsname))
    
    def add_property(self, cls, name):
        data, lock = self.shelf(cls)
        try:
            for id, props in data.items():
                props[name] = None
                data[id] = props
        finally:
            lock.release()
    
    def drop_property(self, cls, name):
        data, lock = self.shelf(cls)
        try:
            for id, props in data.items():
                del props[name]
                data[id] = props
        finally:
            lock.release()
    
    def rename_property(self, cls, oldname, newname):
        data, lock = self.shelf(cls)
        try:
            for id, props in data.items():
                props[newname] = props[oldname]
                del props[oldname]
                data[id] = props
        finally:
            lock.release()
