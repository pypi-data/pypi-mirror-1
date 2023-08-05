"""Test fixture for Storage Managers."""

import datetime
import os
thisdir = os.path.dirname(__file__)
logname = os.path.join(thisdir, "djvtest.log")


try:
    import pythoncom
except ImportError:
    pythoncom = None

try:
    set
except NameError:
    from sets import Set as set

import sys
import threading
import time
import traceback
import unittest
import warnings

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

__all__ = ['Animal', 'Exhibit', 'Lecture', 'Vet', 'Visit', 'Zoo',
           # Don't export the ZooTests class--it will break e.g. test_dejavu.
           'arena', 'init', 'run', 'setup', 'teardown']

import dejavu
from dejavu import errors, logic, storage
from dejavu import Unit, UnitProperty, ToOne, ToMany, UnitSequencerInteger, UnitAssociation
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
    PreviousZoos = UnitProperty(list, hints={'bytes': 8000})
    LastEscape = EscapeProperty(datetime.datetime)
    Lifespan = UnitProperty(float, hints={'precision': 4})
    Age = UnitProperty(float, hints={'precision': 4}, default=1)
    MotherID = UnitProperty(int)
    PreferredFoodID = UnitProperty(int)
    AlternateFoodID = UnitProperty(int)

Animal.many_to_one('ID', Animal, 'MotherID')


class Zoo(Unit):
    Name = UnitProperty()
    Founded = UnitProperty(datetime.date)
    Opens = UnitProperty(datetime.time)
    LastEscape = UnitProperty(datetime.datetime)
    
    if fixedpoint:
        # Explicitly set precision and scale so test_storemsaccess
        # can test CURRENCY type
        Admission = UnitProperty(fixedpoint.FixedPoint,
                                 hints={'precision': 4, 'scale': 2})
    else:
        Admission = UnitProperty(float)

Zoo.one_to_many('ID', Animal, 'ZooID')

class AlternateFoodAssociation(UnitAssociation):
    to_many = False
    register = False
    
    def related(self, unit, expr=None):
        food = unit.sandbox.unit(Food, ID=unit.AlternateFoodID)
        return food

class Food(Unit):
    """A food item."""
    Name = UnitProperty()
    NutritionValue = UnitProperty(int)

Food.one_to_many('ID', Animal, 'PreferredFoodID')

descriptor = AlternateFoodAssociation('AlternateFoodID', Food, 'ID')
descriptor.nearClass = Animal
Animal._associations['Alternate Food'] = descriptor
Animal.AlternateFood = descriptor
del descriptor

class Vet(Unit):
    """A Veterinarian."""
    Name = UnitProperty()
    ZooID = UnitProperty(int, index=True)
    City = UnitProperty()
    sequencer = UnitSequencerInteger(initial=200)

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
    Creators = UnitProperty(tuple)
    
    if decimal:
        Acreage = UnitProperty(decimal.Decimal)
    else:
        Acreage = UnitProperty(float)
    
    # Remove the ID property (inherited from Unit) from the Exhibit class.
    ID = None
    sequencer = dejavu.UnitSequencer()
    identifiers = ("ZooID", Name)

Zoo.one_to_many('ID', Exhibit, 'ZooID')


