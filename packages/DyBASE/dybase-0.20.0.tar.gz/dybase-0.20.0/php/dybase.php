<?php

$extname="dybaseapi";
if (!extension_loaded($extname)) {
    if (substr(PHP_OS, 0, 3) == 'WIN') {
        @dl("php_$extname.dll");
    } else {
        @dl("$extname.so");
    }
    if (!extension_loaded($extname)) {
        die("The extension '$extname' couldn't be found.\n");
    }
}


/**
  * Base class for all persistent capable objects. 
  * 
  * It is not required to derive all peristent
  * capable objects from Persistent class, but in this case you will have to invoke store/load methods of the Storage class
  */
class Persistent { 
    var $__raw__;
    var $__dirty__;
    var $__oid__;
    var $__storage__;
    
   /**
    * If object is in raw state than load object from the storage
    */
    function load() {
        if ($this->__raw__) {
            $this->__storage__->loadObject($this);
        }
    }

   /**
    *  Check if object is already loaded or explicit invocation of load() method is required
    */
    function isLoaded() { 
        return !$this->__raw__;
    }

   /**
    *  Check if object is persistent (assigned persistent OID)
    */
    function isPersistent() { 
        return $this->__oid__ != null;
    }

   /**
    * Check if object was modified during current transaction
    */
    function isModified() {
        return $this->__dirty__ != null;
    }

   /**
    * Mark object as modified. This object will be automaticaly stored to the database
    * during transaction commit
    */
    function modify() {
        if ($this->__storage__ != null && !$this->__dirty__) { 
           $this->__storage__->modifyObject($this);
        }
    }

   /**
    * If object is not yet persistent, then make it persistent and store in the storage
    */
    function store() { 
        if ($this->__storage__ != null) { 
            $this->__storage__->storeObject($this);
        }
    }   

   /**
    * Get storage in which object is stored, None if object is not yet persistent
    */
    function &getStorage() {
        return $this->__storage__;
    }

   /**
    * Remove object from the storage
    */
    function deallocate() {
        if ($this->__storage__ != null) {
            $this->__storage__->deallocateObject($this);
            unset($this->__storage__);
        }
    }

   /**
    * Override this method if you want to provibit implicit loading of all object referenced from this object
    */
    function recursiveLoading() {
        return true;
    }

   /**
    * Fuunction called after loading of the object from the storage
    */
    function onLoad() { 
    }    

    function Persistent($oid = null) { 
        $this->__oid__ = $oid;
        $this->__raw__ = false;
        $this->__storage__ = null;
    }
}


/**
 * Iterator for index. 
 * All objects in index will be traversed in key ascending order
 */
class IndexIterator {
    var $storage;
    var $iterator;

    function IndexIterator(&$storage, $index, $low=null, $lowInclusive=false, $high=null, $highInclusive=false, $ascent=true) { 
        $this->storage = &$storage;
        $this->iterator = dybase_createiterator($storage->db, $index, $low, $lowInclusive, $high, $highInclusive, $ascent);
    }

    function &next() { 
        return $this->storage->_lookupObject(dybase_iteratornext($this->iterator));
    }
        
    function close() {
        dybase_freeiterator($this->iterator);
    }
}

/**
 * Indexed collection of persistent object        
 * This collection is implemented using B+Tree
 */
class Index extends Persistent {
    var $index;

   /**
    * Delete index
    */
    function drop() {
        dybase_dropindex($this->__storage__->db, $this->index);
    }
    
   /**
    * Remove all entries from the index
    */
    function clear() {
        dybase_clearindex($this->__storage__->db, $this->index);
    }
    
   /** 
    * Insert new entry in the index
    */
    function insert($key, &$value) {
        $this->__storage__->makeObjectPersistent($value);
        return dybase_insertinindex($this->__storage__->db, $this->index, $key, $value->__oid__, false);
    }

   /** 
    * Set object for the specified key, if such key already exists in the index, 
    * previous association of this key will be replaced
    */
    function set($key, &$value) {
        $this->__storage__->makeObjectPersistent($value);
        dybase_insertinindex($this->__storage__->db, $this->index, $key, $value->__oid__, true);
    }

