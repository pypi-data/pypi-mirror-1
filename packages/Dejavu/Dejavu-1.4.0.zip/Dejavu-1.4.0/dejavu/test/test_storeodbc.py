
def create_access_db():
    # Create the database.
    import win32com.client
    cat = win32com.client.Dispatch(r'ADOX.Catalog')
    cat.Create("PROVIDER=MICROSOFT.JET.OLEDB.4.0;DATA SOURCE=zooodbc.mdb;")

create_access_db()

# Once again, we find that the first param must be repeated
# in the connection string. Not sure why.
opts = {u'Connect': ("Provider=MSDASQL;"
                     "Driver={Microsoft Access Driver (*.mdb)};"
                     "DBQ=zooodbc.mdb;Provider=MSDASQL;"),
        u'Expanded Columns': "Animal.PreviousZoos:int",
        }
SM_class = "dejavu.storage.storeodbc.StorageManagerODBC"


if __name__ == "__main__":
    import zoo_fixture
    try:
        zoo_fixture.run(SM_class, opts)
    finally:
        try:
            import os; os.remove("zooodbc.mdb")
        except OSError:
            print "Could not remove database."

