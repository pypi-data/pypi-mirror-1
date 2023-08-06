#include "Python.h"
#include "dybase.h"

#if !defined(LONG_LONG) && defined(PY_LONG_LONG)
#define LONG_LONG PY_LONG_LONG
#endif

static PyObject* DybaseOid(dybase_oid_t oid) 
{
    return oid == 0 ? NULL : PyInt_FromLong(oid);
}

static PyObject* DybaseHandle(void* hnd) 
{
    return hnd == NULL ? NULL : PyInt_FromLong((long)hnd);
}

static PyObject* DybaseNone(void) 
{
    if (PyErr_Occurred()) { 
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* DybaseBool(int result)
{
    if (PyErr_Occurred()) { 
        return NULL;
    }
    if (result) { 
        Py_INCREF(Py_True);
        return Py_True;
    } else {
        Py_INCREF(Py_False);
        return Py_False;
    }
}


static void DybaseErrorHandler(int error_code, char const* msg) {
    if (error_code != dybase_open_error) { 
        PyErr_SetString(PyExc_RuntimeError, msg);
    } else { 
        PyErr_Warn(NULL, (char*)msg) ;
    }
}

static PyObject* DybaseOpen(PyObject *self, PyObject *args)
{
    char* file_path;
    long int   page_pool_size;
    if (!PyArg_ParseTuple(args, "sl:open", &file_path, &page_pool_size)) {
        return NULL;
    }
    return DybaseHandle(dybase_open(file_path, page_pool_size, &DybaseErrorHandler));
}

static PyObject* DybaseClose(PyObject *self, PyObject *args)
{
    long int storage_handle;
    if (!PyArg_ParseTuple(args, "l:close", &storage_handle)) {
        return NULL;
    }
    dybase_close((dybase_storage_t)storage_handle);
    return DybaseNone();    
}

static PyObject* DybaseCommit(PyObject *self, PyObject *args)
{
    long int storage_handle;
    if (!PyArg_ParseTuple(args, "l:commit", &storage_handle)) {
        return NULL;
    }
    dybase_commit((dybase_storage_t)storage_handle);
    return DybaseNone();    
}

static PyObject* DybaseRollback(PyObject *self, PyObject *args)
{
    long int storage_handle;
    if (!PyArg_ParseTuple(args, "l:rollback", &storage_handle)) {
        return NULL;
    }
    dybase_rollback((dybase_storage_t)storage_handle);
    return DybaseNone();    
}

static PyObject* DybaseGetRootObject(PyObject *self, PyObject *args)
{
    long int storage_handle;
    if (!PyArg_ParseTuple(args, "l:getroot", &storage_handle)) {
        return NULL;
    }
    return PyInt_FromLong(dybase_get_root_object((dybase_storage_t)storage_handle));
}

static PyObject* DybaseSetRootObject(PyObject *self, PyObject *args)
{
    long int storage_handle;
    long int root_oid;
    if (!PyArg_ParseTuple(args, "ll:setroot", &storage_handle, &root_oid)) {
        return NULL;
    }
    dybase_set_root_object((dybase_storage_t)storage_handle, (dybase_oid_t)root_oid);
    return DybaseNone();    
}

static PyObject* DybaseAllocateObject(PyObject *self, PyObject *args)
{
    long int storage_handle;
    if (!PyArg_ParseTuple(args, "l:allocate", &storage_handle)) {
        return NULL;
    }
    return DybaseOid(dybase_allocate_object((dybase_storage_t)storage_handle));
}

static PyObject* DybaseDeallocateObject(PyObject *self, PyObject *args)
{
    long int storage_handle;
    long int oid;
    if (!PyArg_ParseTuple(args, "ll:deallocate", &storage_handle, &oid)) {
        return NULL;
    }
    dybase_deallocate_object((dybase_storage_t)storage_handle, (dybase_oid_t)oid);
    return DybaseNone();    
}

static PyObject* DybaseBeginStoreObject(PyObject *self, PyObject *args)
{
    long int storage_handle;
    long int oid;
    char* class_name;
    if (!PyArg_ParseTuple(args, "lls:beginstore", &storage_handle, &oid, &class_name)) {
        return NULL;
    }
    return DybaseHandle(dybase_begin_store_object((dybase_storage_t)storage_handle, (dybase_oid_t)oid, class_name));
}

static PyObject* DybaseStoreObjectReferenceField(PyObject *self, PyObject *args)
{
    long int handle;
    dybase_oid_t oid;
    long int value;    
    char* field_name;
    if (!PyArg_ParseTuple(args, "lsl:storereffield", &handle, &field_name, &value)) {
        return NULL;
    }
    oid = (dybase_oid_t)value;
    dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_object_type, &oid, 0);
    return DybaseNone();    
}
        
static PyObject* DybaseStoreObjectField(PyObject *self, PyObject *args)
{
    long int  handle;
    PyObject* value;
    char* field_name;
    
    if (!PyArg_ParseTuple(args, "lsO:storefield", &handle, &field_name, &value)) {
        return NULL;
    }
    if (PyInt_Check(value)) {
        int i = (int)PyInt_AS_LONG(value);
        dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_int_type, &i, 0);
    } else if (PyLong_Check(value)) { 
        LONG_LONG l = PyLong_AsLongLong(value);
        dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_long_type, &l, 0);
    } else if (PyFloat_Check(value)) { 
        double d = PyFloat_AS_DOUBLE(value);
        dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_real_type, &d, 0);
    } else if (PyString_Check(value)) {
        int length;
        char* buf;
        PyString_AsStringAndSize(value, &buf, &length); 
        dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_string_type, buf, length);
    } else if (PySequence_Check(value)) {
        dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_array_type, NULL, PySequence_Length(value));
    } else if (PyMapping_Check(value)) {
        dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_map_type, NULL, PyMapping_Length(value));
    }            
    return DybaseNone();    
}        
    
