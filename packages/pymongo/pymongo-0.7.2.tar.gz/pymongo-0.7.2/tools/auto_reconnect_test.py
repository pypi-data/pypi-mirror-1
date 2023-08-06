import threading
import time

from pymongo.errors import ConnectionFailure
from pymongo.connection import Connection

db = Connection.paired(("localhost", 27018), pool_size=10).test
db.test.remove({})

class Something(threading.Thread):
    def run(self):
        while True:
            time.sleep(10)
            try:
                id = db.test.save({"x": 1})
                assert db.test.find_one(id)["x"] == 1
                db.test.remove(id)
                db.connection().end_request()
                print "Y"
            except ConnectionFailure, e:
                print e
                print "N"

for _ in range(1):
    t = Something()
    t.start()
    time.sleep(1)
