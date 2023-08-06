import time
import sys
sys.path[0:0] = [""]

from pymongo import Connection
from pymongo.errors import AutoReconnect

db = Connection.paired(("localhost", 27017), ("localhost", 27018)).pymongo_test

db.test.remove({})
for x in range(10):
    db.test.save({"x": x})

while True:
    try:
        assert db.test.count() == 10
        x = 0
        for doc in db.test.find():
            x += doc["x"]
        assert x == 45
        print ".",
        time.sleep(1)
    except AutoReconnect:
        time.sleep(1)