   /**
    * Remove entry from the index. If index is unique, then value can be omitted
    */
    function remove($key, $value = null) {        
        if ($value == null) { 
            $oid = 0;
        } else {
            $oid = $value->__oid__;
        }
        return dybase_removefromindex($this->__storage__->db, $this->index, $key, $oid);
    }

   /**
    * Find object in the index with specified key. 
    * If no key is found null is returned;
    * If one entry is found then the object associated with this key is returned;
    * Othersise list of selected object is returned
    */    
    function &get($key) {
        $result = &$this->find($key, true, $key, true);       
        if ($result != null and sizeof($result) == 1) {
            return $result[0];
        }
        return $result;
    }


   /**
    * Find objects in the index with key belonging to the specified range.
    * high and low paremeters can be assigned null value, in this case there is no
    * correpondent boundary. Each boundary can be exclusive or inclusive.  
    * Returns null if no object is found or list of selected objects
    */
    function &find($low = null, $lowInclusive = true, $high = null, $highInclusive = true) {
        $result = &dybase_searchindex($this->__storage__->db, $this->index, $low, $lowInclusive, $high, $highInclusive);
        if ($result != null) { 
            foreach ($result as $i=>$oid) { 
                $result[$i] = &$this->__storage__->_lookupObject($oid);
            }
        }
        return $result;
    }

    /**
     * Get iterator for key belonging to the specified range.
     * high and low paremeters can be assigned null value, in this case there is no
     * correpondent boundary. Each boundary can be exclusive or inclusive.  
     * Order of traversal is specified by ascent parameter
     */
    function &iterator($low = null, $lowInclusive = true, $high = null, $highInclusive = true, $ascent = true) 
    {
        return new IndexIterator($this->__storage__, $this->index, $low, $lowInclusive, $high, $highInclusive, $ascent);
    }
}

 
/**
 * Main dybase API class
 */
class Storage { 
    var $db;
    var $pagePoolSize;
    var $objByOidMap;

   /**
    * Constructor of the storage
    *    
    * @param pagePoolSize    size of database page pool in bytes (larger page pool ussually leads to better performance)
    */                      
    function Storage($pagePoolSize = 4194304) {
        $this->pagePoolSize = $pagePoolSize;
    }

   /**Open database
    *     
    * @return true if database was successully open, false otherwise
    */
    function open($path) {
        $this->db = dybase_open($path, $this->pagePoolSize);
        if ($this->db != 0) { 
            $this->objectCacheUsed = 0;
            $this->objByOidMap = array();
            $this->modifiedList = array();
            return true;
        } else {
            return false;
        }
    }

   /**
    * Close the storage
    */
    function close() {
        dybase_close($this->db);
    }

   /**
    * Commit current transaction
    */
    function commit() {
        for ($i = 0; $i < sizeof($this->modifiedList); $i++) {
             $this->storeObject($this->modifiedList[$i]);
        }
        $this->modifiedList = array();
        dybase_commit($this->db);
    }

   /**
    * Rollback current transaction
    */
    function rollback() {
        $this->modifiedList = array();
        dybase_rollback($this->db);
        resetHash();
    }

   /**
    * Get storage root object (null if root was not yet specified)
    */
    function &getRootObject() {
        return $this->_lookupObject(dybase_getroot($this->db));
    }

   /**
    * Specify new storage root object
    */
    function setRootObject(&$root) {
        $this->makeObjectPersistent($root);
        dybase_setroot($this->db, $root->__oid__);
    }

   /**     
    * Deallocate object from the storage
    */
    function deallocateObject(&$obj) {
        if ($obj->__oid__ != null) {
            unset($this->objByOidMap[$obj->__oid__]);             
            dybase_deallocate($this->db, $obj->__oid__);
            $obj->__oid__ = null;
        }
    }


   /**
    * Make object peristent (assign OID to the object)
    */
    function makeObjectPersistent(&$obj) {
        if ($obj->__oid__ == null) { 
            $this->storeObject($obj);
        }
    }

