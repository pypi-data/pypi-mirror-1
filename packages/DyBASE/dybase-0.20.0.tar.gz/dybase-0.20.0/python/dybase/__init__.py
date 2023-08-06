# -*- coding: utf-8 -*-

"""DYBASE API

This modules contains Python API to very simple OODBS for languages with dynamic type checking - dybase.
"""

import _dybase as dybaseapi
import weakref
import new
import sys
import threading

class Persistent:
    """Base class for all persistent capable objects.

    It is not required to derive all peristent
    capable objects from Persistent class, but in this case you will have to invoke store/load methods of the Storage class
    """

    def load(self):
        """If object is in raw state than load object from the storage"""
        if hasattr(self, '__storage__'):
            self.__storage__.loadObject(self)

    def isLoaded(self):
        """Check if object is already loaded or explicit invocation of load() method is required"""
        return not hasattr(self, '__raw__')

    def isPersistent(self):
        """Check if object is persistent (assigned persistent OID)"""
        return hasattr(self, '__oid__') and self.__oid__ != 0

    def isModified(self):
        """Check if object was modified during current transaction"""
        return hasattr(self, '__dirty__')

    def modify(self):
        """Mark object as modified. This object will be automatically stored to the database
           during transaction commit"""
        if hasattr(self, '__storage__'):
            self.__storage__.modifyObject(self)

    def store(self):
        """If object is not yet persistent, then make it persistent and store in the storage"""
        if hasattr(self, '__storage__'):
            self.__storage__.storeObject(self)

    def getStorage(self):
        """Get storage in which object is stored, None if object is not yet persistent"""
        if hasattr(self, '__storage__'):
            return self.__storage__
        else:
            return None

    def deallocate(self):
        """Remove object from the storage"""
        if hasattr(self, '__storage__'):
            self.__storage__.deallocateObject(self)
            delattr(self, '__storage__')

    def sharedLock(self, nowait=False):
        """Lock object in shared mode"""
        if hasattr(self, '__storage__'):
            self.__storage__.sharedLock(self, nowait)

    def exclusiveLock(self, nowait=False):
        """Lock object in exclusive mode"""
        if hasattr(self, '__storage__'):
            self.__storage__.exclusiveLock(self, nowait)

    def unlock(self):
        """Unlock object"""
        self.__storage__.unlock(self)

    def __init__(self, oid):
        """Constructor used by the database to create stub object"""
        self.__oid__ = oid

    def __eq__(a, b):
        if hasattr(b, '__target_oid__'):
            return b == a;
        return id(a) == id(b)

    def __ne__(a, b):
        return not (a == b)


class IndexIterator:
    """Iterator for object index. It can be used to iterate through all members
       of index in key acending order"""

    def __iter__(self):
        """return itdself to be able to use iterator in for constrcution"""
        return self

    def next(self):
        """Get next object in the index in key ascendin order.
           Returns None if there are no more object.
        """
        oid = dybaseapi.iteratornext(self.iterator)
        if oid == 0:
            raise StopIteration
        self.storage.lock.acquire()
        obj = self.storage._lookupObject(oid)
        self.storage.lock.release()
        return obj

    def __init__(self, storage, iterator):
        self.storage = storage
        self.iterator = iterator

    def __del__(self):
         dybaseapi.freeiterator(self.iterator)


