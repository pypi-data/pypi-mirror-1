"""Test fixture for Storage Managers."""

import datetime
import os
try:
    import pythoncom
except ImportError:
    pythoncom = None

try:
    set
except NameError:
    from sets import Set as set

import threading
import time
import unittest
import warnings

try:
    import decimal
except ImportError:
    decimal = None

try:
    import fixedpoint
except ImportError:
    fixedpoint = None

__all__ = ['Animal', 'Exhibit', 'Lecture', 'Vet', 'Visit', 'Zoo',
           # Don't export the ZooTests class--it will break e.g. test_dejavu.
           'arena', 'init', 'run', 'setup', 'teardown']

import dejavu
from dejavu import logic
from dejavu import Unit, UnitProperty, ToOne, ToMany
from dejavu.test import tools
from dejavu import engines


class EscapeProperty(UnitProperty):
    def __set__(self, unit, value):
        UnitProperty.__set__(self, unit, value)
        # Zoo is a ToOne association, so it will return a unit or None.
        z = unit.Zoo()
        if z:
            z.LastEscape = unit.LastEscape


class Animal(Unit):
    Species = UnitProperty(hints={'bytes': 100})
    ZooID = UnitProperty(int, index=True)
    Legs = UnitProperty(int, default=4)
    PreviousZoos = UnitProperty(list, hints={'bytes': 1000})
    LastEscape = EscapeProperty(datetime.datetime)
    Lifespan = UnitProperty(float, hints={'bytes': 4})
    MotherID = UnitProperty(int)

Animal.many_to_one('ID', Animal, 'MotherID')


class Zoo(Unit):
    Name = UnitProperty()
    Founded = UnitProperty(datetime.date)
    Opens = UnitProperty(datetime.time)
    LastEscape = UnitProperty(datetime.datetime)
    
    if fixedpoint:
        Admission = UnitProperty(fixedpoint.FixedPoint)
    else:
        Admission = UnitProperty(float)

Zoo.one_to_many('ID', Animal, 'ZooID')


class Vet(Unit):
    """A Veterinarian."""
    Name = UnitProperty()
    ZooID = UnitProperty(int, index=True)

Vet.many_to_one('ZooID', Zoo, 'ID')


class Visit(Unit):
    """Work done by a Veterinarian on an Animal."""
    VetID = UnitProperty(int, index=True)
    ZooID = UnitProperty(int, index=True)
    AnimalID = UnitProperty(int, index=True)
    Date = UnitProperty(datetime.date)

Vet.one_to_many('ID', Visit, 'VetID')
Animal.one_to_many('ID', Visit, 'AnimalID')


class Lecture(Visit):
    """A Visit by a Vet to train staff (rather than visit an Animal)."""
    AnimalID = None
    Topic = UnitProperty()


class Exhibit(Unit):
    # Make this a string to help test vs unicode.
    Name = UnitProperty(str)
    ZooID = UnitProperty(int)
    Animals = UnitProperty(list)
    PettingAllowed = UnitProperty(bool)
    if decimal:
        Acreage = UnitProperty(decimal.Decimal)
    else:
        Acreage = UnitProperty(float)
    
    # Remove the ID property (inherited from Unit) from the Exhibit class.
    ID = None
    sequencer = dejavu.UnitSequencerNull()
    identifiers = (ZooID, Name)

Zoo.one_to_many('ID', Exhibit, 'ZooID')


Jan_1_2001 = datetime.date(2001, 1, 1)
every13days = [Jan_1_2001 + datetime.timedelta(x * 13) for x in range(20)]
every17days = [Jan_1_2001 + datetime.timedelta(x * 17) for x in range(20)]
del x

