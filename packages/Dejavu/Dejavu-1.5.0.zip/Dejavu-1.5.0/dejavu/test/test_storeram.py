
SM_class = "ram"


def run():
    import zoo_fixture
    # Isolate schema changes from one test to the next.
    reload(zoo_fixture)
    zoo_fixture.init()
    zoo_fixture.run(SM_class, {})


if __name__ == "__main__":
    run()
