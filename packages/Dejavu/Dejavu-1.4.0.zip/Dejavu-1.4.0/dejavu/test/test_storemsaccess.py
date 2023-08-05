"""This works...most of the time. Sometimes during the Multithreading,
the Access SM will crash python."""

import warnings

try:
    import pythoncom
except ImportError:
    def run():
        warnings.warn("The pythoncom module could not be imported. "
                      "The MSAccess test will not be run.")
else:
    from dejavu.storage import storeado
    mod = storeado.gen_py()
    if mod is None:
        def run():
            warnings.warn("ADO 2.7 support could not be verified. "
                          "The MSAccess test will not be run.")
    else:
        SM_class = "dejavu.storage.storeado.StorageManagerADO_MSAccess"
        opts = {u'Connect': "PROVIDER=MICROSOFT.JET.OLEDB.4.0;"
                            "DATA SOURCE=zoo.mdb;",
                u'Expanded Columns': "Animal.PreviousZoos:int",
                }
        
        def run():
            import zoo_fixture
            # Isolate schema changes from one test to the next.
            reload(zoo_fixture)
            zoo_fixture.init()
            zoo_fixture.run(SM_class, opts)

if __name__ == "__main__":
    run()
