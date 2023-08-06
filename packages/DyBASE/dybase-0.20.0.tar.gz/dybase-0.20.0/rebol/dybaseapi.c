#include "dybase.h"
#include <assert.h>
#include <stdlib.h>

#if defined(_WIN32)
#define DLL_ENTRY __declspec(dllexport)
#else 
#define DLL_ENTRY 
#endif

static char* str_buf = NULL;
static int   str_buf_size = 0;
static int   dybase_error;

static void error_handler(int error_code, char const* msg) 
{
    dybase_error = error_code;
}

DLL_ENTRY long rapi_open(char const* file_path, long page_pool_size)
{
    return (long)dybase_open(file_path, page_pool_size, &error_handler);
}

DLL_ENTRY void rapi_close(long db)
{
    if (str_buf != NULL) { 
        free(str_buf);
        str_buf = NULL;
        str_buf_size = 0;
    }
    dybase_close((dybase_storage_t)db);    
}

DLL_ENTRY void rapi_commit(long db)
{
    dybase_commit((dybase_storage_t)db);
}

DLL_ENTRY void rapi_rollback(long db)
{
    dybase_rollback((dybase_storage_t)db);
}

DLL_ENTRY long rapi_get_root(long db)
{
    return (long)dybase_get_root_object((dybase_storage_t)db);
}

DLL_ENTRY void rapi_set_root(long db, long root)
{
    dybase_set_root_object((dybase_storage_t)db, (dybase_oid_t)root);
}

DLL_ENTRY long rapi_allocate(long db)
{
    return (long)dybase_allocate_object((dybase_storage_t)db);
}

DLL_ENTRY void rapi_deallocate(long db, long oid)
{
    dybase_deallocate_object((dybase_storage_t)db, (dybase_oid_t)oid);
}

DLL_ENTRY long rapi_begin_store(long db, long oid, char const* class_name)
{
    return (long)dybase_begin_store_object((dybase_storage_t)db, (dybase_oid_t)oid, class_name);
}

DLL_ENTRY void rapi_store_ref_field(long handle, char const* field_name, long value)
{
    dybase_oid_t oid = (dybase_oid_t)value;
    dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_object_type, &oid, 0);
}
        
DLL_ENTRY void rapi_store_array_field(long handle, char const* field_name, int length)
{
    dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_array_type, NULL, length);
}        
    
DLL_ENTRY void rapi_store_map_field(long handle, char const* field_name, int length)
{
    dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_map_type, NULL, length);
}        
    

DLL_ENTRY void rapi_store_int_field(long handle, char const* field_name, int value)
{
    dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_int_type, &value, 0);
}        
    
DLL_ENTRY void rapi_store_real_field(long handle, char const* field_name, double value)
{
    dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_real_type, &value, 0);
}        
    
DLL_ENTRY void rapi_store_str_field(long handle, char* field_name, char* value)
{
    dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_string_type, value, strlen(value));
}        
    
DLL_ENTRY void rapi_store_bool_field(long handle, char* field_name, int value)
{
    char b = (char)value;
    dybase_store_object_field((dybase_handle_t)handle, field_name, dybase_bool_type, &b, 0);
}        
    

DLL_ENTRY void rapi_store_ref_elem(long handle, long value)
{
    dybase_oid_t oid = (dybase_oid_t)value;
    dybase_store_array_element((dybase_handle_t)handle, dybase_object_type, &oid, 0);
}

DLL_ENTRY void rapi_store_array_elem(long handle, int length)
{
    dybase_store_array_element((dybase_handle_t)handle, dybase_array_type, NULL, length);
}        
    
DLL_ENTRY void rapi_store_map_elem(long handle, int length)
{
    dybase_store_array_element((dybase_handle_t)handle, dybase_map_type, NULL, length);
}        
    

DLL_ENTRY void rapi_store_int_elem(long handle, int value)
{
    dybase_store_array_element((dybase_handle_t)handle, dybase_int_type, &value, 0);
}        
    
DLL_ENTRY void rapi_store_real_elem(long handle, double value)
{
    dybase_store_array_element((dybase_handle_t)handle, dybase_real_type, &value, 0);
}        
    
DLL_ENTRY void rapi_store_str_elem(long handle, char* value)
{
    dybase_store_array_element((dybase_handle_t)handle, dybase_string_type, value, strlen(value));
}        
    
DLL_ENTRY void rapi_store_bool_elem(long handle, int value)
{
    char b = (char)value;
    dybase_store_array_element((dybase_handle_t)handle, dybase_bool_type, &b, 0);
}        
    


DLL_ENTRY void rapi_end_store(long handle)
{
    dybase_end_store_object((dybase_handle_t)handle);
}


DLL_ENTRY long rapi_begin_load(long db, long oid)
{
    return (long)dybase_begin_load_object((dybase_storage_t)db, (dybase_oid_t)oid);
}

DLL_ENTRY char* rapi_get_class_name(long handle)
{
    return dybase_get_class_name((dybase_handle_t)handle);
}

DLL_ENTRY char* rapi_next_field(long handle)
{
    return dybase_next_field((dybase_handle_t)handle);
}
    
DLL_ENTRY void rapi_next_elem(long handle)
{
    dybase_next_element((dybase_handle_t)handle);
}
    
DLL_ENTRY int rapi_get_type(long handle)
{
    int   type;
    void* value;
    int   length;
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);   
    return type;
}

DLL_ENTRY long rapi_get_ref(long handle)
{
    int   type;
    void* value;
    int   length;
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);   
    assert(type == dybase_object_type);
    return (long)*(dybase_oid_t*)value;
}
    
DLL_ENTRY int rapi_get_int(long handle)
{
    int   type;
    void* value;
    int   length;
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);   
    assert(type == dybase_int_type);
    return *(int*)value;
}
    
