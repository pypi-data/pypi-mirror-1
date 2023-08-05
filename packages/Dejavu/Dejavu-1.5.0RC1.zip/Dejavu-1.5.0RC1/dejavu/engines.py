"""
Notice in particular that UnitCollection, UnitEngineRule, and UnitEngine
are all _temporary_ Units. Even when you memorize them, they won't be
persistent unless you set each instance's Expiration to None. If you
use UnitEngine.immortalize(), it will make all of its rules immortal
(no Expiration) as well.
"""

import threading
import datetime
try:
    import cPickle as pickle
except ImportError:
    import pickle

import dejavu
from dejavu import errors, logic, recur


class TemporaryUnit(dejavu.Unit):
    
    Expiration = dejavu.UnitProperty(datetime.datetime)
    
    def on_recall(self):
        if self.Expiration is not None:
            if self.Expiration <= datetime.datetime.now():
                self.forget()
                raise errors.UnrecallableError
            else:
                self.decay(minutes=15)
    
    def decay(self, **kw):
        """decay(**kw) -> Set Expiration to now() + timedelta(**kw)."""
        self.Expiration = datetime.datetime.now() + datetime.timedelta(**kw)


class TemporarySweeper(recur.Worker):
    """A worker to sweep out expired TemporaryUnit's."""
    
    def work(self):
        """Start a cycle of scheduled work."""
        now = datetime.datetime.now()
        f = lambda x: x.Expiration != None and x.Expiration <= now
        box = self.arena.new_sandbox()
        
        for cls in self.arena._registered_classes:
            if issubclass(cls, TemporaryUnit):
                # Running box.recall will call TemporaryUnit.on_recall,
                # which should forget expired units.
                box.recall(cls, f)
        box.flush_all()


class UnitCollection(TemporaryUnit):
    """A Set of Unit identifiers.
    
    Type: Unit Type of all Units referenced by this collection.
    
    The Unit Collection is primarily for use as an index for Units.
    Unit Engines use Expressions and other rules to transform a Collection
    as a whole. These classes consume and produce Unit Collections.
    The Unit Collection provides special methods for iteration, whether
    reading or writing, to avoid errors common with multi-process/
    multi-threaded access.
    
    UnitCollection is a subclass of Unit, so that it can be managed by
    Sandboxes. However, due to the structure of the data contained in a
    UnitCollection, it is recommended that Storage Managers use different
    techniques to store and retrieve Unit Collections. They do not need
    more than the ID's of their contained Units stored, since they will
    recall such Units as needed. Not every Storage Manager is going to be
    able to handle this kind of dynamic storage; deployers-- examine your
    Storage Managers and make sure they can!
    """
    
    Members = dejavu.UnitProperty(list)
    EngineID = dejavu.UnitProperty(int, index=True)
    Type = dejavu.UnitProperty()
    Timestamp = dejavu.UnitProperty(datetime.datetime)
    
    def __init__(self, **kwargs):
        dejavu.Unit.__init__(self)
        self.Members = []
        self._mutex = threading.RLock()
        
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
    
    def __getstate__(self):
        return (self._properties, self._initial_property_hash)
    
    def __setstate__(self, state):
        self.sandbox = None
        self._mutex = threading.RLock()
        self._properties, self._initial_property_hash = state
    
    def acquire(self):
        self._mutex.acquire(True)
    
    def release(self):
        self._mutex.release()
    
    def __len__(self):
        return len(self.Members)
    
    def add(self, ID):
        self.acquire()
        try:
            if ID not in self.Members:
                self.Members.append(ID)
        finally:
            self.release()
    
    def unit_class(self):
        return self.sandbox.arena.class_by_name(self.Type)
    
    def ids(self):
        self.acquire()
        try:
            return self.Members[:]
        finally:
            self.release()
    
    def units(self, quota=None):
        cls = self.unit_class()
        
        output = []
        self.acquire()
        try:
            for i, eachID in enumerate(self.Members):
                if quota and i >= quota:
                    break
                filter = dict(zip(cls.identifiers, eachID))
                unit = self.sandbox.unit(cls, **filter)
                if unit:
                    output.append(unit)
        finally:
            self.release()
        return output
    
    def xdict(self, attr):
        """Return a dictionary of {Unit.attr: [Unit, Unit, ...]}."""
        product = {}
        self.acquire()
        try:
            for unit in self.units():
                key = getattr(unit, attr)
                product.setdefault(key, []).append(unit)
        finally:
            self.release()
        return product
    
    def __copy__(self):
        newUnit = dejavu.Unit.__copy__(self)
        newUnit.Members = self.Members[:]
        return newUnit


