import warnings

try:
    import pythoncom
except ImportError:
    def run():
        warnings.warn("The pythoncom module could not be imported. "
                      "The MSAccess test will not be run.")
else:
    from dejavu.storage import storeado
    try:
        storeado.gen_py()
    except ImportError:
        def run():
            warnings.warn("ADO 2.7 support could not be verified. "
                          "The SQLServer test will not be run.")
    else:
        opts = {u'Connect': ("Provider=SQLOLEDB.1; Integrated Security=SSPI; "
                             "Initial Catalog=dejavu_test; "
                             "Data Source=(local)"),
                # Shorten the transaction deadlock timeout.
                # You may need to adjust this for your system.
                u'CommandTimeout': 10,
                }
        SM_class = "sqlserver"
        
        def run():
            import zoo_fixture
            # Isolate schema changes from one test to the next.
            reload(zoo_fixture)
            zoo_fixture.init()
            zoo_fixture.run(SM_class, opts)

if __name__ == "__main__":
    run()
