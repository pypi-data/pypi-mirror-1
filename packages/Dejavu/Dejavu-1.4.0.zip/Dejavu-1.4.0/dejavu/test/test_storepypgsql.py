
try:
    from pyPgSQL import libpq
except ImportError:
    def run():
        import warnings
        warnings.warn("The pyPgSQL.libpq module could not be imported. "
                      "The pyPgSQL test will not be run.")
else:
    user = "postgres"
    passwd = ""
    
    if passwd == "":
        passwd = raw_input("Enter the password for the PostgreSQL '%s' user:" % user)
    
    opts = {u'Connect': ("host=localhost dbname=dejavu_test "
                         "user=%s password=%s" % (user, passwd)),
            }
    SM_class = "dejavu.storage.storepypgsql.StorageManagerPgSQL"
    
    del user, passwd
    
    def run():
        import zoo_fixture
        # Isolate schema changes from one test to the next.
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)

if __name__ == "__main__":
    run()