operations = [              #       OPERAND
    'COPY',                 # SetID of mixin
    'CREATE',               # New type (= class.__name__)
    'DIFFERENCE',           # SetID of mixin
    'FILTER',               # logic.Expression
    'FUNCTION',             # key into arena.engine_functions dict
    'INTERSECTION',         # SetID of mixin
    'RETURN',               # 
    'TRANSFORM',            # New type (= class.__name__)
    'UNION',                # SetID of mixin
    ]


class RuleProperty(dejavu.TriggerProperty):
    def on_set(self, unit, oldvalue):
        eng = unit.UnitEngine()
        if eng:
            eng.update_final_class()

class EngIDProperty(dejavu.TriggerProperty):
    def on_set(self, unit, oldvalue):
        eng = unit.sandbox.unit(UnitEngine, ID=oldvalue)
        if eng:
            eng.update_final_class()
        
        eng = unit.UnitEngine()
        if eng:
            eng.update_final_class()

class UnitEngineRule(TemporaryUnit):
    """A Rule for Unit Engines."""
    
    Operation = RuleProperty(str)
    SetID = RuleProperty(int)
    Operand = RuleProperty(str, False, hints = {u'bytes': 0})
    Sequence = RuleProperty(int)
    EngineID = EngIDProperty(int, index=True)
    
    def __init__(self, **kwargs):
        """kw: Operation, SetID, Operand=(Type | logic.Expression | otherSet)
        
        TRANSFORM:
            If the Operation is 'TRANSFORM', the Operand shall be the name of
            a Unit type. The snapshot will consist of the identifiers of all
            units of that Type which are associated with the current snapshot.
        
        FILTER:
            If the Operation is 'FILTER', the Operand shall be a
            logic.Expression, and the snapshot will consist of the
            identifiers of Units which match the Expression.
        
        So, a typical Engine might have a set of rules which look like:
            --Operation--   --Set-- --Operand--
            CREATE          1       Invoice         # Full set
            FILTER          1       (Expression)    # modifies Set 1
            CREATE          2       Inventory       # Full set
            FILTER          2       (Expression)    # modifies Set 2
            FILTER          2       (Expression)    # modifies Set 2
            TRANSFORM       2       Invoice         # modifies Set 2
            DIFFERENCE      1       2               # Set1 -= Set2
            RETURN          1                       # This is optional.
        
        The last RETURN statement is optional. If omitted, the last Set
        touched will be returned.
        
        For all operations, the Set ID indicates which Set will be
            modified by the operation. Using the above example, you can
            see that for the DIFFERENCE operation, the Set which is modified
            is Set 1.
        """
        dejavu.Unit.__init__(self)
        
        if kwargs.get('Operation', '') == 'FILTER':
            op = kwargs.get('Operand')
            if not isinstance(op, (str, unicode)):
                if not isinstance(op, logic.Expression):
                    # op can be a function
                    op = logic.Expression(op)
                kwargs['Operand'] = pickle.dumps(op)
        
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
    
    def __repr__(self):
        op = self.Operand
        if self.Operation == 'FILTER':
            op = pickle.loads(op)
        return ("dejavu.engines.UnitEngineRule(%s, %s, %s)"
                % (self.Operation, self.SetID, repr(op)))
    
    def on_memorize(self):
        eng = self.UnitEngine()
        if eng:
            eng.update_final_class()
    
    def on_forget(self):
        eng = self.UnitEngine()
        if eng:
            eng.update_final_class()
    
    def expr(self):
        """expr() -> If a FILTER rule, return the Expression, else None."""
        if self.Operation == 'FILTER':
            op = self.Operand
            return pickle.loads(op)
        return None


