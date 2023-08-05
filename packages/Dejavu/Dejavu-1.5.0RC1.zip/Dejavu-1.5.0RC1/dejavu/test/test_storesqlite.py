import os
thisdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
dbpath = os.path.join(thisdir, "sqlite_zoo_test")

_sqlite = None
try:
    # Use _sqlite3 directly to avoid all of the DB-API overhead.
    # This assumes the one built into Python 2.5+
    import _sqlite3 as _sqlite
except ImportError:
    try:
        # Use _sqlite directly to avoid all of the DB-API overhead.
        # This will import the "old API for SQLite 3.x",
        # using e.g. pysqlite 1.1.7
        import _sqlite
    except ImportError:
        def run():
            import warnings
            warnings.warn("The _sqlite module could not be imported. "
                          "The SQLite test will not be run.")

if _sqlite:
    SM_class = "sqlite"
    opts = {"Database": dbpath}
    
    def run():
        import zoo_fixture
        # Isolate schema changes from one test to the next.
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)
        
        print
        print "Testing SQLite with 'Perfect Dates'"
        opts['Perfect Dates'] = True
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)
        opts['Perfect Dates'] = False
        
        print
        print "Testing SQLite ':memory:' database..."
        opts['Database'] = ':memory:'
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)
        
        print
        print "Testing SQLite 'typeless'..."
        opts['Database'] = dbpath
        opts['Type Adapter'] = "dejavu.storage.storesqlite.TypeAdapterSQLiteTypeless"
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)

if __name__ == "__main__":
    run()
