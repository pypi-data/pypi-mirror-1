"""Test of dybase indices
This test can be also used for measuring DYBASE perfrormance
"""

import dybase
import time

class Record(dybase.Persistent): 
    def __init__(self, key):
        self.strKey = str(key)
        self.longKey = key


class Root(dybase.Persistent):
    def __init__(self, db):
        self.strIndex = db.createStrIndex(True)
        self.longIndex = db.createLongIndex(True)

nRecords = 100000
pagePoolSize = 32*1024*1024

db = dybase.Storage(pagePoolSize)

if db.open("testidx.dbs"):
    root = db.getRootObject()
    if root == None:
        root = Root(db)
        db.setRootObject(root)
    longIndex = root.longIndex
    strIndex = root.strIndex
    start = time.time()
    key = 1999L
    for i in range(0,nRecords):
        key = (3141592621L*key + 2718281829L) % 1000000007L
        rec = Record(key)
        inserted = longIndex.insert(rec.longKey, rec)
        assert inserted
        inserted = strIndex.insert(rec.strKey, rec)                
        assert inserted

    db.commit()
    print 'Elapsed time for inserting ', nRecords, ' records: ', time.time() - start, ' seconds'
        
    start = time.time()
    key = 1999L
    for i in range(0,nRecords):
        key = (3141592621L*key + 2718281829L) % 1000000007L
        rec1 = longIndex.get(key)
        rec2 = strIndex.get(str(key))
        assert rec1 != None and rec1 == rec2 and rec1.longKey == key

    print 'Elapsed time for performing ', nRecords*2, ' index searches: ', time.time() - start,  ' seconds'
        
    start = time.time()
    key = -1L
    i = 0
    for rec in longIndex:
        assert key < rec.longKey
        key = rec.longKey
        i = i + 1
    assert i == nRecords
    key = ''
    i = 0
    for rec in strIndex:
        assert key < rec.strKey
        key = rec.strKey
        i = i + 1
    assert i == nRecords
    print 'Elapsed time for iterating through  ', nRecords*2, ' records: ', time.time() - start,  ' seconds'


    start = time.time()
    key = 1999L
    for i in range(0,nRecords):
        key = (3141592621L*key + 2718281829L) % 1000000007L
        rec = longIndex.get(key)
        removed = longIndex.remove(key)
        assert removed
        removed = strIndex.remove(str(key), rec)
        assert removed
        rec.deallocate()

    print 'Elapsed time for deleting ', nRecords, ' records: ', time.time() - start,  ' seconds'
    assert len(tuple(longIndex.iterator())) == 0
    db.close()
