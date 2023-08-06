#include "zend.h"
#include "zend_API.h"
#include "dybase.h"

extern zend_module_entry dbm_module_entry;
#define phpext_db_ptr &dbm_module_entry

static void DybaseErrorHandler(int error_code, char const* msg) {
    zend_error(error_code == dybase_open_error ? E_WARNING : E_ERROR, msg);
}

ZEND_FUNCTION(dybase_open)
{
    char* file_path;
    int  file_path_len;
    long int   page_pool_size;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "sl", &file_path, &file_path_len, &page_pool_size) == FAILURE) {
        return;
    }
    RETURN_LONG((long)dybase_open(file_path, page_pool_size, &DybaseErrorHandler));
}

ZEND_FUNCTION(dybase_close)
{
    long int storage_handle;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &storage_handle) == FAILURE) {
        return;
    }
    dybase_close((dybase_storage_t)storage_handle);
    RETURN_NULL();    
}

ZEND_FUNCTION(dybase_commit)
{
    long int storage_handle;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &storage_handle) == FAILURE) {
        return;
    }
    dybase_commit((dybase_storage_t)storage_handle);
    RETURN_NULL();    
}

ZEND_FUNCTION(dybase_rollback)
{
    long int storage_handle;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &storage_handle) == FAILURE) {
        return;
    }
    dybase_rollback((dybase_storage_t)storage_handle);
    RETURN_NULL();    
}

ZEND_FUNCTION(dybase_getroot)
{
    long int storage_handle;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &storage_handle) == FAILURE) {
        return;
    }
    RETURN_LONG(dybase_get_root_object((dybase_storage_t)storage_handle));
}

ZEND_FUNCTION(dybase_setroot)
{
    long int storage_handle;
    long int root_oid;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ll", &storage_handle, &root_oid) == FAILURE) {
        return;
    }
    dybase_set_root_object((dybase_storage_t)storage_handle, (dybase_oid_t)root_oid);
    RETURN_NULL();    
}

ZEND_FUNCTION(dybase_allocate)
{
    long int storage_handle;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &storage_handle) == FAILURE) {
        return;
    }
    RETURN_LONG(dybase_allocate_object((dybase_storage_t)storage_handle));
}

ZEND_FUNCTION(dybase_deallocate)
{
    long int storage_handle;
    long int oid;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ll", &storage_handle, &oid) == FAILURE) {
        return;
    }
    dybase_deallocate_object((dybase_storage_t)storage_handle, (dybase_oid_t)oid);
    RETURN_NULL();    
}

ZEND_FUNCTION(dybase_beginstore)
{
    long int storage_handle;
    long int oid;
    char* class_name;
    int class_name_len;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "lls", &storage_handle, &oid, &class_name, &class_name_len) == FAILURE) {
        return;
    }
    RETURN_LONG((long)dybase_begin_store_object((dybase_storage_t)storage_handle, (dybase_oid_t)oid, class_name));
}

ZEND_FUNCTION(dybase_storereffield)
{
    long int handle;
    dybase_oid_t oid;
    long int value;    
    char* field_name;
    int field_name_len;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "lsl", &handle, &field_name, &field_name_len, &value) == FAILURE) {
        return;
    }
    oid = (dybase_oid_t)value;
    dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_object_type, &oid, 0);
    RETURN_NULL();    
}
        
ZEND_FUNCTION(dybase_storearrayfield)
{
    long int  handle;
    long int  length;
    char* field_name;
    int field_name_len;
    
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "lsl", &handle, &field_name, &field_name_len, &length) == FAILURE) {
        return;
    }
    dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_map_type, NULL, (int)length);
    RETURN_NULL();    
}        
    


ZEND_FUNCTION(dybase_storefield)
{
    long int  handle;
    zval* value;
    char* field_name;
    int field_name_len;
    
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "lsz", &handle, &field_name, &field_name_len, &value) == FAILURE) {
        return;
    }
    switch (Z_TYPE_P(value)) {
      case IS_BOOL:
        {
            zend_bool b = (zend_bool)Z_BVAL_P(value);
            dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_bool_type, &b, 0);        
        }
        break;
      case IS_LONG:
        {
            int i = Z_LVAL_P(value);
            dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_int_type, &i, 0);
        }
        break;
      case IS_DOUBLE:
        { 
            double d = Z_DVAL_P(value);
            dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_real_type, &d, 0);
        }
        break;
      case IS_STRING:
        dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_string_type, Z_STRVAL_P(value), Z_STRLEN_P(value));
        break;
      case IS_ARRAY:
        dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_map_type, NULL, zend_hash_num_elements(Z_ARRVAL_P(value)));
        break;
    }            
    RETURN_NULL();    
}        
    
