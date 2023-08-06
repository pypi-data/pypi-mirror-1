#!/usr/local/bin/ruby


USE_WEAK_REFERENCES = false
USE_DELEGATOR = false

require "dybaseapi"
require "thread"
require "delegate"
require "weakref"

include Dybaseapi


=begin
= DYBASE API
  This modules contains Python API to very simple OODBS for languages with dynamic type checking - dybase.
=end
module Dybase

=begin    
== Base class for all persistent capable objects. 
   It is not required to derive all peristent
   capable objects from Persistent class, but in this case you will have to invoke store/load methods of the Storage class
=end
class Persistent 

=begin
=== If object is in raw state than load object from the storage
=end
    def load
        if @__storage__ != nil
            @__storage__.loadObject(self)
        end
    end

=begin
=== Check if object is already loaded or explicit invocation of load() method is required
=end
    def isLoaded
        not @__raw__
    end
       
=begin
=== Check if object is persistent (assigned persistent OID)
=end
    def isPersistent
        @__oid__ != nil
    end

=begin
=== Check if object was modified during current transaction
=end
    def isModified
        return @__dirty__ == true
    end    

       
=begin
=== Mark object as modified. This object will be automaticaly stored to the database
    during transaction commit
=end
    def modify
        if @__storage__ != nil and not @__dirty__
            @__storage__.modifyObject(self)
        end
    end


=begin
=== If object is not yet persistent, then make it persistent and store in the storage
=end
    def store
        if @__storage__ != nil
            @__storage__.storeObject(self)
        end
    end
       

=begin
=== Get storage in which object is stored, nil if object is not yet persistent
=end
    def storage
        @__storage__
    end

=begin
=== Remove object from the storage
=end
    def deallocate
        if @__storage__ != nil
            @__storage__.deallocateObject(self)
            @__storage__ = nil
        end
    end

=begin
=== Method invoked after loading of the object from the storage
=end
    def onLoad
    end

=begin
=== Override this methofd if you want to rphibit implicit loading of all objects referenced from this object
=end
    def recursiveLoading
        return true
    end

=begin
=== Lock object in shared mode
=end
    def sharedLock(nowait=false)
        if @__storage__ != nil
            @__storage__.sharedLock(self, nowait)
        end
    end
        
=begin
=== Lock object in exclusive mode
=end
    def exclusiveLock(nowait=false)
        if @__storage__ != nil
            @__storage__.exclusiveLock(self, nowait)
        end
    end
        
=begin
=== Unlock object
=end
    def unlock()
        @__storage__.unlock(self)
    end

  attr_writer :__storage__, :__oid__, :__raw__, :__dirty__, :__nreaders__, :__nwriters__, :__owner__;
  attr_reader :__storage__, :__oid__, :__raw__, :__dirty__, :__nreaders__, :__nwriters__, :__owner__;
end

=begin
== Indexed collection of persistent object        
   This collection is implemented using B+Tree
=end 
class Index<Persistent
    def initialize(index = 0)
        @index = index
    end

=begin
=== Delete index
=end
    def drop
        @__storage__._getImpl.dropindex(@index)
    end
    
=begin
=== Remove all entries from the index
=end
    def clear
        @__storage__._getImpl.clearindex(@index)
    end
    
=begin
=== Insert new entry in the index
=end
    def insert(key, value)
        @__storage__.makeObjectPersistent(value)
        @__storage__._getImpl.insertinindex(@index, key, value.__oid__, false)
    end

=begin
=== Set object for the specified key, if such key already exists in the index, 
    previous association of this key will be replaced
=end
    def set(key, value)
        @__storage__.makeObjectPersistent(value)
        @__storage__._getImpl.insertinindex(@index, key, value.__oid__, true)
    end

=begin
=== Remove entry from the index. If index is unique, then value can be omitted
=end
    def remove(key, value = nil)
        if value == nil
            oid = 0
        else
            oid = value.__oid__
        end
        @__storage__._getImpl.removefromindex(@index, key, oid)
    end

=begin
=== Find object in the index with specified key. 
        
    If no key is found nil is returned;
    If one entry is found then the object associated with this key is returned;
    Othersise list of selected object is returned
=end
    def get(key)
        result = find(key, true, key, true)        
	if result != nil and result.length == 1
            result = result[0]
        end
        result
    end

=begin
=== Find objects in the index with key belonging to the specified range.

    high and low paremeters can be assigned nil value, in this case there is no
    correpondent boundary. Each boundary can be exclusive or inclusive.  
        
    Returns nil if no object is found or list of selected objects
