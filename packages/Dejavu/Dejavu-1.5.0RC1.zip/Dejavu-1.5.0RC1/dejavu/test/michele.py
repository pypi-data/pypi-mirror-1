import dejavu
 
class People(dejavu.Unit):
    name = dejavu.UnitProperty(unicode)
    age = dejavu.UnitProperty(int)
 
    def __str__(self):
        return "Hi, I'm %s and I'm %s years old" % (self.name, self.age)
 
arena = dejavu.Arena()
store = arena.add_store("main", "psycopg",
                        {'Connect': ("host=localhost dbname=test "
                                     "user=postgres password=djvpg")})
store.auto_discover = False


def main():
    try:
        store.create_database()
        for cls in (People, ):
            arena.register(cls)
            arena.create_storage(cls)
        arena.map_all()
    finally:
        store.drop_database()


import pyconquer
pyconquer.log(main, "michele.log")
