#include "ruby.h"
#include "st.h"
#include "dybase.h"

/* Python 2.3 does not have LONG_LONG, uses PY_LONG_LONG instead */
#ifndef LONG_LONG
#define LONG_LONG PY_LONG_LONG
#endif

static void dybase_error(int error_code, char const* msg) {
    rb_raise(rb_eRuntimeError, msg);
}

typedef struct storage_struct { 
    dybase_storage_t storage;
} storage_struct;

typedef struct handle_struct {
    dybase_handle_t  handle;
} handle_struct;

typedef struct iterator_struct {
    dybase_iterator_t iterator;
} iterator_struct;


static void
free_storage(storage_struct *stp)
{
    if (stp->storage != NULL) { 
        dybase_close(stp->storage);
        stp->storage = NULL;
    }
    free(stp);
}

static void
free_iterator(iterator_struct *itp)
{
    dybase_free_index_iterator(itp->iterator);
    free(itp);
}

static VALUE
storage_s_new(VALUE clazz, VALUE file_path, VALUE page_pool_size)
{
    VALUE obj;
    storage_struct *stp;
    file_path = rb_str_to_str(file_path);
    obj = Data_Make_Struct(clazz, storage_struct, 0, free_storage, stp);
    stp->storage = dybase_open(RSTRING(file_path)->ptr, NUM2INT(page_pool_size), &dybase_error);
    return obj;
}

#define GetSTORAGE(obj, stp) \
    Data_Get_Struct(obj, storage_struct, stp); \
    if (stp->storage == NULL) rb_raise(rb_eRuntimeError, "Storage is closed")



static VALUE
storage_close(VALUE self)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    if (stp->storage != NULL) { 
        dybase_close(stp->storage);
        stp->storage = NULL;
    }
    return Qnil;    
}

static VALUE
storage_commit(VALUE self)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    dybase_commit(stp->storage);
    return Qnil;    
}

static VALUE
storage_rollback(VALUE self)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    dybase_rollback(stp->storage);
    return Qnil;    
}

static VALUE
storage_getroot(VALUE self)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    return INT2FIX(dybase_get_root_object(stp->storage));
}

static VALUE
storage_setroot(VALUE self, VALUE root)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    dybase_set_root_object(stp->storage, NUM2INT(root));
    return Qnil;    
}

static VALUE
storage_allocate(VALUE self)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    return INT2FIX(dybase_allocate_object(stp->storage));
}

static VALUE
storage_deallocate(VALUE self, VALUE oid)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    dybase_deallocate_object(stp->storage, NUM2INT(oid));
    return Qnil;    
}

static VALUE
storehandle_s_new(VALUE clazz, VALUE storage, VALUE oid, VALUE class_name)
{
    VALUE obj;
    handle_struct *htp;
    storage_struct *stp;
    GetSTORAGE(storage, stp);
    class_name = rb_str_to_str(class_name);
    obj = Data_Make_Struct(clazz, handle_struct, 0, 0, htp);
    htp->handle = dybase_begin_store_object(stp->storage, NUM2INT(oid), RSTRING(class_name)->ptr);
    return obj;
}

static VALUE
storehandle_storeref(VALUE self, VALUE field_name, VALUE ref)
{
    handle_struct *htp;
    dybase_oid_t oid = NUM2INT(ref);
    Data_Get_Struct(self, handle_struct, htp); 
    field_name = rb_str_to_str(field_name);
    dybase_store_object_field(htp->handle, RSTRING(field_name)->ptr, dybase_object_type, &oid, 0);
    return Qnil;    
}