=end
    def find(low = nil, lowInclusive = true, high = nil, highInclusive = true)
        result = @__storage__._getImpl.searchindex(@index, low, lowInclusive, high, highInclusive)
        if result != nil 
            @__storage__.mutex.synchronize {
                for i in 0...result.length
                    result[i] = @__storage__._lookupObject(result[i])
                end
            }
        end
        result
    end


=begin
=== Iterate through object in the index with key belonging to the specified range.
    High and low paremeters can be assigned None value, in this case there is no
    correpondent boundary. Each boundary can be exclusive or inclusive.  
    Ascent parameter specifies traverse direction (key asending order if True)        
=end
    def iterate(low = nil, lowInclusive = true, high = nil, highInclusive = true, ascent = true)
        iterator = Iterator.new(@__storage__._getImpl, @index, low, lowInclusive, high, highInclusive, ascent)
        while true
            oid = iterator.next
            if oid != 0
                yield @__storage__._lookupObject(oid)
            else
                break
            end
        end
    end
end


=begin
== Persistent delegator class
=end
class PersistentDelegator<Delegator
  def __getobj__
      if @obj.__raw__
          @obj.load()
      end
      return @obj
  end

  def initialize(obj) 
      super
      @obj = obj
  end
end



=begin
== Main dybase API class
=end
class Storage
=begin
=== Constructor of the storage
        
====    pagePoolSize    - size of database page pool in bytes (larger page pool ussually leads to better performance)
====    objectCacheSize - size of obejct cache (number of objects)
=end                     
    def initialize(pagePoolSize = 4194304, objectCacheSize = 1000)
        @pagePoolSize = pagePoolSize
        @objectCacheSize = objectCacheSize
    end


=begin
=== Open the storage
=end
    def open(path)
        @db = StorageImpl.new(path, @pagePoolSize)
        @objectCacheUsed = 0
        @objByOidMap = Hash.new
        @modifiedList = []
        @mutex = Mutex.new
        @cvMutex = Mutex.new
        @cv = ConditionVariable.new
    end    

=begin
=== Close the storage
=end
    def close
        @db.close
    end

=begin
=== Commit current transaction
=end
    def commit
        for obj in @modifiedList
            storeObject(obj)
        end
        @modifiedList = []
        @db.commit
    end

=begin
=== Rollback current transaction
=end
    def rollback
        @modifiedList = []
        @db.rollback
        resetHash
    end

=begin
=== Get storage root object (nil if root was not yet specified)
=end
    def getRootObject
        @mutex.synchronize {
            _lookupObject(@db.getroot())
        }
    end

=begin
=== Specify new storage root object
=end
    def setRootObject(root)
        makeObjectPersistent(root)
        @db.setroot(root.__oid__)
    end
     
    
=begin
=== Deallocate object from the storage
=end
    def deallocateObject(obj)
        if obj.__oid__ != nil
            @objByOidMap.delete(obj.__oid__)
            @db.deallocate(obj.__oid__)
            obj.__oid__ = nil
        end
    end

=begin
=== Make object peristent (assign OID to the object)
=end
    def makeObjectPersistent(obj)
        if obj.__oid__ == nil
            storeObject(obj)
        end
        obj
    end

=begin
=== Mark object as modified. This object will be automaticaly stored to the database
    during transaction commit
=end
    def modifyObject(obj)
        @mutex.synchronize {
            if not obj.__dirty__
                obj.__dirty__ = true
                @modifiedList << obj
            end
        }
    end


=begin  
=== Make object persistent (if it is not yet peristent) and save it to the storage
=end
    def storeObject(obj)
        if obj.__oid__ == nil
            obj.__oid__ = @db.allocate
            obj.__storage__ = self
            _putInCache(obj.__oid__, obj)
        end
        obj.__dirty__ = false
        hnd = StoreHandle.new(@db, obj.__oid__, obj.class.to_s)
        if obj.class == Dybase::Index
            hnd.storereffield("@index", ivar_get(obj, "@index"))
        else
            vars = obj.instance_variables
            for var in vars
                if var[-1] != 95 # variable name terminated with '_' are treated as transient
    		value = ivar_get(obj, var)
                    type = value.class 
                    if type == Fixnum or type == Float or type == String or type == TrueClass or type == FalseClass
                        hnd.storefield(var, value)
                    elsif type == Array
                        hnd.storefield(var, value)
                        for e in value
                            _storeElement(hnd, e)
                        end
                    elsif type == Hash
                        hnd.storefield(var, value)
	                for key,val in value
			    _storeElement(hnd, key)
			    _storeElement(hnd, val)
			end
                    elsif value == nil
                        hnd.storereffield(var, 0)
                    else # persisten object
                        if value.__oid__ == nil
                            storeObject(value)
                        end
                        hnd.storereffield(var, value.__oid__)
                    end
                end
            end
        end
        hnd.endstore
    end
       
