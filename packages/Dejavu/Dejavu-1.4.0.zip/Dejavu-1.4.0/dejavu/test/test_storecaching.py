import os

shelvedb = "dejavu.storage.storeshelve.StorageManagerShelve"
proxiedopts = {u'Path': os.path.join(os.getcwd(), os.path.dirname(__file__))}
opts = {'Next Store': 'shelvedb',
        'Lifetime': '10 minutes',
        }
SM_class = "dejavu.storage.CachingProxy"


def run():
    import zoo_fixture
    # Isolate schema changes from one test to the next.
    reload(zoo_fixture)
    
    zoo_fixture.init()
    zoo_fixture.arena.add_store('shelvedb', shelvedb, proxiedopts)
    zoo_fixture.run(SM_class, opts)


if __name__ == "__main__":
    run()