class ZooTests(unittest.TestCase):
    
    def test_1_model(self):
        self.assertEqual(Zoo.Animal.__class__, dejavu.ToMany)
        self.assertEqual(Zoo.Animal.nearClass, Zoo)
        self.assertEqual(Zoo.Animal.nearKey, 'ID')
        self.assertEqual(Zoo.Animal.farClass, Animal)
        self.assertEqual(Zoo.Animal.farKey, 'ZooID')
        
        self.assertEqual(Animal.Zoo.__class__, dejavu.ToOne)
        self.assertEqual(Animal.Zoo.nearClass, Animal)
        self.assertEqual(Animal.Zoo.nearKey, 'ZooID')
        self.assertEqual(Animal.Zoo.farClass, Zoo)
        self.assertEqual(Animal.Zoo.farKey, 'ID')
    
    def test_2_populate(self):
        box = arena.new_sandbox()
        
        # Notice this also tests that: a Unit which is only
        # dirtied via __init__ is still saved.
        WAP = Zoo(Name = 'Wild Animal Park',
                  Founded = datetime.date(2000, 1, 1),
                  # 59 can give rounding errors with divmod, which
                  # AdapterFromADO needs to correct.
                  Opens = datetime.time(8, 15, 59),
                  LastEscape = datetime.datetime(2004, 7, 29, 5, 6, 7),
                  Admission = "4.95",
                  )
        box.memorize(WAP)
        # The object should get an ID automatically.
        self.assertNotEqual(WAP.ID, None)
        
        SDZ = Zoo(Name = 'San Diego Zoo',
                  # This early date should play havoc with a number
                  # of implementations.
                  Founded = datetime.date(1835, 9, 13),
                  Opens = datetime.time(9, 0, 0),
                  Admission = "0",
                  )
        box.memorize(SDZ)
        # The object should get an ID automatically.
        self.assertNotEqual(SDZ.ID, None)
        
        Biodome = Zoo(Name = u'Montr\xe9al Biod\xf4me',
                      Founded = datetime.date(1992, 6, 19),
                      Opens = datetime.time(9, 0, 0),
                      Admission = "11.75",
                      )
        box.memorize(Biodome)
        
        seaworld = Zoo(Name = 'Sea_World', Admission = "60")
        box.memorize(seaworld)
        
        # Animals
        leopard = Animal(Species='Leopard', Lifespan=73.5)
        self.assertEqual(leopard.PreviousZoos, None)
        box.memorize(leopard)
        leopard.add(WAP)
        leopard.LastEscape = datetime.datetime(2004, 12, 21, 8, 15, 0)
        
        lion = Animal(Species='Lion', ZooID=WAP.ID)
        box.memorize(lion)
        
        box.memorize(Animal(Species='Slug', Legs=1, Lifespan=.75))
        tiger = Animal(Species='Tiger')
        box.memorize(tiger)
        
        # Override Legs.default with itself just to make sure it works.
        box.memorize(Animal(Species='Bear', Legs=4))
        # Notice that ostrich.PreviousZoos is [], whereas leopard is None.
        box.memorize(Animal(Species='Ostrich', Legs=2, PreviousZoos=[],
                            Lifespan=103.2))
        box.memorize(Animal(Species='Centipede', Legs=100))
        
        emp = Animal(Species='Emperor Penguin', Legs=2)
        box.memorize(emp)
        adelie = Animal(Species='Adelie Penguin', Legs=2)
        box.memorize(adelie)
        
        seaworld.add(emp, adelie)
        
        millipede = Animal(Species='Millipede', Legs=1000000)
        millipede.PreviousZoos = [WAP.ID]
        box.memorize(millipede)
        
        SDZ.add(tiger, millipede)
        
        # Add a mother and child to test relationships
        bai_yun = Animal(Species='Ape', Legs=2)
        box.memorize(bai_yun)   # ID = 11
        hua_mei = Animal(Species='Ape', Legs=2, MotherID=bai_yun.ID)
        box.memorize(hua_mei)   # ID = 12
        
        # Exhibits
        pe = Exhibit(Name = 'The Penguin Encounter',
                     ZooID = seaworld.ID,
                     Animals = [emp.ID, adelie.ID],
                     PettingAllowed = True,
                     Acreage = "3.21",
                     )
        box.memorize(pe)
        
        tr = Exhibit(Name = 'Tiger River',
                     ZooID = SDZ.ID,
                     Animals = [tiger.ID],
                     PettingAllowed = False,
                     Acreage = "4",
                     )
        box.memorize(tr)
        
        # Vets
        cs = Vet(Name = 'Charles Schroeder', ZooID = SDZ.ID)
        box.memorize(cs)
        jm = Vet(Name = 'Jim McBain', ZooID = seaworld.ID)
        box.memorize(jm)
        
        # Visits
        for d in every13days:
            box.memorize(Visit(VetID=cs.ID, AnimalID=tiger.ID, Date=d))
        for d in every17days:
            box.memorize(Visit(VetID=jm.ID, AnimalID=emp.ID, Date=d))
        
        box.flush_all()
    
    def test_3_Properties(self):
        box = arena.new_sandbox()
        
        # Zoos
        WAP = box.unit(Zoo, Name='Wild Animal Park')
        self.assertNotEqual(WAP, None)
        self.assertEqual(WAP.Founded, datetime.date(2000, 1, 1))
        self.assertEqual(WAP.Opens, datetime.time(8, 15, 59))
        # This should have been updated when leopard.LastEscape was set.
        self.assertEqual(WAP.LastEscape,
                         datetime.datetime(2004, 12, 21, 8, 15, 0))
        self.assertEqual(str(WAP.Admission), "4.95")
        
        SDZ = box.unit(Zoo, Founded=datetime.date(1835, 9, 13))
        self.assertNotEqual(SDZ, None)
        self.assertEqual(SDZ.Founded, datetime.date(1835, 9, 13))
        self.assertEqual(SDZ.Opens, datetime.time(9, 0, 0))
        self.assertEqual(SDZ.LastEscape, None)
        self.assertEqual(float(SDZ.Admission), 0)
        
        # Try a magic Sandbox recaller method
        Biodome = box.Zoo(Name = u'Montr\xe9al Biod\xf4me')
        self.assertNotEqual(Biodome, None)
        self.assertEqual(Biodome.Name, u'Montr\xe9al Biod\xf4me')
        self.assertEqual(Biodome.Founded, datetime.date(1992, 6, 19))
        self.assertEqual(Biodome.Opens, datetime.time(9, 0, 0))
        self.assertEqual(Biodome.LastEscape, None)
        self.assertEqual(float(Biodome.Admission), 11.75)
        
        if fixedpoint:
            seaworld = box.unit(Zoo, Admission = fixedpoint.FixedPoint(60))
        else:
            seaworld = box.unit(Zoo, Admission = float(60))
        self.assertNotEqual(seaworld, None)
        self.assertEqual(seaworld.Name, u'Sea_World')
        
        # Animals
        leopard = box.unit(Animal, Species='Leopard')
        self.assertEqual(leopard.Species, 'Leopard')
        self.assertEqual(leopard.Legs, 4)
        self.assertEqual(leopard.Lifespan, 73.5)
        self.assertEqual(leopard.ZooID, WAP.ID)
        self.assertEqual(leopard.PreviousZoos, None)
        self.assertEqual(leopard.LastEscape,
                         datetime.datetime(2004, 12, 21, 8, 15, 0))
        
        ostrich = box.unit(Animal, Species='Ostrich')
        self.assertEqual(ostrich.Species, 'Ostrich')
        self.assertEqual(ostrich.Legs, 2)
        self.assertEqual(ostrich.ZooID, None)
        self.assertEqual(ostrich.PreviousZoos, [])
        self.assertEqual(ostrich.LastEscape, None)
        
        millipede = box.unit(Animal, Legs=1000000)
        self.assertEqual(millipede.Species, 'Millipede')
        self.assertEqual(millipede.Legs, 1000000)
        self.assertEqual(millipede.ZooID, SDZ.ID)
        self.assertEqual(millipede.PreviousZoos, [WAP.ID])
        self.assertEqual(millipede.LastEscape, None)
        
        # Exhibits
        exes = box.recall(Exhibit)
        self.assertEqual(len(exes), 2)
        if exes[0].Name == 'The Penguin Encounter':
            pe = exes[0]
            tr = exes[1]
        else:
            pe = exes[1]
            tr = exes[0]
        self.assertEqual(pe.ZooID, seaworld.ID)
        self.assertEqual(len(pe.Animals), 2)
        self.assertEqual(float(pe.Acreage), 3.21)
        self.assertEqual(pe.PettingAllowed, True)
        
        self.assertEqual(tr.ZooID, SDZ.ID)
        self.assertEqual(len(tr.Animals), 1)
        self.assertEqual(float(tr.Acreage), 4)
        self.assertEqual(tr.PettingAllowed, False)
        
        box.flush_all()
    
    def test_Expressions(self):
        box = arena.new_sandbox()
        
        def matches(lam, cls=Animal):
            # We flush_all to ensure a DB hit each time.
            box.flush_all()
            return len(box.recall(cls, logic.Expression(lam)))
        
        zoos = box.recall(Zoo)
        self.assertEqual(zoos[0].dirty(), False)
        self.assertEqual(len(zoos), 4)
        self.assertEqual(matches(lambda x: True), 12)
        self.assertEqual(matches(lambda x: x.Legs == 4), 4)
        self.assertEqual(matches(lambda x: x.Legs == 2), 5)
        self.assertEqual(matches(lambda x: x.Legs >= 2 and x.Legs < 20), 9)
        self.assertEqual(matches(lambda x: x.Legs > 10), 2)
        self.assertEqual(matches(lambda x: x.Lifespan > 70), 2)
        self.assertEqual(matches(lambda x: x.Species.startswith('L')), 2)
        self.assertEqual(matches(lambda x: x.Species.endswith('pede')), 2)
        self.assertEqual(matches(lambda x: x.LastEscape != None), 1)
        self.assertEqual(matches(lambda x: None == x.LastEscape), 11)
        
        # In operator (containedby)
        self.assertEqual(matches(lambda x: 'pede' in x.Species), 2)
        self.assertEqual(matches(lambda x: x.Species in ('Lion', 'Tiger', 'Bear')), 3)
        
        # Try In with cell references
        class thing(object): pass
        pet, pet2 = thing(), thing()
        pet.Name, pet2.Name = 'Slug', 'Ostrich'
        self.assertEqual(matches(lambda x: x.Species in (pet.Name, pet2.Name)), 2)
        
        # logic and other functions
        self.assertEqual(matches(lambda x: dejavu.ieq(x.Species, 'slug')), 1)
        self.assertEqual(matches(lambda x: dejavu.icontains(x.Species, 'PEDE')), 2)
        self.assertEqual(matches(lambda x: dejavu.icontains(('Lion', 'Banana'), x.Species)), 1)
        f = lambda x: dejavu.icontainedby(x.Species, ('Lion', 'Bear', 'Leopard'))
        self.assertEqual(matches(f), 3)
        name = 'Lion'
        self.assertEqual(matches(lambda x: len(x.Species) == len(name)), 3)
        
        # This broke sometime in 2004. Rev 32 seems to have fixed it.
        self.assertEqual(matches(lambda x: 'i' in x.Species), 7)
        
        # Test now(), today(), year()
        self.assertEqual(matches(lambda x: x.Founded != None
                                 and x.Founded < dejavu.today(), Zoo), 3)
        self.assertEqual(matches(lambda x: x.LastEscape == dejavu.now()), 0)
        self.assertEqual(matches(lambda x: dejavu.year(x.LastEscape) == 2004), 1)
        
        # Test AND, OR with cannot_represent.
        # Notice that we reference a method ('count') which no
        # known SM handles, so it will default back to Expr.eval().
        self.assertEqual(matches(lambda x: 'p' in x.Species
                                 and x.Species.count('e') > 1), 3)
        
        # This broke in MSAccess (storeado) in April 2005, due to a bug in
        # db.SQLDecompiler.visit_CALL_FUNCTION (append TOS, not replace!).
        box.flush_all()
        e = logic.Expression(lambda x, **kw: x.LastEscape != None
                             and x.LastEscape >= datetime.datetime(kw['Year'], 12, 1)
                             and x.LastEscape < datetime.datetime(kw['Year'], 12, 31)
                             )
        e.bind_args(Year=2004)
        units = box.recall(Animal, e)
        self.assertEqual(len(units), 1)
        
        # Test wildcards in LIKE. This fails with SQLite <= 3.0.8,
        # so make sure it's always at the end of this method so
        # it doesn't preclude running the other tests.
        box.flush_all()
        units = box.recall(Zoo, logic.Expression(lambda x: "_" in x.Name))
        self.assertEqual(len(units), 1)
    
    def test_Aggregates(self):
        box = arena.new_sandbox()
        
        # views
        legs = [x[0] for x in box.view(Animal, ['Legs'])]
        legs.sort()
        self.assertEqual(legs, [1, 2, 2, 2, 2, 2, 4, 4, 4, 4, 100, 1000000])
        
        expected = {'Leopard': 73.5,
                    'Slug': .75,
                    'Tiger': None,
                    'Lion': None,
                    'Bear': None,
                    'Ostrich': 103.2,
                    'Centipede': None,
                    'Emperor Penguin': None,
                    'Adelie Penguin': None,
                    'Millipede': None,
                    'Ape': None,
                    }
        for species, lifespan in box.view(Animal, ['Species', 'Lifespan']):
            if expected[species] is None:
                self.assertEqual(lifespan, None)
            else:
                self.assertAlmostEqual(expected[species], lifespan, places=5)
        
        # distinct
        legs = box.distinct(Animal, ['Legs'])
        legs.sort()
        self.assertEqual(legs, [1, 2, 4, 100, 1000000])
        
        # This may raise a warning on some DB's.
        f = logic.Expression(lambda x: x.Species == 'Lion')
        escapees = box.distinct(Animal, ['Legs'], f)
        self.assertEqual(escapees, [4])
    
    def test_Multirecall(self):
        # Multirecall isn't designed with caching proxies in mind.
        # If we use any, sweep out all their units before proceeding.
        for store in arena.stores.itervalues():
            if hasattr(store, "sweep_all"):
                store.sweep_all()
        
        box = arena.new_sandbox()
        
        f = logic.Expression(lambda z, a: z.Name == 'San Diego Zoo')
        zooed_animals = box.recall(Zoo & Animal, f)
        self.assertEqual(len(zooed_animals), 2)
        
        SDZ = box.unit(Zoo, Name='San Diego Zoo')
        aid = 0
        for z, a in zooed_animals:
            self.assertEqual(id(z), id(SDZ))
            self.assertNotEqual(id(a), aid)
            aid = id(a)
        
        # Assert that multirecalls with no matching related units returns
        # no matches for the initial class, since all joins are INNER.
        # We're also going to test that you can combine a one-arg expr
        # with a two-arg expr.
        sdexpr = logic.filter(Name='San Diego Zoo')
        leo = logic.Expression(lambda z, a: a.Species == 'Leopard')
        zooed_animals = box.recall(Zoo & Animal, sdexpr + leo)
        self.assertEqual(len(zooed_animals), 0)
        
        # Now try the same expr with INNER, LEFT, and RIGHT JOINs.
        zooed_animals = box.recall(Zoo & Animal)
        self.assertEqual(len(zooed_animals), 6)
        self.assertEqual(set([(z.Name, a.Species) for z, a in zooed_animals]),
                         set([("Wild Animal Park", "Leopard"),
                              ("Wild Animal Park", "Lion"),
                              ("San Diego Zoo", "Tiger"),
                              ("San Diego Zoo", "Millipede"),
                              ("Sea_World", "Emperor Penguin"),
                              ("Sea_World", "Adelie Penguin")]))
        
        zooed_animals = box.recall(Zoo >> Animal)
        self.assertEqual(len(zooed_animals), 12)
        self.assertEqual(set([(z.Name, a.Species) for z, a in zooed_animals]),
                         set([("Wild Animal Park", "Leopard"),
                              ("Wild Animal Park", "Lion"),
                              ("San Diego Zoo", "Tiger"),
                              ("San Diego Zoo", "Millipede"),
                              ("Sea_World", "Emperor Penguin"),
                              ("Sea_World", "Adelie Penguin"),
                              (None, "Slug"),
                              (None, "Bear"),
                              (None, "Ostrich"),
                              (None, "Centipede"),
                              (None, "Ape"),
                              (None, "Ape"),
                              ]))
        
        zooed_animals = box.recall(Zoo << Animal)
        self.assertEqual(len(zooed_animals), 7)
        self.assertEqual(set([(z.Name, a.Species) for z, a in zooed_animals]),
                         set([("Wild Animal Park", "Leopard"),
                              ("Wild Animal Park", "Lion"),
                              ("San Diego Zoo", "Tiger"),
                              ("San Diego Zoo", "Millipede"),
                              ("Sea_World", "Emperor Penguin"),
                              ("Sea_World", "Adelie Penguin"),
                              (u'Montr\xe9al Biod\xf4me', None),
                              ]))
        
        # Try a multiple-arg expression
        f = logic.Expression(lambda a, z: a.Legs >= 4 and z.Admission < 10)
        animal_zoos = box.recall(Animal & Zoo, f)
        self.assertEqual(len(animal_zoos), 4)
        names = [a.Species for a, z in animal_zoos]
        names.sort()
        self.assertEqual(names, ['Leopard', 'Lion', 'Millipede', 'Tiger'])
        
        # Let's try three joined classes just for the sadistic fun of it.
        tree = (Animal >> Zoo) >> Vet
        f = logic.Expression(lambda a, z, v: z.Name == 'Sea_World')
        self.assertEqual(len(box.recall(tree, f)), 2)
        
        # MSAccess can't handle an INNER JOIN nested in an OUTER JOIN.
        # Test that this fails for MSAccess, but works for other SM's.
        trees = []
        def make_tree():
            trees.append( (Animal & Zoo) >> Vet )
        warnings.filterwarnings("ignore", category=dejavu.StorageWarning)
        try:
            make_tree()
        finally:
            warnings.filters.pop(0)
        
        azv = []
        def set_azv():
            f = logic.Expression(lambda a, z, v: z.Name == 'Sea_World')
            azv.append(box.recall(trees[0], f))
        
        smname = arena.stores['testSM'].__class__.__name__
        if smname in ("StorageManagerADO_MSAccess",):
            self.assertRaises(pythoncom.com_error, set_azv)
        else:
            set_azv()
            self.assertEqual(len(azv[0]), 2)
        
        # Try mentioning the same class twice.
        tree = (Animal << Animal)
        f = logic.Expression(lambda anim, mother: mother.ID != None)
        animals = [mother.ID for anim, mother in box.recall(tree, f)]
        self.assertEqual(animals, [11])
    
    def test_Editing(self):
        # Edit
        box = arena.new_sandbox()
        SDZ = box.unit(Zoo, Name='San Diego Zoo')
        SDZ.Name = 'The San Diego Zoo'
        SDZ.Founded = datetime.date(1900, 1, 1)
        SDZ.Opens = datetime.time(7, 30, 0)
        SDZ.Admission = "35.00"
        box.flush_all()
        
        # Test edits
        box = arena.new_sandbox()
        SDZ = box.unit(Zoo, Name='The San Diego Zoo')
        self.assertEqual(SDZ.Name, 'The San Diego Zoo')
        self.assertEqual(SDZ.Founded, datetime.date(1900, 1, 1))
        self.assertEqual(SDZ.Opens, datetime.time(7, 30, 0))
        if fixedpoint:
            self.assertEqual(SDZ.Admission, fixedpoint.FixedPoint(35, 2))
        else:
            self.assertEqual(SDZ.Admission, 35.0)
        box.flush_all()
        
        # Change it back
        box = arena.new_sandbox()
        SDZ = box.unit(Zoo, Name='The San Diego Zoo')
        SDZ.Name = 'San Diego Zoo'
        SDZ.Founded = datetime.date(1835, 9, 13)
        SDZ.Opens = datetime.time(9, 0, 0)
        SDZ.Admission = "0"
        box.flush_all()
        
        # Test re-edits
        box = arena.new_sandbox()
        SDZ = box.unit(Zoo, Name='San Diego Zoo')
        self.assertEqual(SDZ.Name, 'San Diego Zoo')
        self.assertEqual(SDZ.Founded, datetime.date(1835, 9, 13))
        self.assertEqual(SDZ.Opens, datetime.time(9, 0, 0))
        if fixedpoint:
            self.assertEqual(SDZ.Admission, fixedpoint.FixedPoint(0, 2))
        else:
            self.assertEqual(SDZ.Admission, 0.0)
    
    def test_Multithreading(self):
        f = logic.Expression(lambda x: x.Legs == 4)
        def thread_recall():
            # Notice we only do reads in this thread, not writes, since
            # the order of thread execution can not be guaranteed.
            box = arena.new_sandbox()
            quadrupeds = box.recall(Animal, f)
            self.assertEqual(len(quadrupeds), 4)
        
        ts = []
        # PostgreSQL, for example, has a default max_connections of 100.
        for x in range(99):
            t = threading.Thread(target=thread_recall)
            t.start()
            ts.append(t)
        for t in ts:
            t.join()
    
    def test_Iteration(self):
        box = arena.new_sandbox()
        
        # Test box.unit inside of xrecall
        for visit in box.xrecall(Visit, logic.filter(VetID=1)):
            firstvisit = box.unit(Visit, VetID=1, Date=Jan_1_2001)
            self.assertEqual(firstvisit.VetID, 1)
            self.assertEqual(visit.VetID, 1)
        
        # Test recall inside of xrecall
        for visit in box.xrecall(Visit, logic.filter(VetID=1)):
            f = logic.Expression(lambda x: x.VetID == 1 and x.ID != visit.ID)
            othervisits = box.recall(Visit, f)
            self.assertEqual(len(othervisits), len(every13days) - 1)
        
        # Test far associations inside of xrecall
        for visit in box.xrecall(Visit, logic.filter(VetID=1)):
            # visit.Vet is a ToOne association, so will return a unit or None.
            vet = visit.Vet()
            self.assertEqual(vet.ID, 1)
    
    def test_Engines(self):
        box = arena.new_sandbox()
        
        quadrupeds = box.recall(Animal, logic.filter(Legs=4))
        self.assertEqual(len(quadrupeds), 4)
        
        eng = engines.UnitEngine()
        box.memorize(eng)
        eng.add_rule('CREATE', 1, "Animal")
        eng.add_rule('FILTER', 1, logic.filter(Legs=4))
        self.assertEqual(eng.FinalClassName, "Animal")
        
        qcoll = eng.take_snapshot()
        self.assertEqual(len(qcoll), 4)
        self.assertEqual(qcoll.EngineID, eng.ID)
        
        eng.add_rule('TRANSFORM', 1, "Zoo")
        self.assertEqual(eng.FinalClassName, "Zoo")
        
        # Sleep for a second so the Timestamps are different.
        time.sleep(1)
        qcoll = eng.take_snapshot()
        self.assertEqual(len(qcoll), 2)
        zoos = qcoll.units()
        zoos.sort(dejavu.sort('Name'))
        
        SDZ = box.unit(Zoo, Name='San Diego Zoo')
        WAP = box.unit(Zoo, Name='Wild Animal Park')
        self.assertEqual(zoos, [SDZ, WAP])
        
        # Flush and start over
        box.flush_all()
        box = arena.new_sandbox()
        
        # Use the Sandbox magic recaller method
        eng = box.UnitEngine(1)
        self.assertEqual(len(eng.rules()), 3)
        snaps = eng.snapshots()
        self.assertEqual(len(snaps), 2)
        
        self.assertEqual(snaps[0].Type, "Animal")
        self.assertEqual(len(snaps[0]), 4)
        
        self.assertEqual(snaps[1].Type, "Zoo")
        self.assertEqual(len(snaps[1]), 2)
        self.assertEqual(eng.last_snapshot(), snaps[1])
        
        # Remove the last TRANSFORM rule to see if finalclass reverts.
        self.assertEqual(eng.FinalClassName, "Zoo")
        eng.rules()[-1].forget()
        self.assertEqual(eng.FinalClassName, "Animal")
    
    def test_Subclassing(self):
        box = arena.new_sandbox()
        box.memorize(Visit(VetID=21, ZooID=1, AnimalID=1))
        box.memorize(Visit(VetID=21, ZooID=1, AnimalID=2))
        box.memorize(Visit(VetID=32, ZooID=1, AnimalID=3))
        box.memorize(Lecture(VetID=21, ZooID=1, Topic='Cage Cleaning'))
        box.memorize(Lecture(VetID=21, ZooID=1, Topic='Ape Mating Habits'))
        box.memorize(Lecture(VetID=32, ZooID=3, Topic='Your Tiger and Steroids'))
        
        visits = box.recall(Visit, logic.filter(ZooID=1))
        self.assertEqual(len(visits), 5)
        
        box.flush_all()
        
        box = arena.new_sandbox()
        visits = box.recall(Visit, logic.filter(VetID=21))
        self.assertEqual(len(visits), 4)
        cc = [x for x in visits
              if getattr(x, "Topic", None) == "Cage Cleaning"]
        self.assertEqual(len(cc), 1)
        
        # Checking for non-existent attributes in/from subclasses
        # isn't supported yet.
