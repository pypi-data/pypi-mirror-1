try:
    import cPickle as pickle
except ImportError:
    import pickle

import sha
import types
import warnings

import logic
import errors


__all__ = ['UnitAssociation', 'ToMany', 'ToOne', 'UnitJoin',
           'Unit', 'UnitProperty', 'TriggerProperty', 'MetaUnit',
           'UnitSequencerInteger', 'UnitSequencerNull',
           'UnitSequencerUnicode',
           '_define_fixedpoint_states', '_fix_fixedpoint_cmp',
           ]

def _fix_fixedpoint_cmp():
    """Add methods to fixedpoint to support pickling."""
    import fixedpoint
    def __cmp__(self, other):
        if other is None:
            return 1
        xn, yn, p = fixedpoint._norm(self, other, FixedPoint=type(self))
        return cmp(xn, yn)
    fixedpoint.FixedPoint.__cmp__ = __cmp__

def _define_fixedpoint_states():
    """Add methods to fixedpoint to support pickling."""
    import fixedpoint
    
    if not hasattr(fixedpoint.FixedPoint, "__getstate__"):
        def __getstate__(self):
            return (self.n, self.p)
        fixedpoint.FixedPoint.__getstate__ = __getstate__
        
        def __setstate__(self, v):
            self.n, self.p = v
        fixedpoint.FixedPoint.__setstate__ = __setstate__


###########################################################################
##                                                                       ##
##                             Associations                              ##
##                                                                       ##
###########################################################################


class UnitAssociation(object):
    """Non-data descriptor method to retrieve related Units via attributes."""
    
    to_many = None
    
    def __init__(self, nearKey, farClass, farKey):
        # Since the keys will be used as kwarg keys, they must be strings.
        self.nearKey = str(nearKey)
        self.farKey = str(farKey)
        
        self.nearClass = None
        self.farClass = farClass
    
    def __get__(self, unit, unitclass=None):
        if unit is None:
            # When calling on the class instead of an instance...
            return self
        else:
            m = types.MethodType(self.related, unit, unitclass)
            return m
    
    def __delete__(self, unit):
        raise AttributeError("Unit Associations may not be deleted.")
    
    def related(self, unit, expr=None):
        raise NotImplementedError


class ToOne(UnitAssociation):
    
    to_many = False
    
    def related(self, unit, expr=None):
        value = getattr(unit, self.nearKey)
        if value is None:
            return None
        
        f = logic.filter(**{self.farKey: value})
        if expr is not None:
            f += expr
        units = unit.sandbox.xrecall(self.farClass, f)
        try:
            return units.next()
        except StopIteration:
            return None


class ToMany(UnitAssociation):
    
    to_many = True
    
    def related(self, unit, expr=None):
        value = getattr(unit, self.nearKey)
        if value is None:
            return []
        
        f = logic.filter(**{self.farKey: value})
        if expr is not None:
            f += expr
        return unit.sandbox.recall(self.farClass, f)


