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
    SM_class = "dejavu.storage.storemysql.StorageManagerMySQL"
    
    def run():
        import zoo_fixture
        # Isolate schema changes from one test to the next.
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)

if __name__ == "__main__":
    run()
