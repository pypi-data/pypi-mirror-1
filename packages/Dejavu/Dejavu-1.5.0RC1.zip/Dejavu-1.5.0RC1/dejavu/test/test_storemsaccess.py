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
                          "The MSAccess test will not be run.")
    else:
        
        class CurrencyAdapter(storeado.TypeAdapter_MSAccess):
            """Stores Decimal and FixedPoint objects as CURRENCY."""
            
            def decimal_type(self, colname, precision, scale):
                if precision == 0:
                    precision = 19
                if scale > precision:
                    scale = precision
                if scale > 4 or precision - scale > 15:
                    return "TEXT"
                return "CURRENCY"
            
        SM_class = "access"
        opts = {u'Connect': "PROVIDER=MICROSOFT.JET.OLEDB.4.0;"
                            "DATA SOURCE=zoo.mdb;",
                }
        
        def run():
            import zoo_fixture
            
            # lists to keep track of the test_currency runs
            standard_runs = []
            altered_runs = []
            
            def test_currency(obj):
                sm = zoo_fixture.arena.stores['testSM']
                fta = sm.db.typeadapter.__class__.__name__
                
                for c, p in [('Exhibit', 'Acreage'), ('Zoo', 'Admission')]:
                    dbtype = sm.db[c][p].dbtype
                    if fta == "CurrencyAdapter":
                        if dbtype != "CURRENCY" and not dbtype.startswith("WCHAR"):
                            obj.fail("%s wrong type for %s.%s" % (dbtype, c, p))
                    else:
                        if not dbtype.startswith("NUMERIC") and not dbtype.startswith("WCHAR"):
                            obj.fail("%s wrong type for %s.%s" % (dbtype, c, p))
                        obj.assertEqual(len(standard_runs), 0)
            
            # Isolate schema changes from one test to the next.
            reload(zoo_fixture)
            
            # test the standard MS Access setup where Decimal and FixedPoint
            # objects are stored in the database as INTEGERS, LONGS or NUMERIC
            print
            print "Standard MSAccess test."
            zoo_fixture.ZooTests.test_currency = test_currency
            zoo_fixture.init()
            zoo_fixture.run(SM_class, opts)
            standard_runs.append(True)
            
            # plugin the adapter for testing CURRENCY columns
            storeado.MSAccessDatabase.typeadapter = CurrencyAdapter()
            
            reload(zoo_fixture)
            
            # test storing and recalling Decimal values to the database using
            # CURRENCY columns - the (current) default behavior of pythoncom
            # is to return CURRENCY values as a tuple
            print
            print "MSAccess test - CURRENCY returned as tuple."
            zoo_fixture.ZooTests.test_currency = test_currency
            zoo_fixture.init()
            zoo_fixture.run(SM_class, opts)
            altered_runs.append(True)
            
            # set pythoncom to return CURRENCY values as Decimal objects
            pythoncom.__future_currency__ = True
            
            reload(zoo_fixture)
            
            # test storing and recalling Decimal values to the database using
            # CURRENCY columns - CURRENCY values are now returned as Decimal
            # objects
            print
            print "MSAccess test - CURRENCY returned as Decimal."
            zoo_fixture.ZooTests.test_currency = test_currency
            zoo_fixture.init()
            zoo_fixture.run(SM_class, opts)
            altered_runs.append(True)


if __name__ == "__main__":
    run()