ZEND_FUNCTION(dybase_storearrayelem)
{
    long int  handle;
    long int  length;
    
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ll", &handle, &length) == FAILURE) {
        return;
    }
    dybase_store_array_element((dybase_handle_t)handle, dybase_map_type, NULL, (int)length);
    RETURN_NULL();    
}        
    
ZEND_FUNCTION(dybase_storeelem)
{
    long int  handle;
    zval* value;
    
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "lz", &handle, &value) == FAILURE) {
        return;
    }
    switch (Z_TYPE_P(value)) {
      case IS_BOOL:
        {
            zend_bool b = (zend_bool)Z_BVAL_P(value);
            dybase_store_array_element((dybase_handle_t)handle, dybase_bool_type, &b, 0);
        }
        break;
      case IS_LONG:
        { 
            int i = (int)Z_LVAL_P(value);
            dybase_store_array_element((dybase_handle_t)handle, dybase_int_type, &i, 0);
        }
        break;
      case IS_DOUBLE:
        { 
            double d = Z_DVAL_P(value);
            dybase_store_array_element((dybase_handle_t)handle, dybase_real_type, &d, 0);
        }
        break;
      case IS_STRING:
        dybase_store_array_element((dybase_handle_t)handle, dybase_string_type, Z_STRVAL_P(value), Z_STRLEN_P(value));
        break;
      case IS_ARRAY:
        dybase_store_array_element((dybase_handle_t)handle, dybase_map_type, NULL, zend_hash_num_elements(Z_ARRVAL_P(value)));
    }            
    RETURN_NULL();    
}        
    
ZEND_FUNCTION(dybase_storerefelem)
{
    long int  handle;
    dybase_oid_t oid;
    long int value;    
    
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ll", &handle, &value) == FAILURE) {
        return;
    }
    oid = (dybase_oid_t)value;
    dybase_store_array_element((dybase_handle_t)handle, dybase_object_type, &oid, 0);
    RETURN_NULL();    
}

ZEND_FUNCTION(dybase_endstore)
{
    long int  handle;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &handle) == FAILURE) {
        return;
    }
    dybase_end_store_object((dybase_handle_t)handle);
    RETURN_NULL();    
}


ZEND_FUNCTION(dybase_beginload)
{
    long int storage_handle;
    long int oid;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ll", &storage_handle, &oid) == FAILURE) {
        return;
    }
    RETURN_LONG((long)dybase_begin_load_object((dybase_storage_t)storage_handle, (dybase_oid_t)oid));
}

ZEND_FUNCTION(dybase_getclassname)
{
    long int  handle;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &handle) == FAILURE) {
        return;
    }
    RETURN_STRING(dybase_get_class_name((dybase_handle_t)handle), 1);
}


ZEND_FUNCTION(dybase_nextfield)
{
    long int  handle;
    char* fieldName;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &handle) == FAILURE) {
        return;
    }
    fieldName = dybase_next_field((dybase_handle_t)handle);
    if (fieldName == NULL) {
        RETURN_NULL();
    }
    RETURN_STRING(fieldName, 1);
}
    
ZEND_FUNCTION(dybase_nextelem)
{
    long int  handle;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &handle) == FAILURE) {
        return;
    }
    dybase_next_element((dybase_handle_t)handle);
    RETURN_NULL();    
}
    
ZEND_FUNCTION(dybase_getref)
{
    long int  handle;
    int type;
    void* value;
    int length;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &handle) == FAILURE) {
        return;
    }
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);
    if (type != dybase_object_type) {
        RETURN_NULL();    
    }    
    RETURN_LONG(*(dybase_oid_t*)value);
}
    
ZEND_FUNCTION(dybase_getvalue)
{
    long int  handle;
    int type;
    void* value;
    int length;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &handle) == FAILURE) {
        return;
    }
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);
    switch (type) { 
      case dybase_int_type:
        RETURN_LONG(*(int*)value);  
      case dybase_bool_type:
        RETURN_BOOL(*(zend_bool*)value);  
      case dybase_real_type:
        RETURN_DOUBLE(*(double*)value);  
      case dybase_string_type:
        RETURN_STRINGL((char*)value, length, 1);
      default:
        RETURN_NULL();
    }
}

