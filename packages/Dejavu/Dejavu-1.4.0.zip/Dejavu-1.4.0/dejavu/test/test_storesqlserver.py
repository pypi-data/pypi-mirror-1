from dejavu.storage import storeado
mod = storeado.gen_py()
if mod is None:
    def run():
        import warnings
        warnings.warn("ADO 2.7 support could not be verified. "
                      "The SQLServer test will not be run.")
else:
    opts = {u'Connect': ("Provider=SQLOLEDB.1; Integrated Security=SSPI; "
                         "Initial Catalog=dejavu_test; "
                         "Data Source=REDROVER\\"),
            u'Expanded Columns': "Animal.PreviousZoos:int",
            }
    SM_class = "dejavu.storage.storeado.StorageManagerADO_SQLServer"
    
    def run():
        import zoo_fixture
        # Isolate schema changes from one test to the next.
        reload(zoo_fixture)
        zoo_fixture.init()
        zoo_fixture.run(SM_class, opts)

if __name__ == "__main__":
    run()