static PyObject* DybaseStoreArrayElement(PyObject *self, PyObject *args)
{
    long int  handle;
    PyObject* value;
    
    if (!PyArg_ParseTuple(args, "lO:storeelem", &handle, &value)) {
        return NULL;
    }
    if (PyInt_Check(value)) {
        int i = (int)PyInt_AS_LONG(value);
        dybase_store_array_element((dybase_handle_t)handle, dybase_int_type, &i, 0);
    } else if (PyLong_Check(value)) { 
        LONG_LONG l = PyLong_AsLongLong(value);
        dybase_store_array_element((dybase_handle_t)handle, dybase_long_type, &l, 0);
    } else if (PyFloat_Check(value)) { 
        double d = PyFloat_AS_DOUBLE(value);
        dybase_store_array_element((dybase_handle_t)handle, dybase_real_type, &d, 0);
    } else if (PyString_Check(value)) {
        int length;
        char* buf;
        PyString_AsStringAndSize(value, &buf, &length);
        dybase_store_array_element((dybase_handle_t)handle, dybase_string_type, buf, length);
    } else if (PySequence_Check(value)) {
        dybase_store_array_element((dybase_handle_t)handle, dybase_array_type, NULL, PySequence_Length(value));
    } else if (PyMapping_Check(value)) {
        dybase_store_array_element((dybase_handle_t)handle, dybase_map_type, NULL, PyMapping_Length(value));
    }            
    return DybaseNone();    
}        
    
static PyObject* DybaseStoreReferenceArrayElement(PyObject *self, PyObject *args)
{
    long int  handle;
    dybase_oid_t oid;
    long int value;    
    
    if (!PyArg_ParseTuple(args, "ll:storerefelem", &handle, &value)) {
        return NULL;
    }
    oid = (dybase_oid_t)value;
    dybase_store_array_element((dybase_handle_t)handle, dybase_object_type, &oid, 0);
    return DybaseNone();    
}

