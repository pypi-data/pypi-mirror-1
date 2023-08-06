import random
import dybase
import time

class Root(dybase.Persistent):
    def __init__(self, db):
        self.longIndex = db.createLongIndex(True)

class DataObject(dybase.Persistent):
    def __init__(self, key):
        self.longKey = key

db = dybase.Storage()

if db.open("testperf.dbs"):
    root = db.getRootObject()
    if root == None:
        root = Root(db)
        db.setRootObject(root)
    longIndex = root.longIndex
    for i in range(500000):
        key = long(random.randint(0, 10000000))
        rec = DataObject(key)
        rec.data = str(i)
        longIndex.insert(rec.longKey, rec)
    db.commit()
    print "db.commit()"
    
    for i in range(500000):
        key = long(random.randint(0, 10000000))
        rec = longIndex.get(key)
        if rec:
            print "%s " % rec.data,
    print "Done"