class UnitEngine(TemporaryUnit):
    """A factory for Unit Collections."""
    
    Owner = dejavu.UnitProperty()
    Name = dejavu.UnitProperty()
    Created = dejavu.UnitProperty(datetime.datetime)
    FinalClassName = dejavu.UnitProperty()
    
    def __init__(self, **kwargs):
        dejavu.Unit.__init__(self)
        self.Created = datetime.datetime.today()
        self.Owner = u''
        
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
    
    def on_forget(self):
        # Rules and Snapshots shouldn't persist past
        # the life of their Engines. Forget them.
        for rule in self.rules():
            rule.forget()
        for snap in self.snapshots():
            snap.forget()
    
    def update_final_class(self):
        results = {}
        last_set = 1
        for rule in self.rules():
            last_set = rule.SetID
            operation = rule.Operation
            if operation in ('CREATE', 'TRANSFORM'):
                results[last_set] = rule.Operand
            if operation == 'RETURN':
                break
        if last_set in results:
            self.FinalClassName = results[last_set]
    
    def final_class(self):
        return self.sandbox.arena.class_by_name(self.FinalClassName)
    
    def rules(self):
        """An ordered list of Rules for this Engine."""
        allrules = [x for x in self.UnitEngineRule()]
        allrules.sort(dejavu.sort(u'Sequence'))
        return allrules
    
    def add_rule(self, Operation, SetID=None, Operand=None):
        allrules = self.rules()
        if isinstance(Operation, UnitEngineRule):
            newRule = Operation
        else:
            if SetID is None:
                try:
                    SetID = allrules[-1].SetID
                except IndexError:
                    SetID = 1
            newRule = UnitEngineRule(Operation=Operation, SetID=SetID,
                                     Operand=Operand)
        
        try:
            nextSeq = allrules[-1].Sequence + 1
        except IndexError:
            nextSeq = 0
        newRule.Sequence = nextSeq
        
        newRule.EngineID = self.ID
        newRule.Expiration = self.Expiration
        self.sandbox.memorize(newRule)
    
    def snapshots(self):
        """Unit Collections obtained by executing the rules sometime in the past."""
        allSnap = self.sandbox.recall(UnitCollection, EngineID=self.ID)
        allSnap.sort(dejavu.sort(u'Timestamp'))
        return allSnap
    
    def take_snapshot(self, args={}):
        """Execute the rules and return a Unit Collection (or None)."""
        allrules = self.rules()
        snap = RuleProcessor(self.sandbox).process(allrules, args)
        if snap is not None:
            snap.EngineID = self.ID
            now = datetime.datetime.now()
            snap.Timestamp = now
            snap.decay(minutes=15)
            self.sandbox.memorize(snap)
        return snap
    
    def last_snapshot(self, args={}):
        allSnaps = self.snapshots()
        if len(allSnaps) == 0:
            aSnap = self.take_snapshot(args)
        else:
            aSnap = allSnaps[-1]
        return aSnap
    
    def immortalize(self):
        self.Expiration = None
        for rule in self.rules():
            rule.Expiration = None
    
    def __copy__(self):
        newUnit = dejavu.Unit.__copy__(self)
        newUnit.Name = "Copy of %s" % newUnit.Name
        newUnit.Created = datetime.datetime.now()
        return newUnit
    
    def clone(self, user, temporary=True):
        """Copy self and all Rules of self. Memorize automatically."""
        newUnit = self.__copy__()
        newUnit.Owner = user
        if temporary:
            newUnit.decay(minutes=15)
        else:
            newUnit.Expiration = None
        self.sandbox.memorize(newUnit)
        for rule in self.rules():
            newRule = rule.__copy__()
            newRule.EngineID = newUnit.ID
            newRule.Expiration = newUnit.Expiration
            self.sandbox.memorize(newRule)
        return newUnit
    
    def permit(self, user, write_access=True):
        if write_access:
            return self.Owner in (u'Public', user)
        else:
            return self.Owner in ('System', 'Public', user)

UnitEngine.one_to_many('ID', UnitEngineRule, 'EngineID')
UnitEngine.one_to_many('ID', UnitCollection, 'EngineID')


