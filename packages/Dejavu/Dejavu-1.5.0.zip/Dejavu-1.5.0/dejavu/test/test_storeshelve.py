"""Test the shelve Storage Manager for dejavu.

Notice that, since StorageManagerShelve doesn't decompile any Expressions,
this will also test all native dejavu logic functions and any other aspects
of Expression(unit).
"""

import os

opts = {u'Path': os.path.join(os.path.dirname(__file__), "testdb")}
SM_class = "shelve"

def run():
    import zoo_fixture
    # Isolate schema changes from one test to the next.
    reload(zoo_fixture)
    zoo_fixture.init()
    zoo_fixture.run(SM_class, opts)


if __name__ == "__main__":
    run()