static VALUE
storehandle_storefield(VALUE self, VALUE field_name, VALUE value)
{
    handle_struct *htp;
    Data_Get_Struct(self, handle_struct, htp); 
    field_name = rb_str_to_str(field_name);
    switch (TYPE(value)) { 
      case T_FLOAT:
        {
            double d = NUM2DBL(value);
            dybase_store_object_field(htp->handle, RSTRING(field_name)->ptr, dybase_real_type, &d, 0);
            break;
        }
      case T_FIXNUM:
        {
            int i = FIX2INT(value);
            dybase_store_object_field(htp->handle, RSTRING(field_name)->ptr, dybase_int_type, &i, 0);
            break;
        }
      case T_TRUE:
        {
            char b = 1;
            dybase_store_object_field(htp->handle, RSTRING(field_name)->ptr, dybase_bool_type, &b, 0);
            break;
        }
      case T_FALSE:
        {
            char b = 0;
            dybase_store_object_field(htp->handle, RSTRING(field_name)->ptr, dybase_bool_type, &b, 0);
            break;
        }
      case T_STRING:
        dybase_store_object_field(htp->handle, RSTRING(field_name)->ptr, dybase_string_type, 
                                  RSTRING(value)->ptr, RSTRING(value)->len);
         break;
      case T_ARRAY:
        dybase_store_object_field(htp->handle, RSTRING(field_name)->ptr, dybase_array_type, 
                                  NULL, RARRAY(value)->len);
	break;
      case T_HASH:
        dybase_store_object_field(htp->handle, RSTRING(field_name)->ptr, dybase_map_type, 
                                  NULL, RHASH(value)->tbl->num_entries);
	break;
    }
    return Qnil;    
}

static VALUE
storehandle_storeelem(VALUE self, VALUE value)
{
    handle_struct *htp;
    Data_Get_Struct(self, handle_struct, htp); 
    switch (TYPE(value)) { 
      case T_FLOAT:
        {
            double d = NUM2DBL(value);
            dybase_store_array_element(htp->handle, dybase_real_type, &d, 0);
            break;
        }
      case T_FIXNUM:
        {
            int i = FIX2INT(value);
            dybase_store_array_element(htp->handle, dybase_int_type, &i, 0);
            break;
        }
      case T_TRUE:
        {
            char b = 1;
            dybase_store_array_element(htp->handle, dybase_bool_type, &b, 0);
            break;
        }
      case T_FALSE:
        {
            char b = 0;
            dybase_store_array_element(htp->handle, dybase_bool_type, &b, 0);
            break;
        }
      case T_STRING:
        dybase_store_array_element(htp->handle, dybase_string_type, RSTRING(value)->ptr, RSTRING(value)->len);
        break;
      case T_ARRAY:
        dybase_store_array_element(htp->handle, dybase_array_type, NULL, RARRAY(value)->len);
	break;
      case T_HASH:
        dybase_store_array_element(htp->handle, dybase_map_type, NULL, RHASH(value)->tbl->num_entries);
	break;
    }
    return Qnil;    
}

static VALUE
storehandle_storerefelem(VALUE self, VALUE ref)
{
    handle_struct *htp;
    dybase_oid_t oid = NUM2INT(ref);
    Data_Get_Struct(self, handle_struct, htp); 
    dybase_store_array_element(htp->handle, dybase_object_type, &oid, 0);
    return Qnil;    
}

static VALUE
storehandle_endstore(VALUE self)
{
    handle_struct *htp;
    Data_Get_Struct(self, handle_struct, htp); 
    dybase_end_store_object(htp->handle);
    return Qnil;    
}



static VALUE
loadhandle_s_new(VALUE clazz, VALUE storage, VALUE oid)
{
    VALUE obj;
    handle_struct *htp;
    storage_struct *stp;
    GetSTORAGE(storage, stp);
    obj = Data_Make_Struct(clazz, handle_struct, 0, 0, htp);
    htp->handle = dybase_begin_load_object(stp->storage, NUM2INT(oid));
    return obj;
}

static VALUE
loadhandle_getclassname(VALUE self) 
{
    handle_struct *htp;
    Data_Get_Struct(self, handle_struct, htp); 
    return rb_str_new2(dybase_get_class_name(htp->handle));
}

static VALUE
loadhandle_nextfield(VALUE self) 
{
    handle_struct *htp;
    char* fieldName;
    Data_Get_Struct(self, handle_struct, htp); 
    fieldName = dybase_next_field(htp->handle);
    return (fieldName == NULL) ? Qnil : rb_str_new2(fieldName);
}

static VALUE
loadhandle_nextelem(VALUE self) 
{
    handle_struct *htp;
    Data_Get_Struct(self, handle_struct, htp); 
    dybase_next_element(htp->handle);
    return Qnil;
}