static PyObject* DybaseEndStoreObject(PyObject *self, PyObject *args)
{
    long int  handle;
    if (!PyArg_ParseTuple(args, "l:endstore", &handle)) {
        return NULL;
    }
    dybase_end_store_object((dybase_handle_t)handle);
    return DybaseNone();    
}


static PyObject* DybaseBeginLoadObject(PyObject *self, PyObject *args)
{
    long int storage_handle;
    long int oid;
    if (!PyArg_ParseTuple(args, "ll:beginload", &storage_handle, &oid)) {
        return NULL;
    }
    return DybaseHandle(dybase_begin_load_object((dybase_storage_t)storage_handle, (dybase_oid_t)oid));
}

static PyObject* DybaseGetClassName(PyObject *self, PyObject *args)
{
    long int  handle;
    if (!PyArg_ParseTuple(args, "l:getclassname", &handle)) {
        return NULL;
    }
    return PyString_FromString(dybase_get_class_name((dybase_handle_t)handle));
}


static PyObject* DybaseNextField(PyObject *self, PyObject *args)
{
    long int  handle;
    char* fieldName;
    if (!PyArg_ParseTuple(args, "l:nextfield", &handle)) {
        return NULL;
    }
    fieldName = dybase_next_field((dybase_handle_t)handle);
    if (fieldName == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return PyString_FromString(fieldName);
}
    
static PyObject* DybaseNextElement(PyObject *self, PyObject *args)
{
    long int  handle;
    if (!PyArg_ParseTuple(args, "l:nextelem", &handle)) {
        return NULL;
    }
    dybase_next_element((dybase_handle_t)handle);
    return DybaseNone();    
}
    
static PyObject* DybaseGetReferece(PyObject *self, PyObject *args)
{
    long int  handle;
    int type;
    void* value;
    int length;
    if (!PyArg_ParseTuple(args, "l:getref", &handle)) {
        return NULL;
    }
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);
    if (type != dybase_object_type) {
        Py_INCREF(Py_None);
        return Py_None;
    }    
    return PyInt_FromLong(*(dybase_oid_t*)value);
}
    
static PyObject* DybaseGetValue(PyObject *self, PyObject *args)
{
    long int  handle;
    int type;
    void* value;
    int length;
    
    if (!PyArg_ParseTuple(args, "l:getvalue", &handle)) {
        return NULL;
    }
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);
    switch (type) { 
      case dybase_int_type:
        return PyInt_FromLong(*(int*)value);  
      case dybase_long_type:
        return PyLong_FromLongLong(*(LONG_LONG*)value);  
      case dybase_real_type:
        return PyFloat_FromDouble(*(double*)value);  
      case dybase_string_type:
        return PyString_FromStringAndSize((char*)value, length);
      default:
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static PyObject* DybaseGetArrayLength(PyObject *self, PyObject *args)
{
    long int  handle;
    int type;
    void* value;
    int length;
    
    if (!PyArg_ParseTuple(args, "l:getvalue", &handle)) {
        return NULL;
    }
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);
    if (type != dybase_array_type) { 
        Py_INCREF(Py_None);
        return Py_None;
    }
    return PyInt_FromLong(length);
}

static PyObject* DybaseGetDictionaryLength(PyObject *self, PyObject *args)
{
    long int  handle;
    int type;
    void* value;
    int length;
    
    if (!PyArg_ParseTuple(args, "l:getvalue", &handle)) {
        return NULL;
    }
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);
    if (type != dybase_map_type) { 
        Py_INCREF(Py_None);
        return Py_None;
    }
    return PyInt_FromLong(length);
}