##        f = logic.filter(AnimalID=2)
##        self.assertEqual(len(box.recall(Visit, f)), 1)
##        self.assertEqual(len(box.recall(Lecture, f)), 0)
    
##    def test_Transactions(self):
##        box = arena.new_sandbox()
##        box.mark("rollback point name")
##        lion = box.unit(Animal, Species=Lion)
##        lion.LastEscape = datetime.datetime(2005, 12, 25, 8, 14)
##        box.commit_since("rollback point name")
    
    def testzzzz_Schema_Upgrade(self):
        # Must run last.
        zs = ZooSchema(arena)
        
        # In this first upgrade, we simulate the case where the code was
        # upgraded, and the database schema upgrade performed afterward.
        # The Schema.latest property is set, and upgrade() is called with
        # no argument (which should upgrade us to "latest").
        Animal.set_property("ExhibitID")
        zs.latest = 2
        zs.upgrade()
        
        # In this example, we simulate the developer who wants to put
        # model changes inline with database changes (see upgrade_to_3).
        # We do not set latest, but instead supply an arg to upgrade().
        zs.upgrade(3)
        
        # Test that Animals have a new "Family" property, and an ExhibitID.
        box = arena.new_sandbox()
        emp = box.unit(Animal, Family='Emperor Penguin')
        self.assertEqual(emp.ExhibitID, 'The Penguin Encounter')