   /**
    * Mark object as modified. This object will be automaticaly stored to the database
    * during transaction commit
    */
    function modifyObject(&$obj) {
        $obj->__dirty__ = true;
        $this->modifiedList[] = &$obj;
    }

   /**
    * Make object persistent (if it is not yet peristent) and save it to the storage
    */
    function storeObject(&$obj) {
        if ($obj->__oid__ == null) { 
            $obj->__oid__ = dybase_allocate($this->db);
            $obj->__storage__ = &$this;
            $this->objByOidMap[$obj->__oid__] = &$obj;
        }
        $obj->__dirty__ = false;
        $hnd = dybase_beginstore($this->db, $obj->__oid__, get_class($obj));
        if (get_class($obj) == "Index") {
            dybase_storereffield($hnd, "index", $obj->index);
        } else { 
            foreach (get_object_vars($obj) as $field => $value) {
                if ($field[strlen($field)-1] == '_') {
                    continue;
                }       
                if (is_int($value) || is_float($value) || is_string($value)) { 
                    dybase_storefield($hnd, $field, $value);
                } else if (is_array($value)) {  
                    $arr = &$obj->$field;
                    dybase_storearrayfield($hnd, $field, sizeof($arr));
		    foreach ($arr as $key=>$value) { 
		        $this->_storeElement($hnd, $key);
                        $this->_storeElement($hnd, $value);
                    }
                } else if ($value == null) { 
                    dybase_storereffield($hnd, $field, 0);
                } else { 
                    if ($value->__oid__ == null) { 
                        $this->storeObject($obj->$field);
                    }
                    dybase_storereffield($hnd, $field, $obj->$field->__oid__);
                }
            }
        }
        dybase_endstore($hnd);             
    }

   /**
    * Create index for keys of string type
    */
    function &createStrIndex($unique = true) {
        $idx = &new Index();
        $idx->index = dybase_createstrindex($this->db, $unique);
        $this->storeObject($idx);
        return $idx;
    }


   /**
    * Create index for keys of int type
    */
    function &createIntIndex($unique = true) {
        $idx = &new Index();
        $idx->index = dybase_createintindex($this->db, $unique);
        $this->storeObject($idx);
        return $idx;
    }


   /**
    * Create index for keys of boolean type
    */
    function &createBoolIndex($unique = true) {
        $idx = &new Index();
        $idx->index = dybase_createboolindex($this->db, $unique);
        $this->storeObject($idx);
        return $idx;
    }

   /**
    * Create index for keys of float type
    */
    function &createRealIndex($unique = true) {
        $idx = &new Index();
        $idx->index = dybase_createlrealindex($this->db, $unique);
        $this->storeObject($idx);
        return $idx;
    }

   /**
    * Resolve references in raw object
    */
    function loadObject(&$obj) {
        $obj->__raw__ = false;
        foreach (get_obj_vars($obj) as $field => $value) {
            if (get_class($value) == "Persistent") {
                $obj->$field = &$this->_lookupObject($value->__oid__, false);
            } else if (is_array($value)) { 
                $this->_loadArray($obj->$field);
            }
        }
        $obj->onLoad();
    }

   /**
    * Reset object hash. Each fetched object is stored in objByOidMap hash table.
    * It is needed to provide OID->instance mapping. Since placing object in hash increase its access counter, 
    * such object can not be deallocated by garbage collector. So after some time all peristent objects from 
    * the storage will be loaded to the memory. To solve the problem almost all languages with implicit
    * memory deallocation (garbage collection) provides weak references. But no PHP.
    * So to prevent memory overflow you should use resetHash() method. 
    * This method just clear hash table. After invocation of this method, you should not use any variable
    * referening persistent objects. Instead you should invoke getRootObject method and access all other 
    * persistent objects only through the root. 
    */
    function resetHash() { 
        unset($this->objByOidMap);
    }        

   /**
    * Start garbage collection
    */
    function gc() {
        dybase_gc($this->db);
    }