static PyObject* DybaseCreateStringIndex(PyObject *self, PyObject *args)
{
    long int  storage_handle;
    PyObject* unique;
    if (!PyArg_ParseTuple(args, "lO:createstrindex", &storage_handle, &unique)) {
        return NULL;
    }
    return DybaseOid(dybase_create_index((dybase_storage_t)storage_handle, dybase_string_type, PyObject_IsTrue(unique)));
}

static PyObject* DybaseCreateIntIndex(PyObject *self, PyObject *args)
{
    long int  storage_handle;
    PyObject* unique;
    if (!PyArg_ParseTuple(args, "lO:createingindex", &storage_handle, &unique)) {
        return NULL;
    }
    return DybaseOid(dybase_create_index((dybase_storage_t)storage_handle, dybase_int_type, PyObject_IsTrue(unique)));
}

static PyObject* DybaseCreateLongIndex(PyObject *self, PyObject *args)
{
    long int  storage_handle;
    PyObject* unique;
    if (!PyArg_ParseTuple(args, "lO:createlongindex", &storage_handle, &unique)) {
        return NULL;
    }
    return DybaseOid(dybase_create_index((dybase_storage_t)storage_handle, dybase_long_type, PyObject_IsTrue(unique)));
}

static PyObject* DybaseCreateRealIndex(PyObject *self, PyObject *args)
{
    long int  storage_handle;
    PyObject* unique;
    if (!PyArg_ParseTuple(args, "lO:createrealindex", &storage_handle, &unique)) {
        return NULL;
    }
    return DybaseOid(dybase_create_index((dybase_storage_t)storage_handle, dybase_real_type, PyObject_IsTrue(unique)));
}

static PyObject* DybaseInsertInIndex(PyObject *self, PyObject *args)
{
    long int  storage_handle;
    PyObject* key;
    PyObject* replace;
    long int  index, value;
    int       result = 0;
    if (!PyArg_ParseTuple(args, "llOlO:insertinindex", &storage_handle, &index, &key, &value, &replace)) {
        return NULL;
    }
    
    if (PyInt_Check(key)) {
        int i = (int)PyInt_AS_LONG(key);
        result = dybase_insert_in_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &i, dybase_int_type, 0, (dybase_oid_t)value, PyObject_IsTrue(replace));
    } else if (PyLong_Check(key)) { 
        LONG_LONG l = PyLong_AsLongLong(key);
        result = dybase_insert_in_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &l, dybase_long_type, 0, (dybase_oid_t)value, PyObject_IsTrue(replace));
    } else if (PyFloat_Check(key)) { 
        double d = PyFloat_AS_DOUBLE(key);
        result = dybase_insert_in_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &d, dybase_real_type, 0, (dybase_oid_t)value, PyObject_IsTrue(replace));
    } else if (PyString_Check(key)) {
        int length;
        char* buf;
        PyString_AsStringAndSize(key, &buf, &length);
        result = dybase_insert_in_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, buf, dybase_string_type, length, (dybase_oid_t)value, PyObject_IsTrue(replace));
    } else { 
        DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
        return NULL;
    } 
    return DybaseBool(result);
}

static PyObject* DybaseRemoveFromIndex(PyObject *self, PyObject *args)
{
    long int  storage_handle;
    PyObject* key;
    long int  index, value;
    int       result = 0;
    if (!PyArg_ParseTuple(args, "llOl:removefromindex", &storage_handle, &index, &key, &value)) {
        return NULL;
    }
    
    if (PyInt_Check(key)) {
        int i = (int)PyInt_AS_LONG(key);
        result = dybase_remove_from_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &i, dybase_int_type, 0, (dybase_oid_t)value);
    } else if (PyLong_Check(key)) { 
        LONG_LONG l = PyLong_AsLongLong(key);
        result = dybase_remove_from_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &l, dybase_long_type, 0, (dybase_oid_t)value);
    } else if (PyFloat_Check(key)) { 
        double d = PyFloat_AS_DOUBLE(key);
        result = dybase_remove_from_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &d, dybase_real_type, 0, (dybase_oid_t)value);
    } else if (PyString_Check(key)) {
        int length;
        char* buf;
        PyString_AsStringAndSize(key, &buf, &length);
        result = dybase_remove_from_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, buf, dybase_string_type, length, (dybase_oid_t)value);
    } else { 
        DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
        return NULL;
    }
    return DybaseBool(result);
}