class UnitJoin(object):
    
    def __init__(self, class1, class2, leftbiased=None):
        self.class1 = class1
        self.class2 = class2
        self.leftbiased = leftbiased
        
        # From http://msdn.microsoft.com/library/en-us/
        #           dnacc2k/html/acintsql.asp#acintsql_joins
        # "OUTER JOINs can be nested inside INNER JOINs in a multi-table
        # join, but INNER JOINs cannot be nested inside OUTER JOINs."
        if leftbiased is not None:
            if ((isinstance(class1, UnitJoin) and class1.leftbiased is None)
                or (isinstance(class1, UnitJoin) and class1.leftbiased is None)):
                warnings.warn("Some StorageManagers cannot nest an INNER "
                              "JOIN within an OUTER JOIN. Consider rewriting "
                              "your join tree.", errors.StorageWarning)
    
    def __str__(self):
        if self.leftbiased is None:
            op = "&"
        elif self.leftbiased is True:
            op = "<<"
        else:
            op = ">>"
        if isinstance(self.class1, UnitJoin):
            name1 = str(self.class1)
        else:
            name1 = self.class1.__name__
        if isinstance(self.class2, UnitJoin):
            name2 = str(self.class2)
        else:
            name2 = self.class2.__name__
        return "(%s %s %s)" % (name1, op, name2)
    __repr__ = __str__
    
    def __iter__(self):
        def genclasses():
            if isinstance(self.class1, UnitJoin):
                for cls in iter(self.class1):
                    yield cls
            else:
                yield self.class1
            if isinstance(self.class2, UnitJoin):
                for cls in iter(self.class2):
                    yield cls
            else:
                yield self.class2
        return genclasses()
    
    def __lshift__(self, other):
        if isinstance(other, (MetaUnit, UnitJoin)):
            return UnitJoin(self, other, leftbiased=True)
        else:
            raise TypeError("Joined classes must be UnitJoin or Unit subclasses.")
    __rrshift__ = __lshift__
    
    def __rshift__(self, other):
        if isinstance(other, (MetaUnit, UnitJoin)):
            return UnitJoin(self, other, leftbiased=False)
        else:
            raise TypeError("Joined classes must be UnitJoin or Unit subclasses.")
    __rlshift__ = __rshift__
    
    def __add__(self, other):
        if isinstance(other, (MetaUnit, UnitJoin)):
            return UnitJoin(self, other)
        else:
            raise TypeError("Joined classes must be UnitJoin or Unit subclasses.")
    __and__ = __add__
    
    def __radd__(self, other):
        if isinstance(other, (MetaUnit, UnitJoin)):
            return UnitJoin(other, self)
        else:
            raise TypeError("Joined classes must be UnitJoin or Unit subclasses.")
    __rand__ = __radd__


###########################################################################
##                                                                       ##
##                            Unit Sequencers                            ##
##                                                                       ##
###########################################################################


# All Units must possess at least one UnitProperty which is an identifier.
# The sequencing of identifiers depends upon their type and the particular
# needs of the class. Pick one of these UnitSequencers to fit your subclass.
# When creating new sequencers, you should aim to generate identifiers that
# obey the builtin max() and min() functions.

class UnitSequencerNull(object):
    """A null sequencer for Unit identifiers. Sequencing will error.
    
    In many cases, identifier values simply have no algorithmic sequence;
    for example, a set of Employee Units might use Social Security
    Numbers for identifiers (which you should never, ever do ;).
    
    In other cases, sequencing will be best handled by custom algorithms
    within application code; that is, the job of abstracting the sequence
    logic would not be worth the effort.
    """
    
    def __init__(self, type=unicode):
        self.type = type
    
    def valid_id(self, value):
        for atom in value:
            if atom is None:
                return False
        return True
    
    def assign(self, unit, sequence):
        raise StopIteration("No sequence defined.")


class UnitSequencerInteger(object):
    """A sequencer for Unit identifiers, where id[i+1] == id[i] + 1."""
    
    def __init__(self, type=int, initial=1):
        self.type = type
        self.initial = initial
    
    def valid_id(self, value):
        return value != (None,) # and value >= self.initial?
    
    def assign(self, unit, sequence):
        newvalue= self.initial
        if sequence:
            m = max(sequence)
            if m != (None,):
                newvalue = m[0] + 1
        unit.identifiers[0].__set__(unit, newvalue)


class UnitSequencerUnicode(object):
    """UnitSequencerUnicode(type=unicode, width=6,
        range="abcdefghijklmnopqrstuvwxyz")
    A sequencer for Unit identifiers, where e.g. next(['abc']) == 'abd'."""
    
    def __init__(self, type=unicode, width=6,
                 range="abcdefghijklmnopqrstuvwxyz"):
        self.type = type
        self.width = width
        self.range = range
    
    def valid_id(self, value):
        return value != (None,)
    
    def assign(self, unit, sequence):
        r = self.range
        newvalue = r[0] * self.width
        if sequence:
            maxid = max(sequence)[0]
            if len(maxid) != self.width:
                raise OverflowError("'%s' is not of width %s." %
                                    (maxid, self.width))
            for i in range(self.width - 1, -1, -1):
                pos = r.index(maxid[i]) + 1
                if pos >= len(r) or pos < 0:
                    maxid = maxid[:i] + r[0] + maxid[i+1:]
                else:
                    maxid = maxid[:i] + r[pos] + maxid[i+1:]
                    break
            else:
                raise OverflowError("Next identifier exceeds width %s."
                                    % self.width)
            newvalue = maxid
        unit.identifiers[0].__set__(unit, newvalue)


