
try:
    import _sqlite
except ImportError:
    def run():
        import warnings
        warnings.warn("The _sqlite module could not be imported. "
                      "The SQLite test will not be run.")
else:
    SM_class = "dejavu.storage.storesqlite.StorageManagerSQLite"
    opts = {"Database": "sqlite_zoo_test"}
    
    def run():
        import zoo_fixture
        # Isolate schema changes from one test to the next.
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)

if __name__ == "__main__":
    run()