static PyObject* DybaseIndexSearch(PyObject *self, PyObject *args)
{
    long int  storage_handle;
    PyObject *low, *lowInclusive, *high, *highInclusive, *list;    
    long int  index_oid;
    dybase_oid_t* selected_objects;
    int i, n_selected = 0;
    dybase_storage_t storage;
    dybase_oid_t index;

    if (!PyArg_ParseTuple(args, "llOOOO:indexsearch", &storage_handle, &index_oid, &low, &lowInclusive, &high, &highInclusive)) {
        return NULL;
    }
    storage = (dybase_storage_t)storage_handle;
    index = (dybase_oid_t)index_oid;
    if (low == Py_None) { 
        if (high == Py_None) { 
            n_selected = dybase_index_search(storage, index, 0, NULL, 0, 0, NULL, 0, 0, &selected_objects);
        } else if (PyInt_Check(high)) {
            int highVal = (int)PyInt_AS_LONG(high);
            n_selected = dybase_index_search(storage, index, dybase_int_type, NULL, 0, 0, &highVal, 0, PyObject_IsTrue(highInclusive), &selected_objects);
        } else if (PyLong_Check(high)) { 
            LONG_LONG highVal = PyLong_AsLongLong(high);
            n_selected = dybase_index_search(storage, index, dybase_long_type, NULL, 0, 0, &highVal, 0, PyObject_IsTrue(highInclusive), &selected_objects);            
        } else if (PyFloat_Check(high)) { 
            double highVal = PyFloat_AS_DOUBLE(high);
            n_selected = dybase_index_search(storage, index, dybase_real_type, NULL, 0, 0, &highVal, 0, PyObject_IsTrue(highInclusive), &selected_objects);            
        } else if (PyString_Check(high)) {            
            int length;
            char* buf;
            PyString_AsStringAndSize(high, &buf, &length);
            n_selected = dybase_index_search(storage, index, dybase_string_type, NULL, 0, 0, buf, length, PyObject_IsTrue(highInclusive), &selected_objects);
        } else { 
            DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
            return NULL;
        }
    } else if (high == Py_None) { 
        if (PyInt_Check(low)) {
            int lowVal = (int)PyInt_AS_LONG(low);
            n_selected = dybase_index_search(storage, index, dybase_int_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), NULL, 0, 0, &selected_objects);
        } else if (PyLong_Check(low)) { 
            LONG_LONG lowVal = PyLong_AsLongLong(low);
            n_selected = dybase_index_search(storage, index, dybase_long_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), NULL, 0, 0, &selected_objects);            
        } else if (PyFloat_Check(low)) { 
            double lowVal = PyFloat_AS_DOUBLE(low);
            n_selected = dybase_index_search(storage, index, dybase_real_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), NULL, 0, 0, &selected_objects);            
        } else if (PyString_Check(low)) {            
            int length;
            char* buf;
            PyString_AsStringAndSize(low, &buf, &length);
            n_selected = dybase_index_search(storage, index, dybase_string_type, buf, length, PyObject_IsTrue(lowInclusive), NULL, 0, 0, &selected_objects);
        } else { 
            DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
            return NULL;
        }
    } else if (PyInt_Check(low) && PyInt_Check(high)) {
        int lowVal = (int)PyInt_AS_LONG(low);
        int highVal = (int)PyInt_AS_LONG(high);
        n_selected =  dybase_index_search(storage, index, dybase_int_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), &highVal, 0, PyObject_IsTrue(highInclusive), &selected_objects);
    } else if (PyLong_Check(low) && PyLong_Check(high)) { 
        LONG_LONG lowVal = PyLong_AsLongLong(low);
        LONG_LONG highVal = PyLong_AsLongLong(high);
        n_selected = dybase_index_search(storage, index, dybase_long_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), &highVal, 0, PyObject_IsTrue(highInclusive), &selected_objects);
    } else if (PyFloat_Check(low) && PyFloat_Check(high)) { 
        double lowVal = PyFloat_AS_DOUBLE(low);
        double highVal = PyFloat_AS_DOUBLE(high);
        n_selected = dybase_index_search(storage, index, dybase_real_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), &highVal, 0, PyObject_IsTrue(highInclusive), &selected_objects);
    } else if (PyString_Check(low) && PyString_Check(high)) {  
        int lowLength, highLength;
        char *lowBuf, *highBuf;
        PyString_AsStringAndSize(high, &highBuf, &highLength);
        PyString_AsStringAndSize(low, &lowBuf, &lowLength);
        n_selected = dybase_index_search(storage, index, dybase_string_type, lowBuf, lowLength, PyObject_IsTrue(lowInclusive), 
                                          highBuf, highLength, PyObject_IsTrue(highInclusive), &selected_objects);
    } else { 
        DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
        return NULL;
    }
    if (n_selected == 0) { 
        return DybaseNone();
    } 
    list = PyList_New(n_selected);
    for (i = 0; i < n_selected; i++) { 
        PyList_SET_ITEM(list, i, PyInt_FromLong(selected_objects[i]));
    }
    dybase_free_selection(storage, selected_objects, n_selected);
    return list;
}