=begin  
=== Create index for keys of string type
=end
    def createStrIndex(unique = true)
        makeObjectPersistent(Index.new(@db.createstrindex(unique)))
    end

=begin  
=== Create index for keys of finxnum type
=end
    def createIntIndex(unique = true)
        makeObjectPersistent(Index.new(@db.createintindex(unique)))
    end

=begin  
=== Create index for keys of float type
=end
    def createFloatIndex(unique = true)
        makeObjectPersistent(Index.new(@db.createrealindex(unique)))
    end

=begin  
=== Create index for keys of bool type
=end
    def createBoolIndex(unique = true)
        makeObjectPersistent(Index.new(@db.createboolindex(unique)))
    end


=begin  
=== Resolve references in raw object
=end
    def loadObject(obj)
        @mutex.synchronize {
            if obj.__raw__       
                obj.__raw__ = false
                vars = obj.instance_variables
                for var in vars
                    value = ivar_get(obj, var)
                    if value.class == Dybase::Persistent
                        ivar_set(obj, var, _lookupObject(value.__oid__, false))
                    elsif value.class == Array
                        _loadArray(value)
                    elsif value.class == Hash
                        _loadHash(value)
                    end
                end
                obj.onLoad()
            end
        }
    end

    def _getImpl
        @db
    end

=begin  
=== Reset object hash. 
    Each fetched object is stored in objByOidMap hash table.
    It is needed to provide OID->instance mapping. Since placing object in hash increase its access counter, 
    such object can not be deallocated by garbage collector. So after some time all peristent objects from 
    the storage will be loaded to the memory. To solve the problem almost all languages with implicit
    memory deallocation (garbage collection) provides weak references. Ruby also supports weak references.
    The file dybase-weak.rb contains implementation of dybase API using weak refernces. 
    Unfortunataly using weak references adds very large memory overhead. 
    Without weak refences TestIndex apllication is able to handle 100000 object is few seconds, 
    with weak references - 10000 objects casuse terrible swapping at computer with 512Mb of RAM and
    so execution time tramatically inxreased. 
 
===  That is why by default I provide version of DYBASE API without weak references.        
     To prevent memory overflow you should use resetHash() method. 
     This method just clear hash table. After invocation of this method, you should not use any variable
     referening persistent objects. Instead you should invoke getRootObject method and access all other 
     persistent objects only through the root. 
=end
    def resetHash() 
        @objByOidMap.clear
    end       

=begin  
=== Start garbage collector
=end
    def gc() 
        @db.gc
    end       

=begin  
=== Set garbage collection threshold.
    By default garbage collection is disable (threshold is set to 0).
    If it is set to non zero value, GC will be started each time when
    delta between total size of allocated and deallocated objects exeeds specified threshold OR
    after reaching end of allocation bitmap in allocator. 

=== allocated_delta: delta between total size of allocated and deallocated object since last GC 
    or storage openning 
=end
    def setGcThreshold(threshold) 
        @db.setgcthreshold(threshold)
    end       


=begin  
=== Lock object in exclusive mode
=end
    def exclusiveLock(obj, nowait=false)
        result = true
        currThread = Thread.current
        @cvMutex.synchronize {
            while true
                if obj.__owner__ == currThread
                     obj.__nwriters__ += 1
                     break
                elsif obj.__nreaders__ == nil and obj.__nwriters__ == nil
                    obj.__nwriters__ = 1
                    obj.__owner__ = currThread
                    break
                else
                    if nowait
                        result = false
                        break
                    end
                    @cv.wait(@cvMutex)
                end
            end
        }
        return result
    end
      
=begin  
=== Lock object in shared mode
=end
    def sharedLock(obj, nowait=false)
        result = true
        currThread = Thread.current
        @cvMutex.synchronize {
            while true
                if obj.__owner__ == currThread
                    obj.__nwriters__ += 1
                    break
                elsif obj.__nwriters__ == nil
                    if obj.__nreaders__ == nil
                        obj.__nreaders__ = 1 
                    else
                        obj.__nreaders__ += 1
                    end
                    break
                else
                    if nowait
                        result = false
                        break
                    end
                    @cv.wait(@cvMutex)
                end
            end
        }                 
        return result
    end