static VALUE
loadhandle_getref(VALUE self) 
{
    handle_struct *htp;
    int type;
    void* value;
    int length;
    Data_Get_Struct(self, handle_struct, htp); 
    dybase_get_value(htp->handle, &type, &value, &length);
    if (type != dybase_object_type) {
        return Qnil;
    }
    return INT2FIX(*(dybase_oid_t*)value);
}
    
static VALUE
loadhandle_getvalue(VALUE self) 
{
    handle_struct *htp;
    int type;
    void* value;
    int length;
    Data_Get_Struct(self, handle_struct, htp); 
    dybase_get_value(htp->handle, &type, &value, &length);
    switch (type) { 
      case dybase_bool_type:
        return *(char*)value ? Qtrue : Qfalse;  
      case dybase_int_type:
        return INT2FIX(*(int*)value);  
      case dybase_real_type:
        return rb_float_new(*(double*)value);  
      case dybase_string_type:
        return rb_str_new((char*)value, length);
      default:
        return Qnil;
    }
}
    
static VALUE
loadhandle_arraylength(VALUE self) 
{
    handle_struct *htp;
    int type;
    void* value;
    int length;
    Data_Get_Struct(self, handle_struct, htp); 
    dybase_get_value(htp->handle, &type, &value, &length);
    if (type != dybase_array_type) {
        return Qnil;
    }
    return INT2FIX(length);
}
    
static VALUE
loadhandle_hashlength(VALUE self) 
{
    handle_struct *htp;
    int type;
    void* value;
    int length;
    Data_Get_Struct(self, handle_struct, htp); 
    dybase_get_value(htp->handle, &type, &value, &length);
    if (type != dybase_map_type) {
        return Qnil;
    }
    return INT2FIX(length);
}
    
static VALUE
storage_createstrindex(VALUE self, VALUE unique)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    return INT2FIX(dybase_create_index(stp->storage, dybase_string_type, unique != Qfalse));
}

static VALUE
storage_createintindex(VALUE self, VALUE unique)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    return INT2FIX(dybase_create_index(stp->storage, dybase_int_type, unique != Qfalse));
}

static VALUE
storage_createboolindex(VALUE self, VALUE unique)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    return INT2FIX(dybase_create_index(stp->storage, dybase_bool_type, unique != Qfalse));
}

static VALUE
storage_createrealindex(VALUE self, VALUE unique)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    return INT2FIX(dybase_create_index(stp->storage, dybase_real_type, unique != Qfalse));
}

static VALUE
storage_insertinindex(VALUE self, VALUE index, VALUE key, VALUE obj, VALUE replace)
{
    int result = 0;
    storage_struct *stp;
    dybase_oid_t indexOid = (dybase_oid_t)NUM2INT(index);
    dybase_oid_t objOid = (dybase_oid_t)NUM2INT(obj);
    GetSTORAGE(self, stp);

    switch (TYPE(key)) { 
      case T_FLOAT:
        {
            double d = NUM2DBL(key);
            result = dybase_insert_in_index(stp->storage, indexOid, &d, dybase_real_type, 0, objOid, replace != Qfalse);
            break;
        }
      case T_FIXNUM:
        {
            int i = (int)NUM2INT(key);
            result = dybase_insert_in_index(stp->storage, indexOid, &i, dybase_int_type, 0, objOid, replace != Qfalse);
            break;
        }
      case T_TRUE:
        {
            char b = 1;
            result = dybase_insert_in_index(stp->storage, indexOid, &b, dybase_bool_type, 0, objOid, replace != Qfalse);
            break;
        }
      case T_FALSE:
        {
            char b = 0;
            result = dybase_insert_in_index(stp->storage, indexOid, &b, dybase_bool_type, 0, objOid, replace != Qfalse);
            break;
        }
      case T_STRING:
        result = dybase_insert_in_index(stp->storage, indexOid, RSTRING(key)->ptr, dybase_string_type, RSTRING(key)->len, objOid, replace != Qfalse);
        break;
    }
    return result ? Qtrue : Qfalse;
}