static PyObject* DybaseDropIndex(PyObject *self, PyObject *args)
{
    long int storage_handle;
    long int index;

    if (!PyArg_ParseTuple(args, "ll:dropindex", &storage_handle, &index)) {
        return NULL;
    }
    dybase_drop_index((dybase_storage_t)storage_handle, (dybase_oid_t)index);
    return DybaseNone();
}

static PyObject* DybaseClearIndex(PyObject *self, PyObject *args)
{
    long int storage_handle;
    long int index;

    if (!PyArg_ParseTuple(args, "ll:clearindex", &storage_handle, &index)) {
        return NULL;
    }
    dybase_clear_index((dybase_storage_t)storage_handle, (dybase_oid_t)index);
    return DybaseNone();
}

static PyObject* DybaseGC(PyObject *self, PyObject *args)
{
    long int storage_handle;

    if (!PyArg_ParseTuple(args, "l:gc", &storage_handle)) {
        return NULL;
    }
    dybase_gc((dybase_storage_t)storage_handle);
    return DybaseNone();
}

static PyObject* DybaseSetGCThreshold(PyObject *self, PyObject *args)
{
    long int storage_handle;
    long int threshold;

    if (!PyArg_ParseTuple(args, "ll:setgcthreshold", &storage_handle, &threshold)) {
        return NULL;
    }
    dybase_set_gc_threshold((dybase_storage_t)storage_handle, threshold);
    return DybaseNone();
}

