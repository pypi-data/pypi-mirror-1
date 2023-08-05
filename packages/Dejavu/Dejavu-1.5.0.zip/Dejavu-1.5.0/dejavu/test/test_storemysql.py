try:
    import _mysql
except ImportError:
    def run():
        import warnings
        warnings.warn("The _mysql module could not be imported. "
                      "The test for MySQL will not be run.")
else:
    opts = {"host": "localhost",
            "db": "dejavu_test",
            "user": "root",
            "passwd": "",
            }
    if opts['passwd'] == "":
        opts['passwd'] = raw_input("Enter the password for the MySQL '%s' user:"
                                   % opts['user'])
    SM_class = "mysql"
    
    def run():
        # Isolate schema changes from one test to the next.
        import zoo_fixture
        
        print "Testing MySQL with 'latin1' encoding..."
        opts['encoding'] = "latin1"
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)
        
        print
        print "Testing MySQL with 'utf8' encoding..."
        opts['encoding'] = "utf8"
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)

if __name__ == "__main__":
    run()