ZEND_FUNCTION(dybase_arraylength)
{
    long int  handle;
    int type;
    void* value;
    int length;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &handle) == FAILURE) {
        return;
    }
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);
    if (type != dybase_map_type) {
        RETURN_NULL();    
    }    
    RETURN_LONG(length);  
}

ZEND_FUNCTION(dybase_createstrindex)
{
    long int  storage_handle;
    zend_bool unique = 1;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l|b", &storage_handle, &unique) == FAILURE) {
        return;
    }
    RETURN_LONG(dybase_create_index((dybase_storage_t)storage_handle, dybase_string_type, unique));
}

ZEND_FUNCTION(dybase_createintindex)
{
    long int  storage_handle;
    zend_bool unique = 1;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l|b", &storage_handle, &unique) == FAILURE) {
        return;
    }
    RETURN_LONG(dybase_create_index((dybase_storage_t)storage_handle, dybase_int_type, unique));
}

ZEND_FUNCTION(dybase_createboolindex)
{
    long int  storage_handle;
    zend_bool unique = 1;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l|b", &storage_handle, &unique) == FAILURE) {
        return;
    }
    RETURN_LONG(dybase_create_index((dybase_storage_t)storage_handle, dybase_bool_type, unique));
}

ZEND_FUNCTION(dybase_createrealindex)
{
    long int  storage_handle;
    zend_bool unique = 1;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l|b", &storage_handle, &unique) == FAILURE) {
        return;
    }
    RETURN_LONG(dybase_create_index((dybase_storage_t)storage_handle, dybase_real_type, unique));
}

ZEND_FUNCTION(dybase_insertinindex)
{
    long int  storage_handle;
    zval*     key;
    long int  index, value;
    int       result = 0;
    zend_bool replace = 1;

    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "llzl|b", &storage_handle, &index, &key, &value, &replace) == FAILURE) {
        return;
    }
    switch (Z_TYPE_P(key)) {
      case IS_BOOL:
        {
            zend_bool b = (char)Z_BVAL_P(key);
            result = dybase_insert_in_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &b, dybase_bool_type, 0, (dybase_oid_t)value, replace);
        }
        break;
      case IS_LONG:
        { 
            int i = (int)Z_LVAL_P(key);
            result = dybase_insert_in_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &i, dybase_int_type, 0, (dybase_oid_t)value, replace);
        }
        break;
      case IS_DOUBLE:
        { 
            double d = Z_DVAL_P(key);
            result = dybase_insert_in_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &d, dybase_real_type, 0, (dybase_oid_t)value, replace);
        }
        break;
      case IS_STRING:
        result = dybase_insert_in_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, Z_STRVAL_P(key), dybase_string_type, Z_STRLEN_P(key), (dybase_oid_t)value, replace);
        break;
      default:
        DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
    } 
    RETURN_BOOL(result);
}

ZEND_FUNCTION(dybase_removefromindex)
{
    long int  storage_handle;
    zval* key;
    long int  index, value;
    int       result = 0;
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "llzl", &storage_handle, &index, &key, &value) == FAILURE) {
        return;
    }
    
    switch (Z_TYPE_P(key)) {
      case IS_BOOL:
        {
            zend_bool b = (char)Z_BVAL_P(key);
            result = dybase_remove_from_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &b, dybase_bool_type, 0, (dybase_oid_t)value);
        }
        break;
      case IS_LONG:
        { 
            int i = (int)Z_LVAL_P(key);
            result = dybase_remove_from_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &i, dybase_int_type, 0, (dybase_oid_t)value);
        }
        break;
      case IS_DOUBLE:
        {
            double d = Z_DVAL_P(key);
            result = dybase_remove_from_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, &d, dybase_real_type, 0, (dybase_oid_t)value);
        }
        break;
      case IS_STRING:
        result = dybase_remove_from_index((dybase_handle_t)storage_handle, (dybase_oid_t)index, Z_STRVAL_P(key), dybase_string_type, Z_STRLEN_P(key), (dybase_oid_t)value);
        break;
      default: 
        DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
    } 
    RETURN_BOOL(result); 
}