static PyObject* DybaseCreateIterator(PyObject *self, PyObject *args)
{
    long int  storage_handle;
    PyObject *low, *lowInclusive, *high, *highInclusive, *ascentOrder;    
    long int  index_oid;
    dybase_iterator_t iterator = NULL;
    dybase_storage_t storage;
    dybase_oid_t index;
    int ascent;

    if (!PyArg_ParseTuple(args, "llOOOOO:createiterator", &storage_handle, &index_oid, &low, &lowInclusive, &high, &highInclusive, &ascentOrder)) {
        return NULL;
    }
    storage = (dybase_storage_t)storage_handle;
    index = (dybase_oid_t)index_oid;
    ascent = PyObject_IsTrue(ascentOrder);
    if (low == Py_None) { 
        if (high == Py_None) { 
            iterator = dybase_create_index_iterator(storage, index, 0, NULL, 0, 0, NULL, 0, 0, ascent);
        } else if (PyInt_Check(high)) {
            int highVal = (int)PyInt_AS_LONG(high);
            iterator = dybase_create_index_iterator(storage, index, dybase_int_type, NULL, 0, 0, &highVal, 0, PyObject_IsTrue(highInclusive), ascent);
        } else if (PyLong_Check(high)) { 
            LONG_LONG highVal = PyLong_AsLongLong(high);
            iterator = dybase_create_index_iterator(storage, index, dybase_long_type, NULL, 0, 0, &highVal, 0, PyObject_IsTrue(highInclusive), ascent);            
        } else if (PyFloat_Check(high)) { 
            double highVal = PyFloat_AS_DOUBLE(high);
            iterator = dybase_create_index_iterator(storage, index, dybase_real_type, NULL, 0, 0, &highVal, 0, PyObject_IsTrue(highInclusive), ascent);            
        } else if (PyString_Check(high)) {            
            int length;
            char* buf;
            PyString_AsStringAndSize(high, &buf, &length);
            iterator = dybase_create_index_iterator(storage, index, dybase_string_type, NULL, 0, 0, buf, length, PyObject_IsTrue(highInclusive), ascent);
        } else { 
            DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
            return NULL;
        }
    } else if (high == Py_None) { 
        if (PyInt_Check(low)) {
            int lowVal = (int)PyInt_AS_LONG(low);
            iterator = dybase_create_index_iterator(storage, index, dybase_int_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), NULL, 0, 0, ascent);
        } else if (PyLong_Check(low)) { 
            LONG_LONG lowVal = PyLong_AsLongLong(low);
            iterator = dybase_create_index_iterator(storage, index, dybase_long_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), NULL, 0, 0, ascent);            
        } else if (PyFloat_Check(low)) { 
            double lowVal = PyFloat_AS_DOUBLE(low);
            iterator = dybase_create_index_iterator(storage, index, dybase_real_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), NULL, 0, 0, ascent);            
        } else if (PyString_Check(low)) {            
            int length;
            char* buf;
            PyString_AsStringAndSize(low, &buf, &length);
            iterator = dybase_create_index_iterator(storage, index, dybase_string_type, buf, length, PyObject_IsTrue(lowInclusive), NULL, 0, 0, ascent);
        } else { 
            DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
            return NULL;
        }
    } else if (PyInt_Check(low) && PyInt_Check(high)) {
        int lowVal = (int)PyInt_AS_LONG(low);
        int highVal = (int)PyInt_AS_LONG(high);
        iterator = dybase_create_index_iterator(storage, index, dybase_int_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), &highVal, 0, PyObject_IsTrue(highInclusive), ascent);
    } else if (PyLong_Check(low) && PyLong_Check(high)) { 
        LONG_LONG lowVal = PyLong_AsLongLong(low);
        LONG_LONG highVal = PyLong_AsLongLong(high);
        iterator = dybase_create_index_iterator(storage, index, dybase_long_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), &highVal, 0, PyObject_IsTrue(highInclusive), ascent);
    } else if (PyFloat_Check(low) && PyFloat_Check(high)) { 
        double lowVal = PyFloat_AS_DOUBLE(low);
        double highVal = PyFloat_AS_DOUBLE(high);
        iterator = dybase_create_index_iterator(storage, index, dybase_real_type, &lowVal, 0, PyObject_IsTrue(lowInclusive), &highVal, 0, PyObject_IsTrue(highInclusive), ascent);
    } else if (PyString_Check(low) && PyString_Check(high)) {  
        int lowLength, highLength;
        char *lowBuf, *highBuf;
        PyString_AsStringAndSize(high, &highBuf, &highLength);
        PyString_AsStringAndSize(low, &lowBuf, &lowLength);
        iterator = dybase_create_index_iterator(storage, index, dybase_string_type, lowBuf, lowLength, PyObject_IsTrue(lowInclusive), 
                                          highBuf, highLength, PyObject_IsTrue(highInclusive), ascent);
    } else { 
        DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
        return NULL;
    }
    return DybaseHandle(iterator);
}