   /**
    * Set garbage collection threshold.
    * By default garbage collection is disable (threshold is set to 0).
    * If it is set to non zero value, GC will be started each time when
    * delta between total size of allocated and deallocated objects exeeds specified threshold OR
    * after reaching end of allocation bitmap in allocator. 
    * @param allocated_delta delta between total size of allocated and deallocated object since last GC 
    * or storage openning 
    */
    function setGcThreshold($threshold) {
        dybase_setgcthreshold($this->db, $threshold);
    }
        
    function _loadArray(&$arr) {
        foreach ($arr as $key=>$value) { 
            if (get_class($key) == "Persistent") {
	        unset($arr[$key]);
                $key = &$this->_lookupObject($key->__oid__, false);
		$arr[$key] = &$value; 
            } else if (is_array($key)) { 
                $this->_loadArray($key);
            }
            if (get_class($value) == "Persistent") {
                $arr[$key] = &$this->_lookupObject($value->__oid__, false);
            } else if (is_array($value)) { 
                $this->_loadArray($value);
            }
        }
    }

    function &_fetchComponent($hnd, $recursive) {
    	$oid = dybase_getref($hnd);
        if ($oid == null) {                         
            $len = dybase_arraylength($hnd);
            if ($len != null) { 
                $value = &$this->_fetchArray($hnd, $len, $recursive);
            } else { 
                $value = dybase_getvalue($hnd);
            }
        } else if ($oid == 0) {
	    $value= null;
        } else if ($recursive) { 
            $value = &$this->_lookupObject($oid, false);
        } else {
            $value = &$this->objByOidMap[$oid];
            if ($value == null) { 
                $value = &new Persistent($oid);
            }
        }
	return $value;
    }

    function &_lookupObject($oid, $recursive=true) {
        if ($oid == 0) { 
            return null;
        }
        $obj = &$this->objByOidMap[$oid];
        if ($obj == null) { 
            $hnd = dybase_beginload($this->db, $oid);
            $className = dybase_getclassname($hnd);
            $obj = @new $className();
            $obj->__oid__ = $oid;
            if (!$recursive) { 
                if ($obj->recursiveLoading()) { 
                    $recursive = true;
                } else { 
                    $obj->__raw__ = true;
                }
            }
            $this->objByOidMap[$oid] = &$obj;          
            $obj->__storage__ = &$this;
            if (get_class($obj) == "Index") {
                dybase_nextfield($hnd);
                $obj->index = dybase_getref($hnd);
                dybase_nextfield($hnd);
            } else {       
                while (true) { 
                    $fieldName = dybase_nextfield($hnd);
                    if ($fieldName == null) { 
                         break;
                    }
                    $obj->$fieldName = $this->_fetchComponent($hnd, $recursive);
                }
                if ($recursive) {
                    $obj->onLoad();
                }
            }
        } else { 
            if ($recursive && $obj->__raw__) {     
                $this->loadObject($obj);
            }
        }
        return $obj;
    }

    function &_fetchArray($hnd, $len, $recursive) {
        $arr = array();
	for ($i = 0; $i < $len; $i++) { 
            dybase_nextelem($hnd);
	    $key = $this->_fetchComponent($hnd, $recursive);
            dybase_nextelem($hnd);
            $arr[$key] = $this->_fetchComponent($hnd, $recursive);
        }
        return $arr;
    }

    function _storeElement($hnd, &$elem) {
        if (is_int($elem) || is_float($elem) || is_string($elem)) {
             dybase_storeelem($hnd, $elem);
        } else if (is_array($elem)) { 
             dybase_storearrayelem($hnd, $elem);
	     foreach ($elem as $key=>$value) { 
                 $this->_storeElement($hnd, $key);
                 $this->_storeElement($hnd, $value);
             }
        } else if ($elem == null) {
             dybase_storerefelem($hnd, 0);
        } else { 
             if ($elem->__oid__ == null) {
                 $this->storeObject($elem);
             }
             dybase_storerefelem($hnd, $elem->__oid__);
        }
    }
}       
?>