ZEND_FUNCTION(dybase_searchindex)
{
    long int  storage_handle;
    zval *low, *high;
    zend_bool lowInclusive, highInclusive;    
    long int  index_oid;
    dybase_oid_t* selected_objects;
    int i, n_selected = 0;
    int lowType, highType;
    dybase_storage_t storage;
    dybase_oid_t index;

    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "llzbzb", &storage_handle, &index_oid, &low, &lowInclusive, &high, &highInclusive) == FAILURE) {
        return;
    }
    storage = (dybase_storage_t)storage_handle;
    index = (dybase_oid_t)index_oid;
    lowType = Z_TYPE_P(low);
    highType = Z_TYPE_P(high);
    if (lowType == IS_NULL) { 
        switch (highType) { 
          case IS_NULL:
            n_selected = dybase_index_search(storage, index, 0, NULL, 0, 0, NULL, 0, 0, &selected_objects);
            break;
          case IS_BOOL:
            {
                zend_bool highVal = Z_BVAL_P(high);
                n_selected = dybase_index_search(storage, index, dybase_bool_type, NULL, 0, 0, &highVal, 0, highInclusive, &selected_objects);
            }
            break;
          case IS_LONG:
            { 
                int highVal = Z_LVAL_P(high);
                n_selected = dybase_index_search(storage, index, dybase_int_type, NULL, 0, 0, &highVal, 0, highInclusive, &selected_objects);
            }
            break;
          case IS_DOUBLE:
            {
                double highVal =  Z_DVAL_P(high);
                n_selected = dybase_index_search(storage, index, dybase_real_type, NULL, 0, 0, &highVal, 0, highInclusive, &selected_objects); 
            }
            break;
          case IS_STRING:
            n_selected = dybase_index_search(storage, index, dybase_string_type, NULL, 0, 0, Z_STRVAL_P(high), Z_STRLEN_P(high), highInclusive, &selected_objects);
          default:
            DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
        }
    } else if (highType == IS_NULL) { 
        switch (lowType) { 
          case IS_BOOL:
            {
                zend_bool lowVal = Z_BVAL_P(low);
                n_selected = dybase_index_search(storage, index, dybase_bool_type, &lowVal, 0, lowInclusive, NULL, 0, 0, &selected_objects);
            }
            break;
          case IS_LONG:
            { 
                int lowVal = Z_LVAL_P(low);
                n_selected = dybase_index_search(storage, index, dybase_int_type, &lowVal, 0, lowInclusive, NULL, 0, 0, &selected_objects);
            }
            break;
          case IS_DOUBLE:
            {
                double lowVal =  Z_DVAL_P(low);
                n_selected = dybase_index_search(storage, index, dybase_real_type, &lowVal, 0, lowInclusive,  NULL, 0, 0, &selected_objects);   
            }
            break;
          case IS_STRING:
            n_selected = dybase_index_search(storage, index, dybase_string_type, Z_STRVAL_P(low), Z_STRLEN_P(low), lowInclusive, NULL, 0, 0, &selected_objects);
            break;
          default:
            DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
        }
    } else if (lowType == highType) {
        switch (lowType) { 
          case IS_BOOL:
            {
                zend_bool lowVal = Z_BVAL_P(low);
                zend_bool highVal = Z_BVAL_P(high);
                n_selected = dybase_index_search(storage, index, dybase_bool_type, &lowVal, 0, lowInclusive, &highVal, 0, highInclusive, &selected_objects);
            }
            break;
          case IS_LONG:
            { 
                int lowVal = Z_LVAL_P(low);
                int highVal = Z_LVAL_P(high);
               n_selected = dybase_index_search(storage, index, dybase_int_type, &lowVal, 0, lowInclusive, &highVal, 0, highInclusive, &selected_objects);
            }
            break;
          case IS_DOUBLE:
            {
                double lowVal =  Z_DVAL_P(low);
                double highVal =  Z_DVAL_P(high);
                n_selected = dybase_index_search(storage, index, dybase_real_type, &lowVal, 0, lowInclusive, &highVal, 0, highInclusive, &selected_objects);              
            }
            break;
          case IS_STRING:
            n_selected = dybase_index_search(storage, index, dybase_string_type, Z_STRVAL_P(low), Z_STRLEN_P(low), lowInclusive, Z_STRVAL_P(high), Z_STRLEN_P(high), highInclusive, &selected_objects);
            break;
          default:
            DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
        }
    } else {
        DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
    }
    if (n_selected == 0) { 
        RETURN_NULL();
    } 
    array_init(return_value);
    for (i = 0; i < n_selected; i++) { 
        add_next_index_long(return_value, selected_objects[i]);
    }
    dybase_free_selection(storage, selected_objects, n_selected);
}