static PyObject* DybaseFreeIterator(PyObject *self, PyObject *args)
{
    long int iterator;

    if (!PyArg_ParseTuple(args, "l:freeiterator", &iterator)) {
        return NULL;
    }
    dybase_free_index_iterator((dybase_iterator_t)iterator);
    return DybaseNone();   
}

static PyObject* DybaseIteratorNext(PyObject *self, PyObject *args)
{
    long int iterator;

    if (!PyArg_ParseTuple(args, "l:freeiterator", &iterator)) {
        return NULL;
    }
    return PyInt_FromLong(dybase_index_iterator_next((dybase_iterator_t)iterator));
}


static PyMethodDef dybase_methods[] = {
    {"open", DybaseOpen, METH_VARARGS},
    {"close", DybaseClose, METH_VARARGS},
    {"commit", DybaseCommit, METH_VARARGS},
    {"rollback", DybaseRollback, METH_VARARGS},
    {"getroot", DybaseGetRootObject, METH_VARARGS},
    {"setroot", DybaseSetRootObject, METH_VARARGS},
    {"allocate", DybaseAllocateObject, METH_VARARGS},
    {"deallocate", DybaseDeallocateObject, METH_VARARGS},
    {"beginstore", DybaseBeginStoreObject, METH_VARARGS},
    {"storereffield", DybaseStoreObjectReferenceField, METH_VARARGS},
    {"storefield", DybaseStoreObjectField, METH_VARARGS},
    {"storeelem", DybaseStoreArrayElement, METH_VARARGS},
    {"storerefelem", DybaseStoreReferenceArrayElement, METH_VARARGS},
    {"endstore", DybaseEndStoreObject, METH_VARARGS},
    {"beginload", DybaseBeginLoadObject, METH_VARARGS},
    {"getclassname", DybaseGetClassName, METH_VARARGS},
    {"nextfield", DybaseNextField, METH_VARARGS},
    {"nextelem", DybaseNextElement, METH_VARARGS},
    {"getref", DybaseGetReferece, METH_VARARGS},
    {"getvalue", DybaseGetValue, METH_VARARGS},
    {"arraylength", DybaseGetArrayLength, METH_VARARGS},
    {"dictlength", DybaseGetDictionaryLength, METH_VARARGS},
    {"createstrindex", DybaseCreateStringIndex, METH_VARARGS},
    {"createintindex", DybaseCreateIntIndex, METH_VARARGS},
    {"createlongindex", DybaseCreateLongIndex, METH_VARARGS},
    {"createrealindex", DybaseCreateRealIndex, METH_VARARGS},
    {"insertinindex", DybaseInsertInIndex, METH_VARARGS},
    {"removefromindex", DybaseRemoveFromIndex, METH_VARARGS},
    {"searchindex", DybaseIndexSearch, METH_VARARGS},
    {"dropindex", DybaseDropIndex, METH_VARARGS},
    {"clearindex", DybaseClearIndex, METH_VARARGS},
    {"createiterator", DybaseCreateIterator, METH_VARARGS},
    {"freeiterator", DybaseFreeIterator, METH_VARARGS},
    {"iteratornext", DybaseIteratorNext, METH_VARARGS},
    {"gc", DybaseGC, METH_VARARGS},
    {"setgcthreshold", DybaseSetGCThreshold, METH_VARARGS},
    {NULL, NULL}
};


#ifdef __cplusplus
extern "C" {
#endif
PyMODINIT_FUNC
init_dybase(void)
{
    PyObject *m = Py_InitModule("_dybase", dybase_methods);
    if (m == NULL) { 
        printf("Failed to load module");
    }
    
}
