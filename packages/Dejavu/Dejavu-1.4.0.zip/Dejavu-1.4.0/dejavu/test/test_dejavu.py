import datetime
import unittest
import warnings

import dejavu
from dejavu import logic, storage
from dejavu.test.zoo_fixture import *


arena.add_store("default", "dejavu.storage.CachingProxy")
arena.register(Animal)
arena.register(Lecture)
arena.register(Vet)
arena.register(Visit)
arena.register(Zoo)


class UnitTests(unittest.TestCase):
    
    def setUp(self):
        # CleanUP The Database!
        box = arena.new_sandbox()
        for animal in box.recall(Animal):
            animal.forget()
        for zoo_thing in box.recall(Zoo):
            zoo_thing.forget()
    
    def test_Properties(self):
        # Instance creation and population
        f = datetime.date(1916, 10, 2)
        z = Zoo(Name='San Diego Zoo', Founded=f)
        self.assertEqual(z.dirty(), True)
        self.assertEqual(Zoo.ID.type, int)
        self.assertEqual(z.ID, None)
        self.assertEqual(z.Name, 'San Diego Zoo')
        self.assertEqual(type(z.Name), unicode)
        self.assertEqual(z.Founded, f)
        self.assertEqual(z.__class__.ID.index, True)
        
        a = Animal(Species='Giraffe')
        self.assertEqual(a.dirty(), True)
        self.assertEqual(a.ID, None)
        self.assertEqual(a.Species, 'Giraffe')
        # 4 should be supplied by default
        self.assertEqual(a.Legs, 4)
        self.assertEqual(a.__class__.ZooID.index, True)
        
        # Sandboxing
        s = arena.new_sandbox()
        s.memorize(z)
        self.assertEqual(z.ID, 1)
        s.memorize(a)
        self.assertEqual(a.ID, 1)
        z.add(a)
        self.assertEqual(a.ZooID, 1)
        
        # Triggers
        z.cleanse()
        self.assertEqual(z.dirty(), False)
        a.LastEscape = d = datetime.datetime(2004, 10, 20)
        self.assertEqual(a.LastEscape, d)
        self.assertEqual(z.LastEscape, d)
        self.assertEqual(z.dirty(), True)
    
    def test_associations(self):
        # Test for ticket #35.
        box = arena.new_sandbox()
        box.memorize(Animal(Species='Liger'))
        box.memorize(Zoo(Name='Wallingford'))
        box.flush_all()
        box = arena.new_sandbox()
        liger = box.unit(Animal, Species='Liger')
        wall = box.unit(Zoo, Name='Wallingford')
        liger.ZooID = wall.ID
        self.assertEqual(len([a for a in wall.Animal()]), 1)
        box.flush_all()
    
    def test_xrecall(self):
        # Make sure multiple, simultaneous xrecalls recall all units.
        
        # Create some animals in a sandbox
        box = arena.new_sandbox()
        box.memorize(Animal(Species='Wombat'))
        box.memorize(Animal(Species='Lizard'))
        
        animals = []
        animals2 = []
        
        # Start a new sandbox with no cache
        box = arena.new_sandbox()
        
        # get animals alternating from two different xrecalls
        animals_is_stopped = False
        animals2_is_stopped = False
        animals_iter = box.xrecall(Animal)
        animals2_iter = box.xrecall(Animal)
        while not (animals_is_stopped and animals2_is_stopped):
            try:
                animals.append(animals_iter.next())
            except StopIteration:
                animals_is_stopped = True
            
            try:
                animals2.append(animals2_iter.next())
            except StopIteration:
                animals2_is_stopped = True
        
        for animal in animals:
            self.failUnless(
                animal in animals2,
                "An instance in the first xrecall wasn't in the second" )
        
        for animal in animals2:
            self.failUnless(
                animal in animals,
                "An instance was in the second xrecall but not the first" )
    
    def test_sandbox_cache(self):
        # Make sure the _sandbox_ cache is being used, not the CachingProxy's.
        
        # Create an animal in a sandbox, but retain a reference to it
        box = arena.new_sandbox()
        bat = Animal(Species='Bat')
        box.memorize(bat)
        
        # Modify the unit which is in the sandbox cache.
        bat.Legs = 2
        
        # Retrieve the Unit from the same sandbox again.
        self.assert_(box.unit(Animal) is bat)
        
        # Retrieve the Unit from a new sandbox.
        # Units should be different, and their
        # UnitProperties should be different.
        bat3 = arena.new_sandbox().unit(Animal)
        self.assert_(bat3 is not bat)
        self.assertEqual(bat3.Legs, 4)
    
    def test_Subclassing(self):
        box = arena.new_sandbox()
        box.memorize(Visit(VetID=1, ZooID=1, AnimalID=1))
        box.memorize(Visit(VetID=1, ZooID=1, AnimalID=2))
        box.memorize(Visit(VetID=2, ZooID=1, AnimalID=3))
        box.memorize(Lecture(VetID=1, ZooID=1, Topic='Cage Cleaning'))
        box.memorize(Lecture(VetID=1, ZooID=1, Topic='Ape Mating Habits'))
        box.memorize(Lecture(VetID=2, ZooID=3, Topic='Your Tiger and Steroids'))
        
        visits = box.recall(Visit)
        self.assertEqual(len(visits), 6)
        
        box.flush_all()
        
        box = arena.new_sandbox()
        visits = box.recall(Visit)
        self.assertEqual(len(visits), 6)
        cc = [x for x in visits
              if getattr(x, "Topic", None) == "Cage Cleaning"]
        self.assertEqual(len(cc), 1)
        
        f = logic.filter(AnimalID=2)
        self.assertEqual(len(box.recall(Visit, f)), 1)
        self.assertEqual(len(box.recall(Lecture, f)), 0)
    
    def test_UnitJoin(self):
        box = arena.new_sandbox()
        tree = Animal & Zoo
        self.assertEqual(str(tree), "(Animal & Zoo)")
        tree = Animal << Zoo
        self.assertEqual(str(tree), "(Animal << Zoo)")
        tree = Animal >> Zoo
        self.assertEqual(str(tree), "(Animal >> Zoo)")
        
        trees = []
        def make_tree():
            trees.append( (Animal & Zoo) >> Exhibit )
        
        warnings.filterwarnings("error", category=dejavu.StorageWarning)
        try:
            self.assertRaises(dejavu.StorageWarning, make_tree)
        finally:
            warnings.filters.pop(0)
        
        # Since we raised the warning, our first make_tree failed.
        warnings.filterwarnings("ignore", category=dejavu.StorageWarning)
        try:
            make_tree()
        finally:
            warnings.filters.pop(0)
        
        self.assertEqual(str(trees[0]), "((Animal & Zoo) >> Exhibit)")
        tree = trees[0] & (Visit << Vet) & Exhibit
        self.assertEqual(str(tree), "((((Animal & Zoo) >> Exhibit) & "
                                    "(Visit << Vet)) & Exhibit)")
        self.assertEqual(list(tree), [Animal, Zoo, Exhibit, Visit, Vet, Exhibit])


if __name__ == "__main__":
    unittest.main(__name__)