ZEND_FUNCTION(dybase_dropindex)
{
    long int storage_handle;
    long int index;

    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ll", &storage_handle, &index) == FAILURE) {
        return;
    }
    dybase_drop_index((dybase_storage_t)storage_handle, (dybase_oid_t)index);
    RETURN_NULL();
}

ZEND_FUNCTION(dybase_clearindex)
{
    long int storage_handle;
    long int index;

    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ll", &storage_handle, &index) == FAILURE) {
        return;
    }
    dybase_clear_index((dybase_storage_t)storage_handle, (dybase_oid_t)index);
    RETURN_NULL();
}

ZEND_FUNCTION(dybase_createiterator)
{
    long int  storage_handle;
    zval *low, *high;
    zend_bool lowInclusive, highInclusive, ascent;    
    long int  index_oid;
    dybase_iterator_t* iterator;
    int lowType, highType;
    dybase_storage_t storage;
    dybase_oid_t index;

    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "llzbzbb", &storage_handle, &index_oid, &low, &lowInclusive, &high, &highInclusive, &ascent) == FAILURE) {
        return;
    }
    storage = (dybase_storage_t)storage_handle;
    index = (dybase_oid_t)index_oid;
    lowType = Z_TYPE_P(low);
    highType = Z_TYPE_P(high);
    if (lowType == IS_NULL) { 
        switch (highType) { 
          case IS_NULL:
            iterator = dybase_create_index_iterator(storage, index, 0, NULL, 0, 0, NULL, 0, 0, ascent);
            break;
          case IS_BOOL:
            {
                zend_bool highVal = Z_BVAL_P(high);
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, NULL, 0, 0, &highVal, 0, highInclusive, ascent);
            }
            break;
          case IS_LONG:
            { 
                int highVal = Z_LVAL_P(high);
                iterator = dybase_create_index_iterator(storage, index, dybase_int_type, NULL, 0, 0, &highVal, 0, highInclusive, ascent);
            }
            break;
          case IS_DOUBLE:
            {
                double highVal =  Z_DVAL_P(high);
                iterator = dybase_create_index_iterator(storage, index, dybase_real_type, NULL, 0, 0, &highVal, 0, highInclusive, ascent); 
            }
            break;
          case IS_STRING:
            iterator = dybase_create_index_iterator(storage, index, dybase_string_type, NULL, 0, 0, Z_STRVAL_P(high), Z_STRLEN_P(high), highInclusive, ascent);
          default:
            DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
        }
    } else if (highType == IS_NULL) { 
        switch (lowType) { 
          case IS_BOOL:
            {
                zend_bool lowVal = Z_BVAL_P(low);
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, &lowVal, 0, lowInclusive, NULL, 0, 0, ascent);
            }
            break;
          case IS_LONG:
            { 
                int lowVal = Z_LVAL_P(low);
                iterator = dybase_create_index_iterator(storage, index, dybase_int_type, &lowVal, 0, lowInclusive, NULL, 0, 0, ascent);
            }
            break;
          case IS_DOUBLE:
            {
                double lowVal =  Z_DVAL_P(low);
                iterator = dybase_create_index_iterator(storage, index, dybase_real_type, &lowVal, 0, lowInclusive,  NULL, 0, 0, ascent);   
            }
            break;
          case IS_STRING:
            iterator = dybase_create_index_iterator(storage, index, dybase_string_type, Z_STRVAL_P(low), Z_STRLEN_P(low), lowInclusive, NULL, 0, 0, ascent);
            break;
          default:
            DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
        }
    } else if (lowType == highType) {
        switch (lowType) { 
          case IS_BOOL:
            {
                zend_bool lowVal = Z_BVAL_P(low);
                zend_bool highVal = Z_BVAL_P(high);
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, &lowVal, 0, lowInclusive, &highVal, 0, highInclusive, ascent);
            }
            break;
          case IS_LONG:
            { 
                int lowVal = Z_LVAL_P(low);
                int highVal = Z_LVAL_P(high);
               iterator = dybase_create_index_iterator(storage, index, dybase_int_type, &lowVal, 0, lowInclusive, &highVal, 0, highInclusive, ascent);
            }
            break;
          case IS_DOUBLE:
            {
                double lowVal =  Z_DVAL_P(low);
                double highVal =  Z_DVAL_P(high);
                iterator = dybase_create_index_iterator(storage, index, dybase_real_type, &lowVal, 0, lowInclusive, &highVal, 0, highInclusive, ascent);              
            }
            break;
          case IS_STRING:
            iterator = dybase_create_index_iterator(storage, index, dybase_string_type, Z_STRVAL_P(low), Z_STRLEN_P(low), lowInclusive, Z_STRVAL_P(high), Z_STRLEN_P(high), highInclusive, ascent);
            break;
          default:
            DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
        }
    } else {
        DybaseErrorHandler(dybase_bad_key_type, "Invalid index key type");
    }
    RETURN_LONG((long)iterator);
}

