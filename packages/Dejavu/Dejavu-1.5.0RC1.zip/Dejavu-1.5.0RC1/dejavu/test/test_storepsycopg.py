
try:
    try:
        # If possible, you should copy the _psycopg.pyd file into a top level
        # so the SM can avoid importing the entire package.
        import _psycopg
    except ImportError:
        from psycopg2 import _psycopg
except ImportError:
    def run():
        import warnings
        warnings.warn("The psycopg2._psycopg module could not be imported. "
                      "The psycopg test will not be run.")
else:
    user = "postgres"
    passwd = ""
    
    if passwd == "":
        passwd = raw_input("Enter the password for the PostgreSQL '%s' user:" % user)
    
    opts = {u'Connect': ("host=localhost dbname=dejavu_test "
                         "user=%s password=%s" % (user, passwd)),
            }
    SM_class = "psycopg"
    
    del user, passwd
    
    def run():
        # Isolate schema changes from one test to the next.
        import zoo_fixture
        
        print "Testing PostgreSQL with 'SQL_ASCII' encoding..."
        opts['encoding'] = "SQL_ASCII"
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)
        
        print
        print "Testing PostgreSQL with 'UNICODE' encoding..."
        opts['encoding'] = "UNICODE"
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)

if __name__ == "__main__":
    run()