###########################################################################
##                                                                       ##
##                                 Units                                 ##
##                                                                       ##
###########################################################################


class UnitProperty(object):
    """UnitProperty(type=unicode, index=False, hints=None, key=None)
    Data descriptor for Unit data which will persist in storage.
    
    hints: A dictionary which provides named hints to Storage Managers
        concerning the nature of the data. A common use, for example,
        is to inform Managers that would usually store unicode strings
        as strings of length 255, that a particular value should be
        a larger object; this is done with a 'bytes' mapping, such as:
        hints = {u'bytes': 0}, where 0 implies no limit. Canonical storage
        hint names and implementation details may be found in /storage
        documentation.
    """
    
    def __init__(self, type=unicode, index=False, hints=None, key=None, default=None):
        if type.__name__ == 'FixedPoint':
            # fixedpoint can't handle "FixedPoint() != None" in Python 2.4
            _fix_fixedpoint_cmp()
            
            # fixedpoint.Fixedpoint can't be pickled because it
            # defines __slots__ but not __getstate__. Provide it.
            _define_fixedpoint_states()
        
        self.type = type
        self.index = index
        if hints is None: hints = {}
        self.hints = hints
        self.key = key
        self.default = default
    
    def __get__(self, unit, unitclass=None):
        if unit is None:
            # When calling on the class instead of an instance...
            return self
        else:
            return unit._properties[self.key]
    
    def __set__(self, unit, value):
        if self.coerce:
            value = self.coerce(unit, value)
        oldvalue = unit._properties[self.key]
        if oldvalue != value:
            unit._properties[self.key] = value
    
    def coerce(self, unit, value):
        if value is not None and not isinstance(value, self.type):
            # Try to coerce the value.
            try:
                value = self.type(value)
            except Exception, x:
                x.args += (value, type(value))
                raise
        return value
    
    def __delete__(self, unit):
        raise AttributeError("Unit Properties may not be deleted.")


class TriggerProperty(UnitProperty):
    """UnitProperty subclass for managing immediate triggers on set.
    
    The __set__ method will call the on_set method, which should then
    deal with the new value.
    """
    
    def __set__(self, unit, value):
        if self.coerce:
            value = self.coerce(unit, value)
        oldvalue = unit._properties[self.key]
        if oldvalue != value:
            unit._properties[self.key] = value
            if unit.sandbox:
                self.on_set(unit, oldvalue)
    
    def on_set(self, unit, oldvalue):
        pass


class MetaUnit(type):
    
    def __init__(cls, name, bases, dct):
        # Make a copy of the parent class' _associations, and store
        # it in the _associations attribute of this subclass. In this
        # manner, Unit Associations should propagate down to subclasses,
        # but not back up to superclasses.
        if hasattr(cls, "_associations"):
            assocs = cls._associations.copy()
        else:
            assocs = {}
        
        # Make a copy of the parent class' _properties keys, and store
        # it in the _properties attribute of this subclass. In this
        # manner, Unit Property keys should propagate down to subclasses,
        # but not back up to superclasses.
        if hasattr(cls, "_properties"):
            props = dict.fromkeys(cls._properties.keys())
        else:
            props = {}
        
        for name, val in dct.iteritems():
            # Now grab any new UnitProperties defined in this class.
            # Overwrite any properties defined in superclasses.
            if isinstance(val, UnitProperty):
                # If the UnitProperty.key is None,
                # supply it from the attribute name (name).
                if val.key is None:
                    val.key = name
                props[name] = val
            
            # Remove any properties from the parent class if requested
            # (request by binding the parent's UnitProperty.key to None).
            if name in props and val is None:
                del props[name]
                
            # Now grab any new UnitAssociations defined in this class.
            if isinstance(val, UnitAssociation):
                val.nearClass = cls
                assocs[name] = val
        
        cls._properties = props
        cls._associations = assocs
    
    def __lshift__(self, other):
        if isinstance(other, (MetaUnit, UnitJoin)):
            return UnitJoin(self, other, leftbiased=True)
        else:
            raise TypeError("Joined classes must be UnitJoin or Unit subclasses.")
    __rrshift__ = __lshift__
    
    def __rshift__(self, other):
        if isinstance(other, (MetaUnit, UnitJoin)):
            return UnitJoin(self, other, leftbiased=False)
        else:
            raise TypeError("Joined classes must be UnitJoin or Unit subclasses.")
    __rlshift__ = __rshift__
    
    def __add__(self, other):
        if isinstance(other, (MetaUnit, UnitJoin)):
            return UnitJoin(self, other)
        else:
            raise TypeError("Joined classes must be UnitJoin or Unit subclasses.")
    __and__ = __add__
    
    def __radd__(self, other):
        if isinstance(other, (MetaUnit, UnitJoin)):
            return UnitJoin(other, self)
        else:
            raise TypeError("Joined classes must be UnitJoin or Unit subclasses.")
    __rand__ = __radd__