class NothingToDoWithZoos(Unit):
    ALong = UnitProperty(long, hints={'precision': 1})
    AFloat = UnitProperty(float, hints={'precision': 1})
    if decimal:
        ADecimal = UnitProperty(decimal.Decimal,
                                hints={'precision': 1, 'scale': 1})
    if fixedpoint:
        AFixed = UnitProperty(fixedpoint.FixedPoint,
                              hints={'precision': 1, 'scale': 1})


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
        try:
            
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
    ##        
    ##        mostly_empty = Zoo(Name = 'The Mostly Empty Zoo' + (" " * 255))
    ##        box.memorize(mostly_empty)
            
            # Animals
            leopard = Animal(Species='Leopard', Lifespan=73.5)
            self.assertEqual(leopard.PreviousZoos, None)
            box.memorize(leopard)
            self.assertEqual(leopard.ID, 1)
            
            leopard.add(WAP)
            leopard.LastEscape = datetime.datetime(2004, 12, 21, 8, 15, 0, 999907)
            
            lion = Animal(Species='Lion', ZooID=WAP.ID)
            box.memorize(lion)
            
            box.memorize(Animal(Species='Slug', Legs=1, Lifespan=.75,
                                # Test our 8000-byte limit
                                PreviousZoos=["f" * (8000 - 14)]))
            
            tiger = Animal(Species='Tiger', PreviousZoos=['animal\\universe'])
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
            millipede.PreviousZoos = [WAP.Name]
            box.memorize(millipede)
            
            SDZ.add(tiger, millipede)
            
            # Add a mother and child to test relationships
            bai_yun = Animal(Species='Ape', Legs=2)
            box.memorize(bai_yun)   # ID = 11
            self.assertEqual(bai_yun.ID, 11)
            hua_mei = Animal(Species='Ape', Legs=2, MotherID=bai_yun.ID)
            box.memorize(hua_mei)   # ID = 12
            self.assertEqual(hua_mei.ID, 12)
            
            # Exhibits
            pe = Exhibit(Name = 'The Penguin Encounter',
                         ZooID = seaworld.ID,
                         Animals = [emp.ID, adelie.ID],
                         PettingAllowed = True,
                         Acreage = "3.1",
                         # See ticket #45
                         Creators = (u'Richard F\xfcrst', u'Sonja Martin'),
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
            self.assertEqual(cs.ID, Vet.sequencer.initial)
            
            jm = Vet(Name = 'Jim McBain', ZooID = seaworld.ID)
            box.memorize(jm)
            
            # Visits
            for d in every13days:
                box.memorize(Visit(VetID=cs.ID, AnimalID=tiger.ID, Date=d))
            for d in every17days:
                box.memorize(Visit(VetID=jm.ID, AnimalID=emp.ID, Date=d))

            # Foods
            dead_fish = Food(Name="Dead Fish", Nutrition=5)
            live_fish = Food(Name="Live Fish", Nutrition=10)
            bunnies = Food(Name="Live Bunny Wabbit", Nutrition=10)
            steak = Food(Name="T-Bone", Nutrition=7)
            for food in [dead_fish, live_fish, bunnies, steak]:
                box.memorize(food)
            
            # Foods --> add preferred foods
            lion.add(steak)
            tiger.add(bunnies)
            emp.add(live_fish)
            adelie.add(live_fish)
            
            # Foods --> add alternate foods
            lion.AlternateFoodID = bunnies.ID
            tiger.AlternateFoodID = steak.ID
            emp.AlternateFoodID = dead_fish.ID
            adelie.AlternateFoodID = dead_fish.ID
            
        finally:
            box.flush_all()
    
    def test_3_Properties(self):
        box = arena.new_sandbox()
        try:
            # Zoos
            WAP = box.unit(Zoo, Name='Wild Animal Park')
            self.assertNotEqual(WAP, None)
            self.assertEqual(WAP.Founded, datetime.date(2000, 1, 1))
            self.assertEqual(WAP.Opens, datetime.time(8, 15, 59))
            # This should have been updated when leopard.LastEscape was set.
    ##        self.assertEqual(WAP.LastEscape,
    ##                         datetime.datetime(2004, 12, 21, 8, 15, 0, 999907))
            self.assertEqual(WAP.Admission, Zoo.Admission.coerce(WAP, "4.95"))
            
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
    ##        self.assertEqual(leopard.LastEscape,
    ##                         datetime.datetime(2004, 12, 21, 8, 15, 0, 999907))
            
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
            self.assertEqual(millipede.PreviousZoos, [WAP.Name])
            self.assertEqual(millipede.LastEscape, None)
            
            # Test that strings in a list get decoded correctly.
            # See http://projects.amor.org/dejavu/ticket/50
            tiger = box.unit(Animal, Species='Tiger')
            self.assertEqual(tiger.PreviousZoos, ["animal\\universe"])
            
            # Test our 8000-byte limit.
            # len(pickle.dumps(["f" * (8000 - 14)]) == 8000
            slug = box.unit(Animal, Species='Slug')
            self.assertEqual(len(slug.PreviousZoos[0]), 8000 - 14)
            
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
            self.assertEqual(float(pe.Acreage), 3.1)
            self.assertEqual(pe.PettingAllowed, True)
            self.assertEqual(pe.Creators, (u'Richard F\xfcrst', u'Sonja Martin'))
            
            self.assertEqual(tr.ZooID, SDZ.ID)
            self.assertEqual(len(tr.Animals), 1)
            self.assertEqual(float(tr.Acreage), 4)
            self.assertEqual(tr.PettingAllowed, False)
            
        finally:
            box.flush_all()
    
    def test_4_Expressions(self):
        box = arena.new_sandbox()
        try:
            def matches(lam, cls=Animal):
                # We flush_all to ensure a DB hit each time.
                box.flush_all()
                return len(box.recall(cls, (lam)))
            
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
            self.assertEqual(matches(lambda x: x.LastEscape is not None), 1)
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
            
            # Test now(), today(), year(), month(), day()
            self.assertEqual(matches(lambda x: x.Founded != None
                                     and x.Founded < dejavu.today(), Zoo), 3)
            self.assertEqual(matches(lambda x: x.LastEscape == dejavu.now()), 0)
            self.assertEqual(matches(lambda x: dejavu.year(x.LastEscape) == 2004), 1)
            self.assertEqual(matches(lambda x: dejavu.month(x.LastEscape) == 12), 1)
            self.assertEqual(matches(lambda x: dejavu.day(x.LastEscape) == 21), 1)

            
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
            units = box.recall(Zoo, lambda x: "_" in x.Name)
            self.assertEqual(len(units), 1)
        finally:
            box.flush_all()
    
    def test_5_Aggregates(self):
        box = arena.new_sandbox()
        try:
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
            
            expected = [u'Montr\xe9al Biod\xf4me', 'Wild Animal Park']
            e = (lambda x: x.Founded != None
                 and x.Founded <= dejavu.today()
                 and x.Founded >= datetime.date(1990, 1, 1))
            values =  [val[0] for val in box.view(Zoo, ['Name'], e)]
            for name in expected:
                self.assert_(name in values)
            
            # distinct
            legs = box.distinct(Animal, ['Legs'])
            legs.sort()
            self.assertEqual(legs, [1, 2, 4, 100, 1000000])
            
            # This may raise a warning on some DB's.
            f = (lambda x: x.Species == 'Lion')
            escapees = box.distinct(Animal, ['Legs'], f)
            self.assertEqual(escapees, [4])
            
            # range should return a sorted list
            legs = box.range(Animal, 'Legs', lambda x: x.Legs <= 100)
            self.assertEqual(legs, range(1, 101))
            topics = box.range(Exhibit, 'Name')
            self.assertEqual(topics, ['The Penguin Encounter', 'Tiger River'])
            vets = box.range(Vet, 'Name')
            self.assertEqual(vets, ['Charles Schroeder', 'Jim McBain'])
        finally:
            box.flush_all()
    
    def test_6_Editing(self):
        # Edit
        box = arena.new_sandbox()
        try:
            SDZ = box.unit(Zoo, Name='San Diego Zoo')
            SDZ.Name = 'The San Diego Zoo'
            SDZ.Founded = datetime.date(1900, 1, 1)
            SDZ.Opens = datetime.time(7, 30, 0)
            SDZ.Admission = "35.00"
        finally:
            box.flush_all()
        
        # Test edits
        box = arena.new_sandbox()
        try:
            SDZ = box.unit(Zoo, Name='The San Diego Zoo')
            self.assertEqual(SDZ.Name, 'The San Diego Zoo')
            self.assertEqual(SDZ.Founded, datetime.date(1900, 1, 1))
            self.assertEqual(SDZ.Opens, datetime.time(7, 30, 0))
            if fixedpoint:
                self.assertEqual(SDZ.Admission, fixedpoint.FixedPoint(35, 2))
            else:
                self.assertEqual(SDZ.Admission, 35.0)
        finally:
            box.flush_all()
        
        # Change it back
        box = arena.new_sandbox()
        try:
            SDZ = box.unit(Zoo, Name='The San Diego Zoo')
            SDZ.Name = 'San Diego Zoo'
            SDZ.Founded = datetime.date(1835, 9, 13)
            SDZ.Opens = datetime.time(9, 0, 0)
            SDZ.Admission = "0"
        finally:
            box.flush_all()
        
        # Test re-edits
        box = arena.new_sandbox()
        try:
            SDZ = box.unit(Zoo, Name='San Diego Zoo')
            self.assertEqual(SDZ.Name, 'San Diego Zoo')
            self.assertEqual(SDZ.Founded, datetime.date(1835, 9, 13))
            self.assertEqual(SDZ.Opens, datetime.time(9, 0, 0))
            if fixedpoint:
                self.assertEqual(SDZ.Admission, fixedpoint.FixedPoint(0, 2))
            else:
                self.assertEqual(SDZ.Admission, 0.0)
        finally:
            box.flush_all()
    
    def test_7_Multirecall(self):
        box = arena.new_sandbox()
        try:
            f = (lambda z, a: z.Name == 'San Diego Zoo')
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
            leo = lambda z, a: a.Species == 'Leopard'
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
            f = (lambda a, z: a.Legs >= 4 and z.Admission < 10)
            animal_zoos = box.recall(Animal & Zoo, f)
            self.assertEqual(len(animal_zoos), 4)
            names = [a.Species for a, z in animal_zoos]
            names.sort()
            self.assertEqual(names, ['Leopard', 'Lion', 'Millipede', 'Tiger'])
            
            # Let's try three joined classes just for the sadistic fun of it.
            tree = (Animal >> Zoo) >> Vet
            f = (lambda a, z, v: z.Name == 'Sea_World')
            self.assertEqual(len(box.recall(tree, f)), 2)
            
            # MSAccess can't handle an INNER JOIN nested in an OUTER JOIN.
            # Test that this fails for MSAccess, but works for other SM's.
            trees = []
            def make_tree():
                trees.append( (Animal & Zoo) >> Vet )
            warnings.filterwarnings("ignore", category=errors.StorageWarning)
            try:
                make_tree()
            finally:
                warnings.filters.pop(0)
            
            azv = []
            def set_azv():
                f = (lambda a, z, v: z.Name == 'Sea_World')
                azv.append(box.recall(trees[0], f))
            
            smname = arena.stores['testSM'].__class__.__name__
            if smname in ("StorageManagerADO_MSAccess",):
                self.assertRaises(pythoncom.com_error, set_azv)
            else:
                set_azv()
                self.assertEqual(len(azv[0]), 2)
            
            # Try mentioning the same class twice.
            tree = (Animal << Animal)
            f = (lambda anim, mother: mother.ID != None)
            animals = [mother.ID for anim, mother in box.recall(tree, f)]
            self.assertEqual(animals, [11])
        finally:
            box.flush_all()
            
    def test_8_CustomAssociations(self):
        box = arena.new_sandbox()
        try:
            # Try different association paths
            std_expected = ['Live Bunny Wabbit', 'Live Fish', 'Live Fish', 'T-Bone']
            cus_expected = ['Dead Fish', 'Dead Fish', 'Live Bunny Wabbit', 'T-Bone']
            uj = Animal & Food
            for path, expected in [# standard path
                                   (None, std_expected),
                                   # custom path
                                   ('Alternate Food', cus_expected)]:
                
                uj.path = path
                foods = [food for animal, food in box.recall(uj)]
                foods.sort(dejavu.sort('Name'))
                self.assertEqual([f.Name for f in foods], expected)

            # Test the magic association methods
            tiger = box.unit(Animal, Species='Tiger')
            self.assertEqual(tiger.Food().Name, 'Live Bunny Wabbit')
            self.assertEqual(tiger.AlternateFood().Name, 'T-Bone')
            
        finally:
            box.flush_all()
    
    def test_Iteration(self):
        box = arena.new_sandbox()
        try:
            # Test box.unit inside of xrecall
            for visit in box.xrecall(Visit, VetID=1):
                firstvisit = box.unit(Visit, VetID=1, Date=Jan_1_2001)
                self.assertEqual(firstvisit.VetID, 1)
                self.assertEqual(visit.VetID, 1)
            
            # Test recall inside of xrecall
            for visit in box.xrecall(Visit, VetID=1):
                f = (lambda x: x.VetID == 1 and x.ID != visit.ID)
                othervisits = box.recall(Visit, f)
                self.assertEqual(len(othervisits), len(every13days) - 1)
            
            # Test far associations inside of xrecall
            for visit in box.xrecall(Visit, VetID=1):
                # visit.Vet is a ToOne association, so will return a unit or None.
                vet = visit.Vet()
                self.assertEqual(vet.ID, 1)
        finally:
            box.flush_all()
    
    def test_Engines(self):
        box = arena.new_sandbox()
        try:
            quadrupeds = box.recall(Animal, Legs=4)
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
        finally:
            box.flush_all()
    
    def test_Subclassing(self):
        box = arena.new_sandbox()
        try:
            box.memorize(Visit(VetID=21, ZooID=1, AnimalID=1))
            box.memorize(Visit(VetID=21, ZooID=1, AnimalID=2))
            box.memorize(Visit(VetID=32, ZooID=1, AnimalID=3))
            box.memorize(Lecture(VetID=21, ZooID=1, Topic='Cage Cleaning'))
            box.memorize(Lecture(VetID=21, ZooID=1, Topic='Ape Mating Habits'))
            box.memorize(Lecture(VetID=32, ZooID=3, Topic='Your Tiger and Steroids'))
            
            visits = box.recall(Visit, inherit=True, ZooID=1)
            self.assertEqual(len(visits), 5)
            
            box.flush_all()
            
            box = arena.new_sandbox()
            visits = box.recall(Visit, inherit=True, VetID=21)
            self.assertEqual(len(visits), 4)
            cc = [x for x in visits
                  if getattr(x, "Topic", None) == "Cage Cleaning"]
            self.assertEqual(len(cc), 1)
            
            # Checking for non-existent attributes in/from subclasses
            # isn't supported yet.
    ##        f = logic.filter(AnimalID=2)
    ##        self.assertEqual(len(box.recall(Visit, f)), 1)
    ##        self.assertEqual(len(box.recall(Lecture, f)), 0)
        finally:
            box.flush_all()
    
    def test_DB_Introspection(self):
        s = arena.stores.values()[0]
        if not hasattr(s, "db"):
            print "not a db (skipped) ",
            return
        
        zootable = s.db['Zoo']
        cols = zootable
        self.assertEqual(len(cols), 6)
        idcol = cols['ID']
        self.assertEqual(s.db.python_type(idcol.dbtype), int)
        for prop in Zoo.properties:
            self.assertEqual(cols[prop].key,
                             prop in Zoo.identifiers)
    
    def test_zzz_Schema_Upgrade(self):
        # Must run last.
        zs = ZooSchema(arena)
        
        # In this first upgrade, we simulate the case where the code was
        # upgraded, and the database schema upgrade performed afterward.
        # The Schema.latest property is set, and upgrade() is called with
        # no argument (which should upgrade us to "latest").
        Animal.set_property("ExhibitID")
        # Test numeric default (see hack in storeado for MS Access).
        prop = Animal.set_property("Stomachs", int)
        prop.default = 1
        zs.latest = 2
        zs.upgrade()
        
        # In this example, we simulate the developer who wants to put
        # model changes inline with database changes (see upgrade_to_3).
        # We do not set latest, but instead supply an arg to upgrade().
        zs.upgrade(3)
        
        # Test that Animals have a new "Family" property, and an ExhibitID.
        box = arena.new_sandbox()
        try:
            emp = box.unit(Animal, Family='Emperor Penguin')
            self.assertEqual(emp.ExhibitID, 'The Penguin Encounter')
        finally:
            box.flush_all()
    
    def test_numbers(self):
##        print "skipped ",
##        return
        
        float_prec = 53
        box = arena.new_sandbox()
        try:
            print "precision:",
            # PostgreSQL should be able to go up to 1000 decimal digits (~= 2 ** 10),
            # but SQL constants don't actually overflow until 2 ** 15. Meh.
            db = getattr(arena.stores['testSM'], "db", None)
            if db:
                import math
                maxprec = db.typeadapter.numeric_max_precision
                if maxprec == 0:
                    # SQLite, for example, must always use TEXT.
                    # So we might as well try... oh... how about 3?
                    overflow_prec = 3
                else:
                    overflow_prec = int(math.log(maxprec, 2)) + 1
            else:
                overflow_prec = 8
            
            dc = decimal.getcontext()
            
            for prec in xrange(overflow_prec + 1):
                p = 2 ** prec
                print p,
                if p > dc.prec:
                    dc.prec = p
                
                # We don't need to test <type long> at different 'scales'.
                long_done = False
                # Test scales at both extremes and the median
                for s in (0, int(prec/2), max(prec-1, 0)):
                    s = 2 ** s
                    
                    # Modify the model and storage
                    if not long_done:
                        arena.drop_property(NothingToDoWithZoos, 'ALong')
                        NothingToDoWithZoos.ALong.hints['bytes'] = p
                        arena.add_property(NothingToDoWithZoos, 'ALong')
                    if p <= float_prec:
                        arena.drop_property(NothingToDoWithZoos, 'AFloat')
                        NothingToDoWithZoos.AFloat.hints['precision'] = p
                        arena.add_property(NothingToDoWithZoos, 'AFloat')
                    if decimal:
                        arena.drop_property(NothingToDoWithZoos, 'ADecimal')
                        NothingToDoWithZoos.ADecimal.hints['precision'] = p
                        NothingToDoWithZoos.ADecimal.hints['scale'] = s
                        arena.add_property(NothingToDoWithZoos, 'ADecimal')
                    if fixedpoint:
                        arena.drop_property(NothingToDoWithZoos, 'AFixed')
                        NothingToDoWithZoos.AFixed.hints['precision'] = p
                        NothingToDoWithZoos.AFixed.hints['scale'] = s
                        arena.add_property(NothingToDoWithZoos, 'AFixed')
                    
                    # Create an instance and set the specified precision/scale
                    nothing = NothingToDoWithZoos()
                    if not long_done:
                        Lval = (16 ** p) - 1
                        setattr(nothing, 'ALong', Lval)
                    if p <= float_prec:
                        fval = float(((2 ** p) - 1) / (2 ** s))
                        setattr(nothing, 'AFloat', fval)
                    nval = "1" * p
                    nval = nval[:-s] + "." + nval[-s:]
                    if decimal:
                        dval = decimal.Decimal(nval)
                        setattr(nothing, 'ADecimal', dval)
                    if fixedpoint:
                        # fixedpoint uses "precision" where we use "scale";
                        # that is, number of digits after the decimal point.
                        fpval = fixedpoint.FixedPoint(nval, s)
                        setattr(nothing, 'AFixed', fpval)
                    box.memorize(nothing)
                    
                    # Flush and retrieve the object. Use comparisons to test
                    # decompilation of imperfect_type when using large numbers.
                    if not long_done:
                        box.flush_all()
                        nothing = box.unit(NothingToDoWithZoos, ALong=Lval)
                        if nothing is None:
                            self.fail("Unit not found by long property. "
                                      "prec=%s scale=%s" % (p, s))
                    if p <= float_prec:
                        box.flush_all()
                        nothing = box.unit(NothingToDoWithZoos, AFloat=fval)
                        if nothing is None:
                            self.fail("Unit not found by float property. "
                                      "prec=%s scale=%s" % (p, s))
                    if decimal:
                        box.flush_all()
                        nothing = box.unit(NothingToDoWithZoos, ADecimal=dval)
                        if nothing is None:
                            self.fail("Unit not found by decimal property. "
                                      "prec=%s scale=%s" % (p, s))
                    if fixedpoint:
                        box.flush_all()
                        nothing = box.unit(NothingToDoWithZoos, AFixed=fpval)
                        if nothing is None:
                            self.fail("Unit not found by fixedpoint property. "
                                      "prec=%s scale=%s" % (p, s))
                    
                    # Test retrieved values.
                    if not long_done:
                        if nothing.ALong != Lval:
                            self.fail("%s != %s prec=%s scale=%s" %
                                      (`nothing.ALong`, `Lval`, p, s))
                    if p <= float_prec:
                        if nothing.AFloat != fval:
                            self.fail("%s != %s prec=%s scale=%s" %
                                      (`nothing.AFloat`, `fval`, p, s))
                    if decimal:
                        if nothing.ADecimal != dval:
                            self.fail("%s != %s prec=%s scale=%s" %
                                      (`nothing.ADecimal`, `dval`, p, s))
                    if fixedpoint:
                        if nothing.AFixed != fpval:
                            self.fail("%s != %s prec=%s scale=%s" %
                                      (`nothing.AFixed`, `fpval`, p, s))
                    nothing.forget()
                    box.flush_all()
                    long_done = True
        finally:
            box.flush_all()


class IsolationTests(unittest.TestCase):
    
    verbose = False
    _boxid = 0
    
    def setUp(self):
        s = arena.stores.values()[0]
        if hasattr(s, "db"):
            self.db = s.db
        else:
            self.db = None
        
        try:
            self.old_implicit = s.db.implicit_trans
            s.db.implicit_trans = False
            self.old_tkey = s.db.transaction_key
            # Use an explicit 'boxid' for the transaction key
            s.db.transaction_key = lambda: self.boxid
        except AttributeError:
            self.old_implicit = None
        
    
    def tearDown(self):
        if self.db and self.old_implicit is not None:
            self.db.implicit_trans = self.old_implicit
            self.db.transaction_key = self.old_tkey
    
    def restore(self):
        self.boxid = 0
        box = arena.new_sandbox()
        box.start()
        jim = box.unit(Vet, Name = 'Jim McBain')
        jim.City = None
        box.flush_all()
    
    def cleanup_boxes(self):
        try:
            self.boxid = 1
            self.box1.rollback()
        except: pass
        try:
            self.boxid = 2
            self.box2.rollback()
        except: pass
        
        # Destroy refs so the conns can go back in the pool.
        del self.box1, self.box2
    
    def attempt(self, testfunc, anomaly_name, level):
        self.restore()
        
        self.boxid = 1
        self.box1 = arena.new_sandbox()
        self.box1.start(level)
        
        self.boxid = 2
        self.box2 = arena.new_sandbox()
        self.box2.start(level)
        
        try:
            testfunc(level)
        except AssertionError:
            self.cleanup_boxes()
            if level.forbids(anomaly_name):
                warnings.warn("%r allowed anomaly %r." %
                              (level, anomaly_name))
        except:
            if self.db.is_lock_error(sys.exc_info()[1]):
                self.cleanup_boxes()
                if not level.forbids(anomaly_name):
                    warnings.warn("%r prevented anomaly %r with an error." %
                                  (level, anomaly_name))
            else:
                self.cleanup_boxes()
                raise
        else:
            self.cleanup_boxes()
            if not level.forbids(anomaly_name):
                warnings.warn("%r prevented anomaly %r." %
                              (level, anomaly_name))
    
    def _get_boxid(self):
        return self._boxid
    def _set_boxid(self, val):
        if self.verbose:
            print val,
        self._boxid = val
    boxid = property(_get_boxid, _set_boxid)
    
    def test_dirty_read(self):
        def dirty_read(level):
            # Write City 1
            self.boxid = 1
            jim1 = self.box1.unit(Vet, Name = 'Jim McBain')
            jim1.City = "Addis Ababa"
            self.box1.repress(jim1)
            
            # Read City 2.
            self.boxid = 2
            jim2 = self.box2.unit(Vet, Name = 'Jim McBain')
            # If READ UNCOMMITTED or lower, this should fail
            assert jim2.City is None
        
        for level in storage.isolation.levels:
            if self.verbose:
                print
                print level,
            if level.name in self.db.isolation_levels:
                self.attempt(dirty_read, "Dirty Read", level)
    
    def test_nonrepeatable_read(self):
        def nonrepeatable_read(level):
            # Read City 1
            self.boxid = 1
            jim1 = self.box1.unit(Vet, Name = 'Jim McBain')
            val1 = jim1.City
            assert val1 is None
            self.box1.repress(jim1)
            
            # Write City 2.
            self.boxid = 2
            jim2 = self.box2.unit(Vet, Name = 'Jim McBain')
            jim2.City = "Tehachapi"
            self.box2.flush_all()
        
            # Re-read City 1
            self.boxid = 1
            jim1 = self.box1.unit(Vet, Name = 'Jim McBain')
            # If READ COMMITTED or lower, this should fail
            assert jim1.City == val1
        
        for level in storage.isolation.levels:
            if self.verbose:
                print
                print level,
            if level.name in self.db.isolation_levels:
                self.attempt(nonrepeatable_read, "Nonrepeatable Read", level)
    
    def test_phantom(self):
        def phantom(level):
            # Read City 1
            self.boxid = 1
            pvets = self.box1.recall(Vet, City = 'Poughkeepsie')
            assert len(pvets) == 0
            
            # Write City 2.
            self.boxid = 2
            jim2 = self.box2.unit(Vet, Name = 'Jim McBain')
            jim2.City = "Poughkeepsie"
            self.box2.flush_all()
        
            # Re-read City 1
            self.boxid = 1
            pvets = self.box1.recall(Vet, City = 'Poughkeepsie')
            # If REPEATABLE READ or lower, this should fail
            assert len(pvets) == 0
        
        for level in storage.isolation.levels:
            if self.verbose:
                print
                print level,
            if level.name in self.db.isolation_levels:
                self.attempt(phantom, "Phantom", level)


class ConcurrencyTests(unittest.TestCase):
    
    def test_Multithreading(self):
##        print "skipped ",
##        return
        
        s = arena.stores.values()[0]
        
        # Test threads overlapping on separate sandboxes
        f = (lambda x: x.Legs == 4)
        def box_per_thread():
            # Notice that, although we write changes in each thread,
            # we only assert the unchanged data, since the order of
            # thread execution can not be guaranteed.
            box = arena.new_sandbox()
            try:
                quadrupeds = box.recall(Animal, f)
                self.assertEqual(len(quadrupeds), 4)
                quadrupeds[0].Age += 1.0
            finally:
                box.flush_all()
        ts = []
        # PostgreSQL, for example, has a default max_connections of 100.
        for x in range(99):
            t = threading.Thread(target=box_per_thread)
            t.start()
            ts.append(t)
        for t in ts:
            t.join()
    
    def test_Implicit_Transactions(self):
        zoostore = arena.storage(Zoo)
        
        if not hasattr(zoostore, "db"):
            print "not a db (skipped) ",
            return
        
        old_implicit = zoostore.db.implicit_trans
        try:
            def commit_test():
                """Test transaction commit."""
                now = datetime.time(8, 18, 28)
                
                box = arena.new_sandbox()
                try:
                    WAP = box.unit(Zoo, Name='Wild Animal Park')
                    WAP.Opens = now
                    box.flush_all()
                    WAP = box.unit(Zoo, Name='Wild Animal Park')
                    self.assertEqual(WAP.Opens, now)
                finally:
                    box.flush_all()
            
            def rollback_test():
                """Test transaction rollback."""
                box = arena.new_sandbox()
                try:
                    SDZ = box.unit(Zoo, Name='San Diego Zoo')
                    SDZ.Name = 'The One and Only San Diego Zoo'
                    SDZ.Founded = datetime.date(2039, 9, 13)
                    box.rollback()
                    SDZ = box.unit(Zoo, Name='San Diego Zoo')
                    self.assertEqual(SDZ.Name, 'San Diego Zoo')
                    self.assertEqual(SDZ.Founded, datetime.date(1835, 9, 13))
                finally:
                    box.flush_all()
            
            zoostore.db.implicit_trans = True
            commit_test()
            if zoostore.rollback:
                rollback_test()
            
            zoostore.db.implicit_trans = False
            zoostore.start()
            commit_test()
            if zoostore.rollback:
                zoostore.start()
                rollback_test()
        finally:
            zoostore.db.implicit_trans = old_implicit
    
    def test_ContextManagement(self):
        # Test context management using Python 2.5 'with ... as'
        try:
            from dejavu.test import test_context
        except SyntaxError:
            print "'with ... as' not supported (skipped) ",
        else:
            test_context.test_with_context(arena)


class DiscoveryTests(unittest.TestCase):
    
    def assertIn(self, first, second, msg=None):
        """Fail if 'second not in first'."""
        if not second.lower() in first.lower():
            raise self.failureException, (msg or '%r not in %r' % (second, first))
    
    def setUp(self):
        self.modeler = None
        
        s = arena.stores.values()[0]
        if not hasattr(s, "db"):
            return
        
        # Clear out all mappings and re-discover
        dict.clear(s.db)
        s.db.discover_all()
        
        from dejavu.storage import db
        self.modeler = db.Modeler(s.db)
    
    def test_make_classes(self):
        if not self.modeler:
            print "not a db (skipped) ",
            return
        
        for cls in (Zoo, Animal):
            tkey = self.modeler.db.table_name(cls.__name__)
            
            uc = self.modeler.make_class(tkey, cls.__name__)
            self.assert_(not issubclass(uc, cls))
            self.assertEqual(uc.__name__, cls.__name__)
            
            # Both Zoo and Animal should have autoincrementing ID's
            # (but MySQL uses all lowercase identifiers).
            self.assertEqual(set([x.lower() for x in uc.identifiers]),
                             set([x.lower() for x in cls.identifiers]))
            self.assert_(isinstance(uc.sequencer, UnitSequencerInteger),
                         "sequencer is of type %r (expected %r)"
                         % (type(uc.sequencer), UnitSequencerInteger))
            
            for pname in cls.properties:
                cname = self.modeler.db.column_name(tkey, pname)
                copy = getattr(uc, cname)
                orig = getattr(cls, pname)
                self.assertEqual(copy.key, cname)
                # self.assertEqual(copy.type, orig.type)
                self.assertEqual(copy.default, orig.default,
                                 "%s.%s default %s != copy %s"
                                 % (cls.__name__, pname,
                                    `orig.default`, `copy.default`))
                
                for k, v in orig.hints.iteritems():
                    if isinstance(v, (int, long)):
                        v2 = copy.hints.get(k)
                        if v2 != 0 and v2 < v:
                            self.fail("%s.%s hint[%s] %s not >= %s" %
                                      (cls.__name__, pname, k, v2, v))
                    else:
                        self.assertEqual(copy.hints[k], v)
    
    def test_make_source(self):
        if not self.modeler:
            print "not a db (skipped) ",
            return
        
        tkey = self.modeler.db.table_name('Exhibit')
        source = self.modeler.make_source(tkey, 'Exhibit')
        
        classline = "class Exhibit(Unit):"
        if not source.lower().startswith(classline.lower()):
            self.fail("%r does not start with %r" % (source, classline))
        
        clsname = self.modeler.db.__class__.__name__
        if "SQLite" in clsname:
            # SQLite's internal types are teh suck.
            self.assertIn(source, "    Name = UnitProperty(")
            self.assertIn(source, "    ZooID = UnitProperty(")
            self.assertIn(source, "    PettingAllowed = UnitProperty(")
            self.assertIn(source, "    Acreage = UnitProperty(")
            self.assertIn(source, "    sequencer = UnitSequencer")
        else:
            try:
                self.assertIn(source, "    Name = UnitProperty(unicode")
            except AssertionError:
                self.assertIn(source, "    Name = UnitProperty(str")
            
            self.assertIn(source, "    ZooID = UnitProperty(int")
            if "Firebird" in self.modeler.db.__class__.__name__:
                # Firebird doesn't have a bool datatype
                self.assertIn(source, "    PettingAllowed = UnitProperty(int")
            else:
                self.assertIn(source, "    PettingAllowed = UnitProperty(bool")
            if decimal:
                self.assertIn(source, "    Acreage = UnitProperty(decimal.Decimal")
            else:
                self.assertIn(source, "    Acreage = UnitProperty(float")
            
            self.assertIn(source, "    sequencer = UnitSequencer()")
        
        
        if "    ID = UnitProperty" in source:
            self.fail("Exhibit incorrectly possesses an ID property.")
        
        # ID = None should remove the existing ID property
        self.assertIn(source, "    ID = None")
        
        for items in ["'zooid', 'name'", "'name', 'zooid'",
                      "u'zooid', u'name'", "u'name', u'zooid'"]:
            if ("    identifiers = (%s)" % items) in source.lower():
                break
        else:
            self.fail("%r not found in %r" %
                      ("    identifiers = ('ZooID', 'Name')", source))


arena = dejavu.Arena()

def _djvlog(message):
    """Dejavu logger (writes to error.log)."""
    if isinstance(message, unicode):
        message = message.encode('utf8')
    s = "%s %s" % (datetime.datetime.now().isoformat(), message)
    f = open(logname, 'ab')
    f.write(s + '\n')
    f.close()

def init():
    global arena
    arena = dejavu.Arena()
    arena.log = _djvlog
    arena.logflags = (dejavu.logflags.ERROR + dejavu.logflags.SQL +
                      dejavu.logflags.IO + dejavu.logflags.RECALL)


class ZooSchema(dejavu.Schema):
    
    # We set "latest" to 1 so we can test upgrading manually.
    latest = 1
    
    def upgrade_to_2(self):
        self.arena.add_property(Animal, "Stomachs")
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
    sm = arena.add_store('testSM', SM_class, opts)
    v = getattr(sm, "version", None)
    if v:
        print v()
    sm.create_database()
    
    arena.register_all(globals())
    engines.register_classes(arena)
    
    zs = ZooSchema(arena)
    zs.upgrade()
    zs.assert_storage()


def teardown():
    """Tear down storage for Zoo classes."""
    # Manually drop each table just to test that code.
    # Call map_all first in case our discovery tests screwed up the keys.
    arena.map_all()
    for cls in arena._registered_classes:
        arena.drop_storage(cls)
    
    for store in arena.stores.values():
        try:
            store.drop_database()
        except (AttributeError, NotImplementedError):
            pass
    arena.stores = {}
    
    arena.shutdown()

def run(SM_class, opts):
    """Run the zoo fixture."""
    try:
        try:
            setup(SM_class, opts)
            loader = unittest.TestLoader().loadTestsFromTestCase
            
            # Run the ZooTests and time it.
            zoocase = loader(ZooTests)
            startTime = datetime.datetime.now()
            tools.djvTestRunner.run(zoocase)
            print "Ran zoo cases in:", datetime.datetime.now() - startTime
            
            # Run the other cases.
            tools.djvTestRunner.run(loader(ConcurrencyTests))
            s = arena.stores.values()[0]
            if hasattr(s, "db"):
                tools.djvTestRunner.run(loader(IsolationTests))
                tools.djvTestRunner.run(loader(DiscoveryTests))
        except:
            traceback.print_exc()
    finally:
        teardown()