=begin  
=== Release granted lock
=end
    def unlock(obj)
        @cvMutex.synchronize {
            if obj.__nwriters__ != nil
               if (obj.__nwriters__ -= 1) == 0
                   obj.__owner__ = nil
                   obj.__nwriters__ = nil
                   @cv.broadcast
               end
            else
               if (obj.__nreaders__ -= 1) == 0
                   obj.__nreaders__ = nil
                   @cv.broadcast
               end                
            end
        }
    end


    def _loadArray(arr)
        for i in 0...arr.length
            elem = arr[i]
            if elem.class == Dybase::Perisistent
                arr[i] = _lookupObject(elem.__oid__, false)
            elsif elem.class == Array
                _loadArray(elem)
            elsif elem.class == Hash
                _loadHash(elem)
            end
        end
    end

    def _loadHash(h)
    	copy = nil
        for key, value in h
            if key.class == Dybase::Perisistent
	        if copy == nil
		   copy = h.dup
		end
	        copy.delete(key)
                key = _lookupObject(key.__oid__, false)
		copy[key] = value
            elsif key.class == Array
                _loadArray(elem)
            elsif key.class == Hash
                _loadHash(elem)
            end

            if value.class == Dybase::Perisistent
                h[key] = _lookupObject(value.__oid__, false)
            elsif value.class == Array
                _loadArray(value)
            elsif value.class == Hash
                _loadHash(value)
            end
        end
	if copy != nil
	    h.replace(copy)
	end
    end

    def _putInCache(oid, obj)
        if USE_WEAK_REFERENCES
            @objByOidMap[oid] = WeakRef.new(obj)
        else
            @objByOidMap[oid] = obj
        end
    end
    
    def _findInCache(oid)
        if USE_WEAK_REFERENCES
            obj = nil
            begin 
    	        wref = @objByOidMap[oid]
                if wref != nil
                    if wref.weakref_alive?
                        obj = wref.__getobj__
                    else 
                        @objByOidMap[oid] = nil
                    end
                end
            rescue WeakRef::RefError
                @objByOidMap[oid] = nil
                obj = nil
            end
        else 
            obj = @objByOidMap[oid]
        end
        return obj
    end


    def _fetchComponent(hnd, recursive)
        oid = hnd.getref()
        if oid == nil
            len = hnd.arraylength()
            if len == nil
	        len = hnd.hashlength();
		if len == nil
		    value = hnd.getvalue()
		else 
		    value = _fetchHash(hnd, len, recursive)
		end
            else
                value = _fetchArray(hnd, len, recursive)
            end
        elsif oid == 0
            value = nil
        elsif recursive
            value = _lookupObject(oid, false)
        else
            value = _findInCache(oid)
            if value == nil
                 value = Persistent.new
    		 value.__oid__ = oid
            end
        end
	return value
    end

    def _lookupObject(oid, recursive=true)
        if oid == 0
            return nil
        end
        obj = _findInCache(oid)
        if obj == nil
            hnd = LoadHandle.new(@db, oid)
            obj = new_instance(hnd.getclassname)
            obj.__oid__ = oid
            if USE_DELEGATOR
                recursive = false
                obj.__raw__ = true
                proxy = PersistentDelegator.new(obj)
                _putInCache(oid, proxy)
            else 
                if not recursive 
                    if obj.recursiveLoading()
                        recursive = true
                    else
                        obj.__raw__ = true
                    end
                end
                _putInCache(oid, obj)
            end
            obj.__storage__ = self
            if obj.class == Dybase::Index
                fieldName = hnd.nextfield()
                ivar_set(obj, fieldName, hnd.getref())
                hnd.nextfield()
            else
                while true
                    fieldName = hnd.nextfield()
                    if fieldName == nil
                         break
                    end
                    ivar_set(obj, fieldName, _fetchComponent(hnd, recursive))
                end
                if recursive
                    obj.onLoad()
                end
            end
            if USE_DELEGATOR
                obj = proxy
            end
        else                
            if recursive and obj.__raw__ and not USE_DELEGATOR
                loadObject(obj)
            end
        end
        return obj
    end   

    def _fetchArray(hnd, length, recursive)
        arr = []
        for i in 0...length
            hnd.nextelem()
            arr << _fetchComponent(hnd, recursive)
        end
        return arr
    end

    def _fetchHash(hnd, length, recursive)
        h = {}
        for i in 0...length
            hnd.nextelem()
            key = _fetchComponent(hnd, recursive)
            hnd.nextelem()
            value = _fetchComponent(hnd, recursive)
	    h[key] = value;
        end
        return h
    end


    def _storeElement(hnd, elem)
        type = elem.class
        if type == Fixnum or type == Float or type == String or type == TrueClass or type == FalseClass
             hnd.storeelem(elem)
        elsif type == Array
             hnd.storeelem(elem)
             for e in elem
                 _storeElement(hnd, e)
             end
        elsif type == Hash
             hnd.storeelem(elem)
             for key,value in elem
                 _storeElement(hnd, key)
                 _storeElement(hnd, value)
             end
        elsif elem == nil
             hnd.storerefelem(0)
        else
             if elem.__oid__ == nil
                 storeObject(elem)
             end
             hnd.storerefelem(elem.__oid__)
        end
    end

    attr_reader :mutex;
end

end