class Index(Persistent):
    """ Indexed collection of persistent object
    This collection is implemented using B+Tree
    """

    def __init__(self, db, index):
        """Constructor used by the database"""
        self.index  = index
        db.makeObjectPersistent(self)

    def drop(self):
        """Delete index"""
        dybaseapi.dropindex(self.__storage__.db, self.index)

    def clear(self):
        """Remove all entries from the index"""
        dybaseapi.clearindex(self.__storage__.db, self.index)

    def insert(self, key, value):
        """Insert new object in the index"""
        self.__storage__.makeObjectPersistent(value)
        return dybaseapi.insertinindex(self.__storage__.db, self.index, key, value.__oid__, False)

    def set(self, key, value):
        """Set object for the specified key, if such key already exists in the index,
           previous association of this key will be replaced"""
        self.__storage__.makeObjectPersistent(value)
        return dybaseapi.insertinindex(self.__storage__.db, self.index, key, value.__oid__, True)


    def remove(self, key, value = None):
        """Remove entry from the index. If index is unique, then value can be omitted"""
        if value == None:
            oid = 0
        else:
            oid = value.__oid__
        return dybaseapi.removefromindex(self.__storage__.db, self.index, key, oid)


    def get(self, key):
        """Find object in the index with specified key.

        If no key is found None is returned;
        If one entry is found then the object associated with this key is returned;
        Othersise list of selected object is returned"""
        result = self.find(key, True, key, True)
        if result != None and len(result) == 1:
            return result[0]
        return result


    def find(self, low = None, lowInclusive = True, high = None, highInclusive = True):
        """Find objects in the index with key belonging to the specified range.

        High and low paremeters can be assigned None value, in this case there is no
        correpondent boundary. Each boundary can be exclusive or inclusive.

        Returns None if no object is found or list of selected objects
        """
        result = dybaseapi.searchindex(self.__storage__.db, self.index, low, lowInclusive, high, highInclusive)
        if result != None:
            self.__storage__.lock.acquire()
            for i in range(0, len(result)):
                result[i] = self.__storage__._lookupObject(result[i])
            self.__storage__.lock.release()
        return result

    def __iter__(self):
        """ Get index iterator. Interator can be used to traverse al indexed object in key ascending order."""
        return self.iterator()

    def iterator(self, low = None, lowInclusive = True, high = None, highInclusive = True, ascent = True):
        """Get selection iterator.

        Iterator can be used to iterate through obejct with key belonging to the specified range.
        High and low paremeters can be assigned None value, in this case there is no
        correpondent boundary. Each boundary can be exclusive or inclusive.
        Ascent parameter specifies traverse direction (key asending order if True)
        """
        iterator = dybaseapi.createiterator(self.__storage__.db, self.index, low, lowInclusive, high, highInclusive, ascent)
        return IndexIterator(self.__storage__, iterator)


class PersistentDelegator:
  def __getattr__(self, name):
    if self.__target__ == None:
       self.__dict__['__target__'] = self.__target_db__._loadTarget(self.__target_oid__)
    return getattr(self.__target__, name)

  def __setattr__(self, name, value):
    if self.__target__ == None:
       self.__dict__['__target__'] = self.__target_db__._loadTarget(self.__target_oid__)
    self.__target__.modify()
    return setattr(self.__target__, name, value)

  def __init__(self, db, oid):
    self.__dict__['__target__'] = None
    self.__dict__['__target_db__'] = db
    self.__dict__['__target_oid__'] = oid

  def __eq__(a, b):
    if hasattr(b, '__target_oid__'):
        return a.__target_oid__ == b.__target_oid__
    if hasattr(b, '__oid__'):
        return a.__target_oid__ == b.__oid__
    return False

  def __ne__(a, b):
    return not (a == b)


