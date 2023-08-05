"""Test the Filesystem Folder Storage Manager for dejavu."""

import os

opts = {u'root': os.path.join(os.path.dirname(__file__), "testdb", "fsroot"),
        'Exhibit.Name': '.mp3'}
SM_class = "folders"

def run():
    import zoo_fixture
    # Isolate schema changes from one test to the next.
    reload(zoo_fixture)
    zoo_fixture.init()
    zoo_fixture.run(SM_class, opts)


if __name__ == "__main__":
    run()