DLL_ENTRY double rapi_get_real(long handle)
{
    int   type;
    void* value;
    int   length;
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);   
    assert(type == dybase_real_type);
    return *(double*)value;
}

DLL_ENTRY int rapi_get_bool(long handle)
{
    int   type;
    void* value;
    int   length;
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);   
    assert(type == dybase_bool_type);
    return *(char*)value;
}
    
DLL_ENTRY char* rapi_get_str(long handle)
{
    int   type;
    void* value;
    int   length;

    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);   
    assert(type == dybase_string_type);

    if (length >= str_buf_size) { 
        if (str_buf != NULL) { 
            free(str_buf);
        }
        str_buf = (char*)malloc(length+1);
        str_buf_size = length + 1;
    }
    memcpy(str_buf, value, length);
    str_buf[length] = '\0';
    return str_buf;
}

DLL_ENTRY int rapi_get_length(long handle)
{
    int   type;
    void* value;
    int   length;
    dybase_get_value((dybase_handle_t)handle, &type, &value, &length);   
    assert(type == dybase_array_type || type == dybase_map_type);
    return length;
}

DLL_ENTRY long rapi_create_str_index(long db, int unique)
{
    return (long)dybase_create_index((dybase_storage_t)db, dybase_string_type, unique);
}

DLL_ENTRY long rapi_create_int_index(long db, int unique)
{
    return (long)dybase_create_index((dybase_storage_t)db, dybase_int_type, unique);
}

DLL_ENTRY long rapi_create_real_index(long db, int unique)
{
    return (long)dybase_create_index((dybase_storage_t)db, dybase_real_type, unique);
}


DLL_ENTRY int rapi_insert_in_str_index(long db, long index, char* key, long value, int replace)
{
    assert(value != 0);
    return dybase_insert_in_index((dybase_handle_t)db, (dybase_oid_t)index, key, dybase_string_type,
                                  strlen(key), (dybase_oid_t)value, replace);
}

DLL_ENTRY int rapi_insert_in_int_index(long db, long index, int key, long value, int replace)
{
    assert(value != 0);
    return dybase_insert_in_index((dybase_handle_t)db, (dybase_oid_t)index, &key, dybase_int_type,
                                  0, (dybase_oid_t)value, replace);
}

DLL_ENTRY int rapi_insert_in_real_index(long db, long index, double key, long value, int replace)
{
    return dybase_insert_in_index((dybase_handle_t)db, (dybase_oid_t)index, &key, dybase_real_type,
                                  0, (dybase_oid_t)value, replace);
}

DLL_ENTRY int rapi_remove_from_str_index(long db, long index, char* key, long value)
{
    return dybase_remove_from_index((dybase_handle_t)db, (dybase_oid_t)index, key, dybase_string_type,
                                  strlen(key), (dybase_oid_t)value);
}

DLL_ENTRY int rapi_remove_from_int_index(long db, long index, int key, long value)
{
    return dybase_remove_from_index((dybase_handle_t)db, (dybase_oid_t)index, &key, dybase_int_type,
                                  0, (dybase_oid_t)value);
}

DLL_ENTRY int rapi_remove_from_real_index(long db, long index, double key, long value)
{
    return dybase_remove_from_index((dybase_handle_t)db, (dybase_oid_t)index, &key, dybase_real_type,
                                  0, (dybase_oid_t)value);
}


DLL_ENTRY void rapi_drop_index(long db, long index)
{
    dybase_drop_index((dybase_storage_t)db, (dybase_oid_t)index);
}

DLL_ENTRY void rapi_clear_index(long db, long index)
{
    dybase_clear_index((dybase_storage_t)db, (dybase_oid_t)index);
}

DLL_ENTRY long rapi_create_str_iterator(long db, long index, char* low, int low_boundary, char* high, int high_boundary, int descent)
{
    int low_len = 0;
    char* low_val = NULL;
    int high_len = 0;
    char* high_val = NULL;
    if (low_boundary) { 
        low_len = strlen(low);
        low_val = low;
    }
    if (high_boundary) { 
        high_len = strlen(high);
        high_val = high;
    }
    return (long)dybase_create_index_iterator((dybase_storage_t)db, index, dybase_string_type, low_val, low_len, 1, high_val, high_len, 1, !descent);
}

DLL_ENTRY long rapi_create_int_iterator(long db, long index, int low, int low_boundary, int high, int high_boundary, int descent)
{    
    int* low_ptr = low_boundary ? &low : NULL;
    int* high_ptr = high_boundary ? &high : NULL;
    return (long)dybase_create_index_iterator((dybase_storage_t)db, index, dybase_int_type, low_ptr, 0, 1, high_ptr, 0, 1, !descent);
}

DLL_ENTRY long rapi_create_real_iterator(long db, long index, double low, int low_boundary, double high, int high_boundary, int descent)
{    
    double* low_ptr = low_boundary ? &low : NULL;
    double* high_ptr = high_boundary ? &high : NULL;
    return (long)dybase_create_index_iterator((dybase_storage_t)db, index, dybase_real_type, low_ptr, 0, 1, high_ptr, 0, 1, !descent);
}

DLL_ENTRY void rapi_free_iterator(long iterator)
{
    dybase_free_index_iterator((dybase_iterator_t)iterator);
}

DLL_ENTRY long rapi_iterator_next(long iterator)
{
    return dybase_index_iterator_next((dybase_iterator_t)iterator);
}


DLL_ENTRY void rapi_gc(long db)
{
    dybase_gc((dybase_storage_t)db);
}
    
DLL_ENTRY void rapi_set_gc_threshold(long db, long threshold)
{
    dybase_set_gc_threshold((dybase_storage_t)db, threshold);
}