class Storage:
    """Main dybase API class"""

    def __init__(self, pagePoolSize = 4*1024*1024, objectCacheSize = 1000, useDelegators = False):
        """Constructor of the storage

        pagePoolSize    - size of database page pool in bytes (larger page pool ussually leads to better performance)
        objectCacheSize - size of obejct cache (number of objects)
        """
        self.pagePoolSize = pagePoolSize
        self.objectCacheSize = objectCacheSize
        self.useDelegators = useDelegators

    def open(self, path):
        """Open database

        Returns True if database wqas successully open, False otherwise
        """
        self.db = dybaseapi.open(path, self.pagePoolSize)
        if self.db != None:
            self.objectCacheUsed = 0
            self.objByOidMap = weakref.WeakValueDictionary()
            self.__next__ = self
            self.__prev__ = self
            self.lock = threading.Lock()
            self.modifiedList = []
            self.cv = threading.Condition()
            return True
        else:
            return False

    def close(self):
        """Close the storage:"""
        self.__next__ = None
        self.__prev__ = None
        dybaseapi.close(self.db)

    def commit(self):
        """Commit current transaction"""
        for obj in self.modifiedList:
             self.storeObject(obj)
        self.modifiedList = []
        dybaseapi.commit(self.db)

    def rollback(self):
        """Rollback current transaction"""
        self.modifiedList = []
        dybaseapi.rollback(self.db)
        self.objByOidMap.clear()

    def getRootObject(self):
        """Get storage root object (None if root was not yet specified)"""
        self.lock.acquire()
        obj = self._lookupObject(dybaseapi.getroot(self.db))
        self.lock.release()
        return obj

    def setRootObject(self, root):
        """Specify new storage root object"""
        self.makeObjectPersistent(root)
        dybaseapi.setroot(self.db, root.__oid__)

    def deallocateObject(self, obj):
        """Deallocate object from the storage"""
        if hasattr(obj, '__oid__'):
            del self.objByOidMap[obj.__oid__]
            dybaseapi.deallocate(self.db, obj.__oid__)
            delattr(obj, '__oid__')

    def makeObjectPersistent(self, obj):
        """Make object peristent (assign OID to the object)"""
        if not hasattr(obj, '__oid__'):
            self.storeObject(obj)

    def modifyObject(self, obj):
        """Mark object as modified. This object will be automaticaly stored to the database
           during transaction commit"""
        self.lock.acquire()
        if not(hasattr(obj, '__dirty__') and obj.__dirty__):
            obj.__dirty__ = True
            self.modifiedList.append(obj)
        self.lock.release()

    def storeObject(self, obj):
        """Make object persistent (if it is not yet peristent) and save it to the storage"""
        if hasattr(obj, '__dirty__'):
            obj.__dirty__ = False
        if not hasattr(obj, '__oid__'):
            obj.__oid__ = dybaseapi.allocate(self.db)
            obj.__storage__ = self
            self.objByOidMap[obj.__oid__] = obj
            self._insertInCache(obj)
        hnd = dybaseapi.beginstore(self.db, obj.__oid__, self._getFullClassName(obj))
        if obj.__class__ == Index:
            dybaseapi.storereffield(hnd, 'index', obj.index)
        else:
            for field, value in vars(obj).items():
                if field.endswith('_'):
                    continue
                if isinstance(value, int) or isinstance(value, long) or isinstance(value, float) or isinstance(value, str):
                    dybaseapi.storefield(hnd, field, value)
                elif isinstance(value, list) or isinstance(value, tuple):
                    dybaseapi.storefield(hnd, field, value)
                    for e in value:
                        self._storeElement(hnd, e)
                elif isinstance(value, dict):
                    dybaseapi.storefield(hnd, field, value)
                    for e in value.iteritems():
                        self._storeElement(hnd, e[0])
                        self._storeElement(hnd, e[1])
                elif value == None:
                    dybaseapi.storereffield(hnd, field, 0)
                else:
                    if not hasattr(value, '__oid__'):
                        self.storeObject(value)
                    dybaseapi.storereffield(hnd, field, value.__oid__)
        dybaseapi.endstore(hnd)

    def createIndex(self, type, unique = True):
        """Create index with specified type"""
        if type == int:
           createIntIndex(self, unique)
        elif type == long:
           createLongIndex(self, unique)
        elif type == str:
           createStrIndex(self, unique)
        elif type == float:
           createRealIndex(self, unique)
        else:
           none

    def createStrIndex(self, unique = True):
        """Create index for keys of string type"""
        return Index(self, dybaseapi.createstrindex(self.db, unique))

    def createIntIndex(self, unique = True):
        """Create index for keys of int type"""
        return Index(self, dybaseapi.createintindex(self.db, unique))

    def createLongIndex(self, unique = True):
        """Create index for keys of long type"""
        return Index(self, dybaseapi.createlongindex(self.db, unique))

    def createRealIndex(self, unique = True):
        """Create index for keys of float type"""
        return Index(self, dybaseapi.createrealindex(self.db, unique))

    def loadObject(self, obj):
        """Resolve references in raw object"""
        self.lock.acquire()
        if hasattr(obj, '__raw__'):
            for field, value in vars(obj).items():
                if value.__class__ == Persistent:
                    setattr(obj, field, self._lookupObject(value.__oid__, False))
                elif isinstance(value, list) or isinstance(value, tuple):
                    self._loadSequence(value)
                elif isinstance(value, dict):
                    self._loadDictionary(value)
            if hasattr(obj, 'onLoad'):
                obj.onLoad()
            delattr(obj, '__raw__')
        self.lock.release()

    def gc(self):
        """Start garbage collection"""
        dybaseapi.gc(self.db)

    def setGcThreshold(self, threshold):
        """Set garbage collection threshold"""
        dybaseapi.setgcthreshold(self.db, threshold)

    def exclusiveLock(self, obj, nowait=False):
        """Lock object in exclusive mode"""
        result = True
        currThread = threading.currentThread()
        self.cv.acquire()
        while True:
            if hasattr(obj, '__owner__') and obj.__owner__ == currThread:
                obj.__nwriters__ = obj.__nwriters__ + 1
                break
            elif (not hasattr(obj, '__nreaders__') or obj.__nreaders__ == 0) \
                and (not hasattr(obj, '__nwriters__') or obj.__nwriters__ == 0):
                    obj.__nwriters__ = 1
                    obj.__owner__ = currThread
                    break
            else:
                if nowait:
                    result = False
                    break
                self.cv.wait()
        self.cv.release()
        return result

    def sharedLock(self, obj, nowait=False):
        """Lock object in shared mode"""
        result = True
        currThread = threading.currentThread()
        self.cv.acquire()
        while True:
            if hasattr(obj, '__owner__') and obj.__owner__ == currThread:
                obj.__nwriters__  = obj.__nwriters__ + 1
                break
            elif not hasattr(obj, '__nwriters__') or obj.__nwriters__ == 0:
                if not hasattr(obj, '__nreaders__'):
                    obj.__nreaders__ = 1
                else:
                    obj.__nreaders__ = obj.__nreaders__ + 1
                break
            else:
                if nowait:
                    result = False
                    break
                self.cv.wait()
        self.cv.release()
        return result

    def unlock(self, obj):
        """Release granted lock"""
        self.cv.acquire()
        if hasattr(obj, '__nwriters__') and obj.__nwriters__ != 0:
            obj.__nwriters__ = obj.__nwriters__ - 1
            if obj.__nwriters__ == 0:
                obj.__owner__ = None
                self.cv.notifyAll()
        else:
            obj.__nreaders__ = obj.__nreaders__ - 1
            if obj.__nreaders__ == 0:
                self.cv.notifyAll()
        self.cv.release()

    def _getFullClassName(self, obj):
        return obj.__class__.__module__ + '.' + obj.__class__.__name__

    def _loadSequence(self, seq):
        for i in range(0, len(seq)):
            elem = seq[i]
            if elem.__class__ == Persistent:
                value[i] = self._lookupObject(elem.__oid__, False)
            elif isinstance(elem, list) or isinstance(elem, tuple):
                self._loadSequence(elem)
            elif isinstance(elem, dict):
                self._loadDictionary(elem)

    def _loadDictionary(self, d):
        for e in d.iteritems():
            key = e[0]
            value = e[1]
            if key.__class__ == Persistent:
                del d[key]
                key = self._lookupObject(key.__oid__, False)
                d[key] = value
            elif isinstance(key, list) or isinstance(key, tuple):
                self._loadSequence(key)
            elif isinstance(key, dict):
                self._loadDictionary(key)

            if value.__class__ == Persistent:
                d[key] = self._lookupObject(value.__oid__, False)
            elif isinstance(value, list) or isinstance(value, tuple):
                self._loadSequence(value)
            elif isinstance(value, dict):
                self._loadDictionary(value)

    def _removeFromCache(self, obj):
        if obj.__next__ != None:
            obj.__prev__.__next__ = obj.__next__
            obj.__next__.__prev__ = obj.__prev__
            obj.__next__ = None
            obj.__prev__ = None
            self.objectCacheUsed = self.objectCacheUsed - 1

    def _insertInCache(self, obj):
        if self.objectCacheUsed >= self.objectCacheSize:
            self._removeFromCache(self.__prev__)
        obj.__next__ = self.__next__
        obj.__prev__ = self
        self.__next__.__prev__ = obj
        self.__next__ = obj
        self.objectCacheUsed = self.objectCacheUsed + 1

    def _fetchComponent(self, hnd, recursive):
        oid = dybaseapi.getref(hnd)
        if oid == None:
            len = dybaseapi.arraylength(hnd)
            if len == None:
                len = dybaseapi.dictlength(hnd)
                if len == None:
                    value = dybaseapi.getvalue(hnd)
                else:
                    value = self._fetchDictionary(hnd, len, recursive)
            else:
                value = self._fetchSequence(hnd, len, recursive)
        elif oid == 0:
            value = None
        elif recursive:
            value = self._lookupObject(oid, False)
        else:
            value = self.objByOidMap.get(oid)
            if value == None:
                value = Persistent(oid)
        return value

    def _loadTarget(self, oid):
        self.lock.acquire()
        obj = self.objByOidMap.get(oid)
        if obj == None:
            hnd = dybaseapi.beginload(self.db, oid)
            obj = self._createInstance(dybaseapi.getclassname(hnd))
            obj.__oid__ = oid
            self.objByOidMap[oid] = obj
            obj.__storage__ = self
            self._insertInCache(obj)
            if obj.__class__ == Index:
                dybaseapi.nextfield(hnd)
                obj.index = dybaseapi.getref(hnd)
                dybaseapi.nextfield(hnd)
            else:
                while True:
                    fieldName = dybaseapi.nextfield(hnd)
                    if fieldName == None:
                         break
                    setattr(obj, fieldName, self._fetchComponent(hnd, True))
                if hasattr(obj, 'onLoad'):
                    obj.onLoad()
        else:
            self._removeFromCache(obj)
            self._insertInCache(obj)
        self.lock.release()
        return obj

    def _lookupObject(self, oid, recursive=True):
        if oid == 0:
            return None
        if self.useDelegators:
            return PersistentDelegator(self, oid)
        obj = self.objByOidMap.get(oid)
        if obj == None:
            hnd = dybaseapi.beginload(self.db, oid)
            obj = self._createInstance(dybaseapi.getclassname(hnd))
            obj.__oid__ = oid
            if not recursive:
                if not hasattr(obj, '__nonrecursive__'):
                    recursive = True
                else:
                    obj.__raw__ = True
            self.objByOidMap[oid] = obj
            obj.__storage__ = self
            self._insertInCache(obj)
            if obj.__class__ == Index:
                dybaseapi.nextfield(hnd)
                obj.index = dybaseapi.getref(hnd)
                dybaseapi.nextfield(hnd)
            else:
                while True:
                    fieldName = dybaseapi.nextfield(hnd)
                    if fieldName == None:
                         break
                    setattr(obj, fieldName, self._fetchComponent(hnd, recursive))
                if recursive and hasattr(obj, 'onLoad'):
                    obj.onLoad()
        else:
            if recursive and hasattr(obj, '__raw__'):
                self.loadObject(obj)
            self._removeFromCache(obj)
            self._insertInCache(obj)
        return obj

    def _fetchSequence(self, hnd, length, recursive):
        seq = []
        for i in range(0, length):
            dybaseapi.nextelem(hnd)
            seq.append(self._fetchComponent(hnd, recursive))
        return seq

    def _fetchDictionary(self, hnd, length, recursive):
        d = {}
        for i in range(0, length):
            dybaseapi.nextelem(hnd)
            key = self._fetchComponent(hnd, recursive)
            dybaseapi.nextelem(hnd)
            value = self._fetchComponent(hnd, recursive)
            d[key] = value
        return d

    def _createInstance(self, fullClassName):
        suf = fullClassName.rindex('.')
        moduleName = fullClassName[0:suf]
        className = fullClassName[suf+1:]
        module = sys.modules.get(moduleName)
        if module == None:
           module = __import__(moduleName)
        cls = module.__dict__[className]
        return new.instance(cls)

    def _storeElement(self, hnd, elem):
        if isinstance(elem, int) or isinstance(elem, long) or isinstance(elem, float) or isinstance(elem, str):
             dybaseapi.storeelem(hnd, elem)
        elif isinstance(elem, list) or isinstance(elem, tuple):
             dybaseapi.storeelem(hnd, elem)
             for e in elem:
                 self._storeElement(hnd, e)
        elif isinstance(elem, dict):
             dybaseapi.storeelem(hnd, elem)
             for e in elem.iteritems():
                 self._storeElement(hnd, e[0])
                 self._storeElement(hnd, e[1])
        elif elem == None:
             dybaseapi.storerefelem(hnd, 0)
        else:
             if not hasattr(elem, '__oid__'):
                 self.storeObject(elem)
             dybaseapi.storerefelem(hnd, elem.__oid__)