static VALUE
storage_removefromindex(VALUE self, VALUE index, VALUE key, VALUE obj)
{
    int result = 0;
    storage_struct *stp;
    dybase_oid_t indexOid = (dybase_oid_t)NUM2INT(index);
    dybase_oid_t objOid = NIL_P(obj) ? 0 : (dybase_oid_t)NUM2INT(obj);
    GetSTORAGE(self, stp);

    switch (TYPE(key)) { 
      case T_FLOAT:
        {
            double d = NUM2DBL(key);
            result = dybase_remove_from_index(stp->storage, indexOid, &d, dybase_real_type, 0, objOid);
            break;
        }
      case T_FIXNUM:
        {
            int i = (int)NUM2INT(key);
            result = dybase_remove_from_index(stp->storage, indexOid, &i, dybase_int_type, 0, objOid);
            break;
        }
      case T_TRUE:
        {
            char b = 1;
            result = dybase_remove_from_index(stp->storage, indexOid, &b, dybase_bool_type, 0, objOid);
            break;
        }
      case T_FALSE:
        {
            char b = 0;
            result = dybase_remove_from_index(stp->storage, indexOid, &b, dybase_bool_type, 0, objOid);
            break;
        }
      case T_STRING:
        result = dybase_remove_from_index(stp->storage, indexOid, RSTRING(key)->ptr, dybase_string_type, 
                                          RSTRING(key)->len, objOid);
        break;
    }
    return result ? Qtrue : Qfalse;
}


