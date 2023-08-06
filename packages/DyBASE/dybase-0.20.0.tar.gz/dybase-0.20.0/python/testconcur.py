"""Test of concurrent execution and locking
"""
import dybase
import threading

class L2List(dybase.Persistent):
    def __init__(self):
        self.head = L2Elem(0)

class L2Elem(dybase.Persistent):
    def __init__(self, count):
        self.next = self
        self.prev = self
        self.count = count

    def __nonrecursive__(self):
        True        

    def unlink(self):
        self.next.prev = self.prev
        self.prev.next = self.next
        self.next.store()
        self.prev.store()

    def linkAfter(self, elem):         
        elem.next.prev = self
        self.next = elem.next
        elem.next = self
        self.prev = elem
        self.store()
        self.next.store()
        self.prev.store()


nElements = 100000
nIterations = 100
nThreads = 4

db = dybase.Storage()

def run():
    list = db.getRootObject()
    for i in range(0, nIterations): 
        sum = 0
        n = 0
        list.sharedLock()
        head = list.head 
        elem = head
        while True: 
            elem.load()
            sum += elem.count
            n += 1
            elem = elem.next
            if elem == head:
                break
        assert n == nElements and sum == nElements*(nElements-1)/2
        list.unlock()
        list.exclusiveLock()
        last = list.head.prev
        last.unlink()
        last.linkAfter(list.head)
        list.unlock()
        


if db.open("testconcur.dbs"):
    list = db.getRootObject()
    if list == None:
        list = L2List()
        db.setRootObject(list)
        for i in range(1, nElements):
            elem = L2Elem(i)
            elem.linkAfter(list.head) 
    threads = []
    for i in (0, nThreads): 
        thread = threading.Thread(target = run)
        thread.start()
        threads.append(thread)
    for thread in threads: 
        thread.join()
    db.close()


