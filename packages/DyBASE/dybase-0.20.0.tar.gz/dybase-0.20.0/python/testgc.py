"""Test of dybase garbage collector
"""
import dybase

class PObject(dybase.Persistent):
    def __init__(self, key):
        self.strKey = str(key)
        self.longKey = key

class StorageRoot(dybase.Persistent):
    def __init__(self, db):
        self.strIndex = db.createStrIndex(True)
        self.longIndex = db.createLongIndex(True)

nObjectsInTree = 10000
nIterations = 100000

db = dybase.Storage()

if db.open("testgcx.dbs"):
    db.setGcThreshold(1000000)
    root = StorageRoot(db)
    db.setRootObject(root)
    longIndex = root.longIndex
    strIndex = root.strIndex
    insKey = 1999L
    remKey = 1999L
    for i in range(0, nIterations):
        if i > nObjectsInTree:
            remKey = (3141592621L*remKey + 2718281829L) % 1000000007L
            removed = longIndex.remove(remKey)                
            assert removed
            removed = strIndex.remove(str(remKey))
            assert removed
        insKey = (3141592621L*insKey + 2718281829L) % 1000000007L
        obj = PObject(insKey)
        obj.next = PObject(0)
        longIndex.insert(obj.longKey, obj)
        strIndex.insert(obj.strKey, obj)
        if i > 0:
            assert root.list.longKey == i-1
        root.list = PObject(i)
        root.store()
        if i % 1000 == 0: 
            db.commit()
    db.close()
