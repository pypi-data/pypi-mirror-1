import os
thisdir = os.path.join(os.getcwd(), os.path.dirname(__file__))

try:
    import kinterbasdb
except ImportError:
    def run():
        import warnings
        warnings.warn("The kinterbasdb module could not be imported. "
                      "The Firebird test will not be run.")
else:
    user = "sysdba"
    passwd = ""
    
    if passwd == "":
        passwd = raw_input("Enter the password for the Firebird '%s' user: " % user)
    
    # Note that "the Firebird 1.5 client library on Windows is thread-safe
    # if the remote protocol is used ... but is not thread-safe if the
    # local protocol is used, ..."
    opts = {'host': "localhost",
            'name': os.path.join(thisdir, r"test.fdb"),
            'user': user,
            'password': passwd,
            }
    SM_class = "firebird"
    
    del user, passwd
    
    def run():
        import zoo_fixture
        # Isolate schema changes from one test to the next.
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)

if __name__ == "__main__":
    run()