arena = dejavu.Arena()

def _djvlog(message, flag):
    """Dejavu logger (writes to error.log)."""
    if flag & arena.logflags:
        s = "%s %s" % (datetime.datetime.now().isoformat(),
                       message.encode('utf8'))
        fname = os.path.join(os.path.dirname(__file__), "djvtest.log")
        f = open(fname, 'ab')
        f.write(s + '\n')
        f.close()

def init():
    global arena
    arena = dejavu.Arena()
    arena.log = _djvlog
    arena.logflags = dejavu.LOGSQL


class ZooSchema(dejavu.Schema):
    
    # We set "latest" to 1 so we can test upgrading.
    latest = 1
    
    def upgrade_to_2(self):
        self.arena.add_property(Animal, "ExhibitID")
        box = self.arena.new_sandbox()
        for exhibit in box.recall(Exhibit):
            for animalID in exhibit.Animals:
                # Use the Sandbox magic recaller method.
                a = box.Animal(animalID)
                if a:
                    # Exhibits are identified by ZooID and Name
                    a.ZooID = exhibit.ZooID
                    a.ExhibitID = exhibit.Name
        box.flush_all()
    
    def upgrade_to_3(self):
        Animal.remove_property("Species")
        Animal.set_property("Family")
        
        # Note that we drop this column in a separate step from step 2.
        # If we had mixed model properties and SM properties in step 2,
        # we could have done this all in one step. But this is a better
        # demonstration of the possibilities. ;)
        Exhibit.remove_property("Animals")
        self.arena.drop_property(Exhibit, "Animals")
        
        self.arena.rename_property(Animal, "Species", "Family")


def setup(SM_class, opts):
    """setup(SM_class, opts). Set up storage for Zoo classes."""
    global arena
    arena.add_store('testSM', SM_class, opts)
    v = getattr(arena.stores['testSM'], "version", None)
    if v:
        print v()
    arena.stores['testSM'].create_database()
    
    arena.register_all(globals())
    engines.register_classes(arena)
    
    zs = ZooSchema(arena)
    zs.upgrade()
    zs.assert_storage()


def teardown():
    """Tear down storage for Zoo classes."""
    global arena
    arena.shutdown()
    for store in arena.stores.values():
        try:
            store.drop_database()
        except (AttributeError, NotImplementedError):
            pass
    arena.stores = {}
    arena.defaultStore = None

def run(SM_class, opts):
    """Run the zoo fixture."""
    try:
        setup(SM_class, opts)
        suite = unittest.TestLoader().loadTestsFromTestCase(ZooTests)
        startTime = datetime.datetime.now()
        tools.djvTestRunner.run(suite)
        print "Ran zoo suite in:", (datetime.datetime.now() - startTime)
    finally:
        teardown()