static VALUE
storage_searchindex(VALUE self, VALUE indexOid, VALUE low, VALUE low_inclusion, VALUE high, VALUE high_inclusion)
{
    storage_struct *stp;
    dybase_oid_t index = (dybase_oid_t)NUM2INT(indexOid);
    int lowInclusion = low_inclusion != Qfalse;
    int highInclusion = high_inclusion != Qfalse;
    int i, n_selected = 0;
    dybase_storage_t storage;
    dybase_oid_t* selected_objects;
    VALUE result;
    GetSTORAGE(self, stp);
    storage = stp->storage;
    
    switch (TYPE(low)) { 
      case T_NIL:
        switch (TYPE(high)) { 
          case T_NIL:
            n_selected = dybase_index_search(storage, index, 0, NULL, 0, 0, NULL, 0, 0, &selected_objects);
            break;
          case T_FLOAT:
            {
                double highVal = NUM2DBL(high);
                n_selected = dybase_index_search(storage, index, dybase_real_type, NULL, 0, 0, &highVal, 0, highInclusion, &selected_objects);            
                break;
            }
          case T_FIXNUM:
            {
                int highVal = (int)NUM2INT(high);
                n_selected = dybase_index_search(storage, index, dybase_int_type, NULL, 0, 0, &highVal, 0, highInclusion, &selected_objects);            
                break;
            }
          case T_TRUE:
            {
                char highVal = 1;
                n_selected = dybase_index_search(storage, index, dybase_bool_type, NULL, 0, 0, &highVal, 0, highInclusion, &selected_objects);            
                break;
            }
          case T_FALSE:
            {
                char highVal = 0;
                n_selected = dybase_index_search(storage, index, dybase_bool_type, NULL, 0, 0, &highVal, 0, highInclusion, &selected_objects);            
                break;
            }
          case T_STRING:
            {
                n_selected = dybase_index_search(storage, index, dybase_string_type, NULL, 0, 0, RSTRING(high)->ptr, RSTRING(high)->len, highInclusion, &selected_objects);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;

      case T_FLOAT:
        switch (TYPE(high)) { 
          case T_NIL:
            {
                double lowVal = NUM2DBL(low);
                n_selected = dybase_index_search(storage, index, dybase_real_type, &lowVal, 0, lowInclusion, NULL, 0, 0, &selected_objects);            
                break;
            }
          case T_FLOAT:
            {
                double lowVal = NUM2DBL(low);
                double highVal = NUM2DBL(high);
                n_selected = dybase_index_search(storage, index, dybase_real_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, &selected_objects);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;
        
      case T_FIXNUM:
        switch (TYPE(high)) { 
          case T_NIL:
            {
                int lowVal = (int)NUM2INT(low);
                n_selected = dybase_index_search(storage, index, dybase_int_type, &lowVal, 0, lowInclusion, NULL, 0, 0, &selected_objects);            
                break;
            }
          case T_FIXNUM:
            {
                int lowVal = (int)NUM2INT(low);
                int highVal = (int)NUM2INT(high);
                n_selected = dybase_index_search(storage, index, dybase_int_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, &selected_objects);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;
        
      case T_TRUE:
        switch (TYPE(high)) { 
          case T_NIL:
            {
                char lowVal = 1;
                n_selected = dybase_index_search(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, NULL, 0, 0, &selected_objects);            
                break;
            }
          case T_TRUE:
            {
                char lowVal = 1;
                char highVal = 1;
                n_selected = dybase_index_search(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, &selected_objects);            
                break;
            }
          case T_FALSE:
            {
                char lowVal = 1;
                char highVal = 0;
                n_selected = dybase_index_search(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, &selected_objects);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;

      case T_FALSE:
        switch (TYPE(high)) { 
          case T_NIL:
            {
                char lowVal = 0;
                n_selected = dybase_index_search(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, NULL, 0, 0, &selected_objects);            
                break;
            }
          case T_TRUE:
            {
                char lowVal = 0;
                char highVal = 1;
                n_selected = dybase_index_search(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, &selected_objects);            
                break;
            }
          case T_FALSE:
            {
                char lowVal = 0;
                char highVal = 0;
                n_selected = dybase_index_search(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, &selected_objects);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;
      
      case T_STRING:
        switch (TYPE(high)) { 
          case T_NIL:
            {
                n_selected = dybase_index_search(storage, index, dybase_string_type, RSTRING(low)->ptr, RSTRING(low)->len, lowInclusion, NULL, 0, 0, &selected_objects);            
                break;
            }
          case T_STRING:
            {
                n_selected = dybase_index_search(storage, index, dybase_string_type, RSTRING(low)->ptr, RSTRING(low)->len, lowInclusion, RSTRING(high)->ptr, RSTRING(high)->len, highInclusion, &selected_objects);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;

      default:
        rb_raise(rb_eRuntimeError, "Invalid key type");
    }
    if (n_selected == 0) { 
        return Qnil;
    } 
    result = rb_ary_new2(n_selected);
    for (i = 0; i < n_selected; i++) { 
        rb_ary_store(result, i, INT2FIX(selected_objects[i]));
    }
    dybase_free_selection(storage, selected_objects, n_selected);
    return result;
}

static VALUE
storage_dropindex(VALUE self, VALUE index)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    dybase_drop_index(stp->storage, (dybase_oid_t)NUM2INT(index));
    return Qnil;
}

static VALUE
storage_clearindex(VALUE self, VALUE index)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    dybase_clear_index(stp->storage, (dybase_oid_t)NUM2INT(index));
    return Qnil;
}

static VALUE
iterator_s_new(VALUE clazz, VALUE storageHandle, VALUE indexOid, VALUE low, VALUE low_inclusion, VALUE high, VALUE high_inclusion, VALUE ascentOrder)
{
    VALUE obj;
    iterator_struct *itp;
    storage_struct *stp;
    dybase_oid_t index = (dybase_oid_t)NUM2INT(indexOid);
    dybase_iterator_t iterator = NULL;
    int lowInclusion = low_inclusion != Qfalse;
    int highInclusion = high_inclusion != Qfalse;
    int ascent = ascentOrder != Qfalse;
    dybase_storage_t storage;
    GetSTORAGE(storageHandle, stp);
    storage = stp->storage;
    
    switch (TYPE(low)) { 
      case T_NIL:
        switch (TYPE(high)) { 
          case T_NIL:
            iterator = dybase_create_index_iterator(storage, index, 0, NULL, 0, 0, NULL, 0, 0, ascent);
            break;
          case T_FLOAT:
            {
                double highVal = NUM2DBL(high);
                iterator = dybase_create_index_iterator(storage, index, dybase_real_type, NULL, 0, 0, &highVal, 0, highInclusion, ascent);            
                break;
            }
          case T_FIXNUM:
            {
                int highVal = (int)NUM2INT(high);
                iterator = dybase_create_index_iterator(storage, index, dybase_int_type, NULL, 0, 0, &highVal, 0, highInclusion, ascent);            
                break;
            }
          case T_TRUE:
            {
                char highVal = 1;
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, NULL, 0, 0, &highVal, 0, highInclusion, ascent);            
                break;
            }
          case T_FALSE:
            {
                char highVal = 0;
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, NULL, 0, 0, &highVal, 0, highInclusion, ascent);            
                break;
            }
          case T_STRING:
            {
                iterator = dybase_create_index_iterator(storage, index, dybase_string_type, NULL, 0, 0, RSTRING(high)->ptr, RSTRING(high)->len, highInclusion, ascent);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;

      case T_FLOAT:
        switch (TYPE(high)) { 
          case T_NIL:
            {
                double lowVal = NUM2DBL(low);
                iterator = dybase_create_index_iterator(storage, index, dybase_real_type, &lowVal, 0, lowInclusion, NULL, 0, 0, ascent);            
                break;
            }
          case T_FLOAT:
            {
                double lowVal = NUM2DBL(low);
                double highVal = NUM2DBL(high);
                iterator = dybase_create_index_iterator(storage, index, dybase_real_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, ascent);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;
        
      case T_FIXNUM:
        switch (TYPE(high)) { 
          case T_NIL:
            {
                int lowVal = (int)NUM2INT(low);
                iterator = dybase_create_index_iterator(storage, index, dybase_int_type, &lowVal, 0, lowInclusion, NULL, 0, 0, ascent);            
                break;
            }
          case T_FIXNUM:
            {
                int lowVal = (int)NUM2INT(low);
                int highVal = (int)NUM2INT(high);
                iterator = dybase_create_index_iterator(storage, index, dybase_int_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, ascent);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;
        
      case T_TRUE:
        switch (TYPE(high)) { 
          case T_NIL:
            {
                char lowVal = 1;
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, NULL, 0, 0, ascent);            
                break;
            }
          case T_TRUE:
            {
                char lowVal = 1;
                char highVal = 1;
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, ascent);            
                break;
            }
          case T_FALSE:
            {
                char lowVal = 1;
                char highVal = 0;
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, ascent);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;

      case T_FALSE:
        switch (TYPE(high)) { 
          case T_NIL:
            {
                char lowVal = 0;
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, NULL, 0, 0, ascent);            
                break;
            }
          case T_TRUE:
            {
                char lowVal = 0;
                char highVal = 1;
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, ascent);            
                break;
            }
          case T_FALSE:
            {
                char lowVal = 0;
                char highVal = 0;
                iterator = dybase_create_index_iterator(storage, index, dybase_bool_type, &lowVal, 0, lowInclusion, &highVal, 0, highInclusion, ascent);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;
      
      case T_STRING:
        switch (TYPE(high)) { 
          case T_NIL:
            {
                iterator = dybase_create_index_iterator(storage, index, dybase_string_type, RSTRING(low)->ptr, RSTRING(low)->len, lowInclusion, NULL, 0, 0, ascent);            
                break;
            }
          case T_STRING:
            {
                iterator = dybase_create_index_iterator(storage, index, dybase_string_type, RSTRING(low)->ptr, RSTRING(low)->len, lowInclusion, RSTRING(high)->ptr, RSTRING(high)->len, highInclusion, ascent);            
                break;
            }
          default:
            rb_raise(rb_eRuntimeError, "Invalid key type");
        }
        break;

      default:
        rb_raise(rb_eRuntimeError, "Invalid key type");
    }
    obj = Data_Make_Struct(clazz, iterator_struct, 0, free_iterator, itp);
    itp->iterator = iterator;
    return obj;
}

static VALUE
iterator_next(VALUE iterator)
{
    iterator_struct *itp;
    Data_Get_Struct(iterator, iterator_struct, itp);
    return INT2FIX(dybase_index_iterator_next(itp->iterator));
}


static VALUE
storage_gc(VALUE self)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    dybase_gc(stp->storage);
    return Qnil;
}

static VALUE
storage_setgcthreshold(VALUE self, VALUE threshold)
{
    storage_struct *stp;
    GetSTORAGE(self, stp);
    dybase_set_gc_threshold(stp->storage, NUM2INT(threshold));
    return Qnil;
}

static VALUE
ruby_ivar_set(VALUE self, VALUE obj, VALUE field, VALUE value)
{
    return rb_ivar_set(obj, rb_to_id(field), value);
}

static VALUE
ruby_ivar_get(VALUE self, VALUE obj, VALUE field)
{
    return rb_ivar_get(obj, rb_to_id(field));
}

static VALUE
ruby_new_instance(VALUE self, VALUE class_name)
{
    VALUE klass, obj;

    class_name = rb_str_to_str(class_name);
    klass = rb_path2class(RSTRING(class_name)->ptr);
    if (TYPE(klass) != T_CLASS) {
        rb_raise(rb_eArgError, "Class not found");
    }
    obj = rb_obj_alloc(klass);
    if (TYPE(obj) != T_OBJECT) {
        rb_raise(rb_eArgError, "Failed to create obejct instance");
    }
    return obj;
}

#ifdef _WIN32
 __declspec(dllexport)
#endif
void
Init_dybaseapi()
{
    VALUE mDybase, cStorage, cLoadHandle, cStoreHandle, cIterator;
    mDybase = rb_define_module("Dybaseapi");
    rb_define_module_function(mDybase, "ivar_set", ruby_ivar_set, 3);
    rb_define_module_function(mDybase, "ivar_get", ruby_ivar_get, 2);
    rb_define_module_function(mDybase, "new_instance", ruby_new_instance, 1);

    cStorage = rb_define_class_under(mDybase, "StorageImpl", rb_cObject);
    rb_define_singleton_method(cStorage, "new", storage_s_new, 2);
    rb_define_method(cStorage, "commit", storage_commit, 0);
    rb_define_method(cStorage, "rollback", storage_rollback, 0);
    rb_define_method(cStorage, "allocate", storage_allocate, 0);
    rb_define_method(cStorage, "deallocate", storage_deallocate, 1);
    rb_define_method(cStorage, "getroot", storage_getroot, 0);
    rb_define_method(cStorage, "setroot", storage_setroot, 1);
    rb_define_method(cStorage, "createstrindex", storage_createstrindex, 1);
    rb_define_method(cStorage, "createintindex", storage_createintindex, 1);
    rb_define_method(cStorage, "createboolindex", storage_createboolindex, 1);
    rb_define_method(cStorage, "createrealindex", storage_createrealindex, 1);
    rb_define_method(cStorage, "insertinindex", storage_insertinindex, 4);
    rb_define_method(cStorage, "removefromindex", storage_removefromindex, 3);
    rb_define_method(cStorage, "searchindex", storage_searchindex, 5);
    rb_define_method(cStorage, "dropindex", storage_dropindex, 1);
    rb_define_method(cStorage, "clearindex", storage_clearindex, 1);
    rb_define_method(cStorage, "close", storage_close, 0);
    rb_define_method(cStorage, "gc", storage_gc, 0);
    rb_define_method(cStorage, "setgcthreshold", storage_setgcthreshold, 1);

    cIterator = rb_define_class_under(mDybase, "Iterator", rb_cObject);
    rb_define_singleton_method(cIterator, "new", iterator_s_new, 7);
    rb_define_method(cIterator, "next", iterator_next, 0);
    

    cLoadHandle = rb_define_class_under(mDybase, "LoadHandle", rb_cObject);
    rb_define_singleton_method(cLoadHandle, "new", loadhandle_s_new, 2);
    rb_define_method(cLoadHandle, "getclassname", loadhandle_getclassname, 0);
    rb_define_method(cLoadHandle, "nextfield", loadhandle_nextfield, 0);
    rb_define_method(cLoadHandle, "nextelem", loadhandle_nextelem, 0);
    rb_define_method(cLoadHandle, "getref", loadhandle_getref, 0);
    rb_define_method(cLoadHandle, "getvalue", loadhandle_getvalue, 0);
    rb_define_method(cLoadHandle, "arraylength", loadhandle_arraylength, 0);
    rb_define_method(cLoadHandle, "hashlength", loadhandle_hashlength, 0);

    cStoreHandle = rb_define_class_under(mDybase, "StoreHandle", rb_cObject);
    rb_define_singleton_method(cStoreHandle, "new", storehandle_s_new, 3);
    rb_define_method(cStoreHandle, "storereffield", storehandle_storeref, 2);
    rb_define_method(cStoreHandle, "storefield", storehandle_storefield, 2);
    rb_define_method(cStoreHandle, "storeelem", storehandle_storeelem, 1);
    rb_define_method(cStoreHandle, "storerefelem", storehandle_storerefelem, 1);
    rb_define_method(cStoreHandle, "endstore", storehandle_endstore, 0);
}