class Unit(object):
    """Unit(**kwarg properties). A generic, persistent object.
    
    Units are the building-block of Dejavu. They are purposefully lightweight,
    relying on Sandboxes to cache them, which in turn rely on Storage Managers
    to load and save them.
    
    They maintain their own "schema" via UnitProperty objects, so that the
    Storage Managers don't need to know every detail about every Unit.
    Storage Managers for simple databases, for example, will simply create
    a single flat table for each unit type. If you write a custom Storage
    Manager, you can do as you like; the only place you might run into a
    problem is if you write a custom Storage Manager for custom Unit types,
    because the knowledge between the two is indeterminate. For example,
    if we provide a standard StorageManagerForLotusNotes, and you create
    custom Units which interface with it, you should probably subclass and
    extend our StorageManagerForLotusNotes with some custom storage logic.
    
    sandbox: The sandbox in which the Unit "lives". Also serves as a flag
        indicating whether this Unit has finished the initial creation
        process.
        
        Sandboxes receive Units during recall() and memorize();
        these processes should set the sandbox attribute.
    
    dirty: indicates whether elements in the _properties dictionary
        have been modified. This flag is used by Sandboxes to optimize
        forget(): they do not ask Storage Managers to save data for Units
        which have not been modified. Because SM's may cache Units, no code
        should set this flag other than UnitProperty.__set__ and SM's.
    """
    
    __metaclass__ = MetaUnit
    _properties = {}
    _associations = {}
    
    # The default ID type is int. If you wish to use a different type for
    # the ID's of a subclass of Unit, just overwrite ID, e.g.:
    #     ID = UnitProperty(unicode, index=True)
    #       or
    #     UnitSubclass.set_property('ID', unicode, index=True)
    #       or even
    #     UnitSubclass.ID.type = unicode
    ID = UnitProperty(int, index=True)
    sequencer = UnitSequencerInteger()
    identifiers = (ID,)
    
    def __init__(self, **kwargs):
        # Copy the class _properties dict into self._properties,
        # setting each value to the UnitProperty.default.
        cls = self.__class__
        self._properties = dict([(k, getattr(cls, k).default)
                                 for k in cls._properties.keys()])
        
        self.sandbox = None
        
        # Make sure we cleanse before assigning properties from kwargs,
        # or the new unit won't get saved if there are no further changes.
        self.cleanse()
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
    
    def repress(self):
        """repress() -> Remove this Unit from memory (do not destroy)."""
        self.sandbox.repress(self)
    
    def forget(self):
        """forget() -> Destroy this Unit."""
        self.sandbox.forget(self)
    
    def __copy__(self):
        newUnit = self.__class__()
        for key in self.__class__.properties():
            if key not in self.identifiers:
                newUnit._properties[key] = self._properties[key]
        for prop in self.identifiers:
            prop.__set__(newUnit, None)
        newUnit.sandbox = None
        return newUnit
    
    #                        Pickle data                         #
    
    def __getstate__(self):
        return (self._properties, self._initial_property_hash)
    
    def __setstate__(self, state):
        self.sandbox = None
        self._properties, self._initial_property_hash = state
    
    
    #                         Properties                         #
    
    def identity(self):
        # Must be immutable for use as a dictionary key.
        return tuple([prop.__get__(self) for prop in self.identifiers])
    
    def _property_hash(self):
        try:
            return sha.new(pickle.dumps(self._properties)).digest()
        except TypeError, x:
            x.args += (self.__class__.__name__, self._properties.keys())
            raise
    
    def dirty(self):
        return self._initial_property_hash != self._property_hash()
    
    def cleanse(self):
        self._initial_property_hash = self._property_hash()
    
    def set_property(cls, key, type=unicode, index=False,
                     descriptor=UnitProperty):
        """Set a Unit Property for cls."""
        setattr(cls, key, descriptor(type, index, key=key))
        cls._properties[key] = None
    set_property = classmethod(set_property)
    
    def set_properties(cls, types={}, descriptor=UnitProperty):
        """Set Unit Properties for cls."""
        for key, typ in types.items():
            cls.set_property(key, typ, False, descriptor)
    set_properties = classmethod(set_properties)
    
    def remove_property(cls, key):
        delattr(cls, key)
        del cls._properties[key]
    remove_property = classmethod(remove_property)
    
    def indices(cls):
        """cls.indices() -> tuple of names of indexed UnitProperties."""
        product = []
        for key in cls.properties():
            try:
                if getattr(cls, key).index:
                    product.append(key)
            except AttributeError, x:
                x.args += (cls, key)
                raise
        return tuple(product)
    indices = classmethod(indices)
    
    def properties(cls):
        """cls.properties() -> list of UnitProperty names."""
        return cls._properties.iterkeys()
    properties = classmethod(properties)
    
    def property_type(cls, key):
        """cls.property_type(key) -> type of the given UnitProperty."""
        # Retrieving from the class gives us
        # the UnitProperty object, not its value.
        return getattr(cls, key).type
    property_type = classmethod(property_type)
    
    def adjust(self, **values):
        """adjust(**values) -> Set UnitProperties by key, value pairs."""
        for key, val in values.iteritems():
            setattr(self, key, val)
    
    
    #                        Associations                        #
    
    def associate(nearClass, nearKey, farClass, farKey, nearDescriptor, farDescriptor):
        """Set UnitAssociations between nearClass.key and farClass.farKey."""
        # Mangle this class first
        farClassName = farClass.__name__
        descriptor = nearDescriptor(nearKey, farClass, farKey)
        descriptor.nearClass = nearClass
        setattr(nearClass, farClassName, descriptor)
        nearClass._associations[farClassName] = descriptor
        
        # Now mangle the far class
        nearClassName = nearClass.__name__
        descriptor = farDescriptor(farKey, nearClass, nearKey)
        descriptor.nearClass = farClass
        setattr(farClass, nearClassName, descriptor)
        farClass._associations[nearClassName] = descriptor
    associate = classmethod(associate)
    
    def one_to_many(nearClass, nearKey, farClass, farKey):
        nearClass.associate(nearKey, farClass, farKey, ToMany, ToOne)
    one_to_many = classmethod(one_to_many)
    
    def one_to_one(nearClass, nearKey, farClass, farKey):
        nearClass.associate(nearKey, farClass, farKey, ToOne, ToOne)
    one_to_one = classmethod(one_to_one)
    
    def many_to_one(nearClass, nearKey, farClass, farKey):
        nearClass.associate(nearKey, farClass, farKey, ToOne, ToMany)
    many_to_one = classmethod(many_to_one)
    
    def associations(cls):
        """cls.associations() -> list of UnitAssociation names."""
        return cls._associations.iterkeys()
    associations = classmethod(associations)
    
    def add(self, *units):
        """add(*units) -> Auto-create a relation between self and unit(s)."""
        cls = self.__class__
        for unit in units:
            try:
                ua = cls._associations[unit.__class__.__name__]
            except KeyError:
                msg = "'%s' is not associated with '%s'" % (cls, unit.__class__)
                raise errors.AssociationError(msg)
            
            nearval = getattr(self, ua.nearKey)
            farval = getattr(unit, ua.farKey)
            if nearval is None:
                if farval is None:
                    raise errors.AssociationError("At least one Unit key must be set.")
                else:
                    setattr(self, ua.nearKey, farval)
            else:
                # If far key is already set, it will simply be overwritten.
                setattr(unit, ua.farKey, nearval)