ZEND_FUNCTION(dybase_freeiterator)
{
    long int iterator;

    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &iterator) == FAILURE) {
        return;
    }
    dybase_free_index_iterator((dybase_iterator_t)iterator);
    RETURN_NULL();
}

ZEND_FUNCTION(dybase_iteratornext)
{
    long int iterator;

    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &iterator) == FAILURE) {
        return;
    }
    RETURN_LONG(dybase_index_iterator_next((dybase_iterator_t)iterator));
}


ZEND_FUNCTION(dybase_gc)
{
    long int storage_handle;

    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "l", &storage_handle) == FAILURE) {
        return;
    }
    dybase_gc((dybase_storage_t)storage_handle);
    RETURN_NULL();
}
    
ZEND_FUNCTION(dybase_setgcthreshold)
{
    long int storage_handle;
    long int threshold;

    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ll", &storage_handle, &threshold) == FAILURE) {
        return;
    }
    dybase_set_gc_threshold((dybase_storage_t)storage_handle, threshold);
    RETURN_NULL();
}



zend_function_entry dybaseapi_functions[] = {
    ZEND_FE(dybase_open, NULL)
    ZEND_FE(dybase_close, NULL)
    ZEND_FE(dybase_commit, NULL)
    ZEND_FE(dybase_rollback, NULL)
    ZEND_FE(dybase_getroot, NULL)
    ZEND_FE(dybase_setroot, NULL)
    ZEND_FE(dybase_allocate, NULL)
    ZEND_FE(dybase_deallocate, NULL)
    ZEND_FE(dybase_beginstore, NULL)
    ZEND_FE(dybase_storereffield, NULL)
    ZEND_FE(dybase_storearrayfield, NULL)
    ZEND_FE(dybase_storefield, NULL)
    ZEND_FE(dybase_storeelem, NULL)
    ZEND_FE(dybase_storerefelem, NULL)
    ZEND_FE(dybase_storearrayelem, NULL)
    ZEND_FE(dybase_endstore, NULL)
    ZEND_FE(dybase_beginload, NULL)
    ZEND_FE(dybase_getclassname, NULL)
    ZEND_FE(dybase_nextfield, NULL)
    ZEND_FE(dybase_nextelem, NULL)
    ZEND_FE(dybase_getref, NULL)
    ZEND_FE(dybase_getvalue, NULL)
    ZEND_FE(dybase_arraylength, NULL)
    ZEND_FE(dybase_createstrindex, NULL)
    ZEND_FE(dybase_createintindex, NULL)
    ZEND_FE(dybase_createboolindex, NULL)
    ZEND_FE(dybase_createrealindex, NULL)
    ZEND_FE(dybase_insertinindex, NULL)
    ZEND_FE(dybase_removefromindex, NULL)
    ZEND_FE(dybase_searchindex, NULL)
    ZEND_FE(dybase_dropindex, NULL)
    ZEND_FE(dybase_clearindex, NULL)
    ZEND_FE(dybase_createiterator, NULL)
    ZEND_FE(dybase_freeiterator, NULL)
    ZEND_FE(dybase_iteratornext, NULL)
    ZEND_FE(dybase_gc, NULL)
    ZEND_FE(dybase_setgcthreshold, NULL)
    {NULL, NULL, NULL}
};


zend_module_entry dybaseapi_module_entry = {
	STANDARD_MODULE_HEADER,
	"dybaseapi",
	dybaseapi_functions,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NO_VERSION_YET,
	STANDARD_MODULE_PROPERTIES
};

ZEND_GET_MODULE(dybaseapi)