class RuleProcessor(object):
    """Processor for the Rules of a Unit Engine."""
    
    def __init__(self, sandbox):
        self.sandbox = sandbox
        self.arena = sandbox.arena
    
    def process(self, rules, args):
        """Execute the rules and return a Unit Collection (or None)."""
        self.sets = {}
        self.args = args
        final = None
        for rule in rules:
            operation = rule.Operation
            func = getattr(self, 'visit_' + operation)
            final = rule.SetID
            func(final, rule.Operand)
        if final is None:
            return None
        else:
            return self.sets[final]
    
    def visit_COPY(self, setID, operand):
        """Copy the set whose ID = operand into another set, whose ID = setID."""
        A = self.sets[setID]
        setID2 = int(operand)
        if setID2 in self.sets:
            # Overwrite the existing set.
            B = self.sets[setID2]
        else:
            # Create a new set.
            B = UnitCollection(Type=A.Type)
            self.sets[setID2] = B
        B.universal = A.universal
        A.acquire()
        B.acquire()
        try:
            B.Members = A.Members[:]
        finally:
            A.release()
            B.release()
    
    def visit_CREATE(self, setID, operand):
        """Create a universal set. Actual population may be deferred."""
        newset = UnitCollection(Type=operand)
        newset.universal = True
        self.sets[setID] = newset
    
    def visit_DIFFERENCE(self, setID, operand):
        A = self.sets[setID]
        
        setID2 = int(operand)
        self.realize_universal(setID2)
        B = self.sets[setID2]
        
        A.acquire()
        B.acquire()
        try:
            if B.universal:
                # B should be every Unit, which means the difference
                # will always be an empty set.
                A.Members = []
            else:
                # B is a subset of A.
                if A.universal:
                    cls = self.arena.class_by_name(A.Type)
                    mem = A.Members
                    for unit in self.sandbox.recall(cls):
                        id = unit.identity()
                        if id not in B.Members:
                            mem.append(id)
                else:
                    A.Members = [x for x in A.Members if x not in B.Members]
            A.universal = False
        finally:
            A.release()
            B.release()
    
    def visit_FILTER(self, setID, operand):
        expr = pickle.loads(operand)
        expr.bind_args(**self.args)
        
        A = self.sets[setID]
        A.acquire()
        try:
            cls = self.arena.class_by_name(A.Type)
            mem = A.Members
            if A.universal:
                A.universal = False
                for unit in self.sandbox.recall(cls, expr):
                    id = unit.identity()
                    if id not in mem:
                        mem.append(id)
            else:
                newset = []
                for id in mem:
                    filter = dict(zip(cls.identifiers, id))
                    unit = self.sandbox.unit(cls, **filter)
                    if unit and expr(unit):
                        newset.append(id)
                A.Members = newset
        finally:
            A.release()
    
    def visit_FUNCTION(self, setID, operand):
        func = self.arena.engine_functions[operand]
        
        A = self.sets[setID]
        A.acquire()
        try:
            # Notice we do not populate universals before passing to func.
            func(self.sandbox, A)
        finally:
            A.release()
    
    def visit_INTERSECTION(self, setID, operand):
        A = self.sets[setID]
        
        setID2 = int(operand)
        B = self.sets[setID2]
        
        A.acquire()
        B.acquire()
        try:
            if B.universal:
                # If A is universal, (A and B) = universal. Defer.
                # If A is not universal, (A and B) = A. Pass.
                pass
            else:
                if A.universal:
                    # B is a subset of A. (A and B) = B. Copy B to A.
                    A.Members = B.Members[:]
                    A.universal = False
                else:
                    A.Members = [x for x in A.Members if x in B.Members]
        finally:
            A.release()
            B.release()
    
    def visit_RETURN(self, setID, operand):
        self.realize_universal(setID)
    
    def realize_universal(self, setID):
        A = self.sets[setID]
        if A.universal:
            A.acquire()
            try:
                A.universal = False
                cls = self.arena.class_by_name(A.Type)
                mem = A.Members
                for unit in self.sandbox.recall(cls):
                    mem.append(unit.identity())
            finally:
                A.release()
    
    def visit_TRANSFORM(self, setID, operand):
        """visit_TRANSFORM(setID, operand=farClass name). Multiple hops OK."""
        A = self.sets[setID]
        start = self.arena.class_by_name(A.Type)
        end = self.arena.class_by_name(operand)
        nodes = self.arena.associations.shortest_path(start, end)
        if nodes is None:
            raise KeyError("No association found between '%s' and '%s'"
                           % (start, end))
        
        # Skip the first node, which should be A.Type
        nodes.pop(0)
        A.acquire()
        try:
            for eachType in nodes:
                # Add all associated Units to the collection A.
                ua = start._associations[eachType.__name__]
                cls = self.arena.class_by_name(A.Type)
                newset = []
                if A.universal:
                    for unit in self.sandbox.recall(cls):
                        farUnits = ua.__get__(unit)()
                        if not ua.to_many:
                            if farUnits is None:
                                farUnits = []
                            else:
                                farUnits = [farUnits]
                        for farUnit in farUnits:
                            farid = farUnit.identity()
                            if farid not in newset:
                                newset.append(farid)
                    A.universal = False
                else:
                    for id in A.Members:
                        filter = dict(zip(cls.identifiers, id))
                        unit = self.sandbox.unit(cls, **filter)
                        if unit:
                            farUnits = ua.__get__(unit)()
                            if not ua.to_many:
                                if farUnits is None:
                                    farUnits = []
                                else:
                                    farUnits = [farUnits]
                            for farUnit in farUnits:
                                farid = farUnit.identity()
                                if farid not in newset:
                                    newset.append(farid)
                A.Members = newset
                start = eachType
                A.Type = eachType.__name__
        finally:
            A.release()
    
    def visit_UNION(self, setID, operand):
        A = self.sets[setID]
        setID2 = int(operand)
        B = self.sets[setID2]
        
        A.acquire()
        B.acquire()
        try:
            if B.universal:
                # (A or B) = Universal set. Make A universal.
                A.universal = True
                A.Members = []
            else:
                if A.universal:
                    pass
                else:
                    amem = A.Members
                    for id in B.Members:
                        if id not in amem:
                            amem.append(id)
        finally:
            A.release()
            B.release()


def register_classes(arena):
    arena.register(UnitCollection)
    arena.register(UnitEngine)
    arena.register(UnitEngineRule)

