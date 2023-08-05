try:
    import cPickle as pickle
except ImportError:
    import pickle

import os
import shutil
import threading

import dejavu
from dejavu import errors, logic, storage


class StorageManagerFolders(storage.StorageManager):
    """StoreManager to save and retrieve Units in flat files.
    
    This is slightly different from shelve, in that this saves
    each Unit to its own folder, and each property to its own file.
    This is useful for storing large items like images and video
    for which you want both a native, readable file for the data
    and also the ability to store metadata.
    
    Unit properties which you want to use for binary data should
    be of type 'str'. The filename will be the property name,
    and the extension should be supplied in config.
    
    Be aware that this SM stores each Unit in its own folder,
    and your operating system may have hard limits or performance
    issues when the number of Units of a given class (or the number
    of classes) grows large.
    """
    
    def __init__(self, arena, allOptions={}):
        storage.StorageManager.__init__(self, arena, allOptions)
        
        root = allOptions['root']
        if not os.path.isabs(root):
            root = os.path.join(os.getcwd(), root)
        self.root = root
        
        self.mode = int(allOptions.get('mode', '0777'), 8)
        
        # Character to use for joining multiple identifiers
        # into a single folder name.
        self.idsepchar = allOptions.get('idsepchar', '_')
        
        # Map of file extensions. Keys should be "clsname.propname"
        # and values should contain the dot (if desired).
        self.extmap = dict([(k, v) for k, v in allOptions.iteritems()
                            if '.' in k])
        self.extdefault = allOptions.get('extdefault', '.txt')
        
        self.locks = {}
    
    def shelf(self, cls):
        """Return path, lock for the given cls."""
        clsname = cls.__name__
        if clsname not in self.locks:
            lock = self.locks[clsname] = threading.Lock()
        else:
            lock = self.locks[clsname]
        lock.acquire()
        
        path = os.path.join(self.root, clsname)
        if not os.path.exists(path):
            os.mkdir(path, self.mode)
        
        return path, lock
    
    def _pull(self, cls, root, idset):
        """Return data from the given path as a dict."""
        
        # Grab identifiers from the folder name.
        unitdict = dict(self.ids_from_folder(cls, idset))
        
        # Grab values from the files in the folder.
        clsname = cls.__name__
        for k in cls.properties:
            extkey = "%s.%s" % (clsname, k)
            ext = self.extmap.get(extkey, self.extdefault)
            
            fname = os.path.join(root, idset, "%s%s" % (k, ext))
            try:
                v = open(fname, 'rb').read()
                if getattr(cls, k).type is not str:
                    v = pickle.loads(v)
            except IOError, exc:
                v = None
            unitdict[k] = v
        
        return unitdict
    
    def recall(self, cls, expr=None):
        clsname = cls.__name__
        units = []
        
        path, lock = self.shelf(cls)
        try:
            root, dirs, _ = os.walk(path).next()
            for idset in dirs:
                unit = cls()
                unit._properties = self._pull(cls, root, idset)
                if expr is None or expr(unit):
                    unit.cleanse()
                    units.append(unit)
        finally:
            lock.release()
        
        for unit in units:
            yield unit
    
    def ids_from_folder(self, cls, fname):
        """Return a list of identifier (k, v) pairs from the given folder."""
        if fname == "__blank__":
            return [(k, "") for k in cls.identifiers]
        
        return [(k, getattr(cls, k).coerce(None, v))
                for k, v in zip(cls.identifiers,
                                fname.split(self.idsepchar))
                ]
    
    def folder_from_unit(self, unit):
        """Return the folder name for the given unit."""
        folder = self.idsepchar.join([str(getattr(unit, k))
                                      for k in unit.identifiers])
        if not folder:
            folder = "__blank__"
        return folder
    
    def _push(self, unit, abspath):
        """Persist unit properties into its folder.
        
        This assumes the folder exists and we have a lock on it.
        """
        cls = unit.__class__
        for key, value in unit._properties.iteritems():
            extkey = "%s.%s" % (cls.__name__, key)
            ext = self.extmap.get(extkey, self.extdefault)
            fname = "%s%s" % (key, ext)
            fname = os.path.join(abspath, fname)
            try:
                f = open(fname, 'wb')
            except IOError:
                raise
            
            try:
                if getattr(cls, key).type is not str:
                    value = pickle.dumps(value)
                f.write(value)
            finally:
                f.close()
    
    def reserve(self, unit):
        """Reserve a persistent slot for unit."""
        cls = unit.__class__
        path, lock = self.shelf(unit.__class__)
        try:
            if not unit.sequencer.valid_id(unit.identity()):
                root, dirs, _ = os.walk(path).next()
                ids = [[v for k, v in self.ids_from_folder(cls, dirname)]
                       for dirname in dirs]
                unit.sequencer.assign(unit, ids)
            
            fname = self.folder_from_unit(unit)
            fname = os.path.join(path, fname)
            if not os.path.exists(fname):
                os.mkdir(fname, self.mode)
            self._push(unit, fname)
        finally:
            lock.release()
            unit.cleanse()
    
    def save(self, unit, forceSave=False):
        """save(unit, forceSave=False). -> Update storage from unit's data."""
        if unit.dirty() or forceSave:
            path, lock = self.shelf(unit.__class__)
            try:
                fname = self.folder_from_unit(unit)
                self._push(unit, os.path.join(path, fname))
            finally:
                lock.release()
                unit.cleanse()
    
    def destroy(self, unit):
        """Delete the unit."""
        path, lock = self.shelf(unit.__class__)
        try:
            fname = self.folder_from_unit(unit)
            shutil.rmtree(os.path.join(path, fname))
        finally:
            lock.release()
    
    __version__ = "0.1"
    
    def version(self):
        return "%s %s" % (self.__class__.__name__, self.__version__)
    
    def view(self, cls, fields, expr=None):
        """view(cls, fields, expr=None) -> All value-tuples for given fields."""
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        path, lock = self.shelf(cls)
        try:
            globs = []
            root, dirs, _ = os.walk(path).next()
            for idset in dirs:
                unit = cls()
                unit._properties = self._pull(cls, root, idset)
                
                if expr is None or expr(unit):
                    globs.append(tuple([getattr(unit, field) for field in fields]))
            return globs
        finally:
            lock.release()
    
    def distinct(self, cls, fields, expr=None):
        """distinct(cls, fields, expr=None) -> Distinct values for given fields."""
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        path, lock = self.shelf(cls)
        try:
            globs = {}
            root, dirs, _ = os.walk(path).next()
            for idset in dirs:
                unit = cls()
                unit._properties = self._pull(cls, root, idset)
                
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
    
    
    #                               Schemas                               #
    
    def create_database(self):
        if not os.path.exists(self.root):
            os.makedirs(self.root)
    
    def drop_database(self):
        shutil.rmtree(self.root)
    
    def create_storage(self, cls):
        clsname = cls.__name__
        if clsname not in self.locks:
            lock = self.locks[clsname] = threading.Lock()
        else:
            lock = self.locks[clsname]
        lock.acquire()
        
        try:
            path = os.path.join(self.root, clsname)
            if not os.path.exists(path):
                os.mkdir(path, self.mode)
        finally:
            lock.release()
    
    def has_storage(self, cls):
        path = os.path.join(self.root, cls.__name__)
        return os.path.exists(path)
    
    def drop_storage(self, cls):
        path = os.path.join(self.root, cls.__name__)
        shutil.rmtree(path)
    
    def add_property(self, cls, name):
        pass
    
    def drop_property(self, cls, name):
        path, lock = self.shelf(cls)
        try:
            root, dirs, _ = os.walk(path).next()
            extkey = "%s.%s" % (cls.__name__, name)
            ext = self.extmap.get(extkey, self.extdefault)
            fname = "%s%s" % (name, ext)
            
            for idset in dirs:
                os.remove(os.path.join(root, idset, fname))
        finally:
            lock.release()
    
    def rename_property(self, cls, oldname, newname):
        path, lock = self.shelf(cls)
        try:
            extkey = "%s.%s" % (cls.__name__, oldname)
            ext = self.extmap.get(extkey, self.extdefault)
            oname = "%s%s" % (oldname, ext)
            
            extkey = "%s.%s" % (cls.__name__, newname)
            ext = self.extmap.get(extkey, self.extdefault)
            nname = "%s%s" % (newname, ext)
            
            root, dirs, _ = os.walk(path).next()
            for idset in dirs:
                os.rename(os.path.join(root, idset, oname),
                          os.path.join(root, idset, nname))
        finally:
            lock.release()
