REBOL [
    Title: "DyBASE Rebol API"
    File:  %dybase.r
    Author: "knizhnik@garret.ru"
    Date:  9-Dec-2003
    Version: 1.1
    Purpose: {
        Provide Rebol API to DyBASE object oriented embedded database
    }
]

dybase-lib-path: %dybaseapi
dybaselib: load/library dybase-lib-path


dybase_open: make routine! [
    "Open database"
    file-path [string!] "Path to database file"
    page-pool-size [long] "Page pool size"
    return: [long]
] dybaselib "rapi_open"

dybase_iterator_next: make routine! [
    "Next iterator element"
    iterator [long] "Iterator handler"
    return: [long]
] dybaselib "rapi_iterator_next"

dybase_free_iterator: make routine! [
    "Deallocate iterator"
    iterator [long] "Iterator handler"
] dybaselib "rapi_free_iterator"

dybase_drop_index: make routine! [
    "Drop index"
    db [long] "Database handler"
    index [long] "Index OID"
] dybaselib "rapi_drop_index"

dybase_clear_index: make routine! [
    "Clear index"
    db [long] "Database handler"
    index [long] "Index OID"
] dybaselib "rapi_clear_index"

dybase_insert_in_str_index: make routine! [
    "Insert new element in string index"
    db [long] "Database handler"
    index [long] "Index OID"
    key [char*] "Object key"
    oid [long] "Object OID"
    replace [int] "Replace existed value"
    return: [int] "1 if key is successfully added, 0 if such key already exists in unique index"
] dybaselib "rapi_insert_in_str_index"

dybase_remove_from_str_index: make routine! [
    "Remove element from string index"
    db [long] "Database handler"
    index [long] "Index OID"
    key [char*] "Object key"
    oid [long] "Object OID"
    return: [int] "0 if key is not present in index, non zero values otherwise"
] dybaselib "rapi_remove_from_str_index"

dybase_create_str_iterator: make routine! [
    "Create iterator for object which key belongs to the specified range"
    db [long] "Database handler"
    index [long] "Index OID"
    low [char*] "Low inclusive boundary or none"
    low-boundary [int] "Low boundary present"
    high [char*] "High inclusive boundary or none"
    high-boundary [int] "High boundary present"
    descent [int] "Descent order"
    return: [long] "Iterator handler"
] dybaselib "rapi_create_str_iterator"

dybase_insert_in_int_index: make routine! [
    "Insert new element in integer index"
    db [long] "Database handler"
    index [long] "Index OID"
    key [int] "Object key"
    oid [long] "Object OID"
    replace [int] "Replace existed value"
    return: [int] "1 if key is successfully added, 0 if such key already exists in unique index"
] dybaselib "rapi_insert_in_int_index"

dybase_remove_from_int_index: make routine! [
    "Remove element from integer index"
    db [long] "Database handler"
    index [long] "Index OID"
    key [int] "Object key"
    oid [long] "Object OID"
    return: [int] "0 if key is not present in index, non zero values otherwise"
] dybaselib "rapi_remove_from_int_index"

dybase_create_int_iterator: make routine! [
    "Create iterator for object which key belongs to the specified range"
    db [long] "Database handler"
    index [long] "Index OID"
    low [int] "Low inclusive boundary or none"
    low-boundary [int] "Low boundary present"
    high [int] "High inclusive boundary or none"
    high-boundary [int] "High boundary present"
    descent [int] "Descent order"
    return: [long] "Iterator handler"
] dybaselib "rapi_create_int_iterator"

dybase_insert_in_real_index: make routine! [
    "Insert new element in decimal index"
    db [long] "Database handler"
    index [long] "Index OID"
    key [double] "Object key"
    oid [long] "Object OID"
    replace [int] "Replace existed value"
    return: [int] "1 if key is successfully added, 0 if such key already exists in unique index"
] dybaselib "rapi_insert_in_real_index"

dybase_remove_from_real_index: make routine! [
    "Remove element from decimal index"
    db [long] "Database handler"
    index [long] "Index OID"
    key [double] "Object key"
    oid [long] "Object OID"
    return: [int] "0 if key is not present in index, non zero values otherwise"
] dybaselib "rapi_remove_from_real_index"

dybase_create_real_iterator: make routine! [
    "Create iterator for object which key belongs to the specified range"
    db [long] "Database handler"
    index [long] "Index OID"
    low [double] "Low inclusive boundary or none"
    low-boundary [int] "Low boundary present"
    high [double] "High inclusive boundary or none"
    high-boundary [int] "High boundary present"
    descent [int] "Descent order"
    return: [long] "Iterator handler"
] dybaselib "rapi_create_real_iterator"

dybase_close: make routine! [
    "Close database"
    db [long] "Database handler"
] dybaselib "rapi_close"

dybase_commit: make routine! [
    "Commit transaction"
    db [long] "Database handler"
] dybaselib "rapi_commit"

dybase_rollback: make routine! [
    "Rollback transaction"
    db [long] "Database handler"
] dybaselib "rapi_rollback"

dybase_get_root: make routine! [
    "Get database root object"
    db [long] "Database handler"
    return: [long] "OID of root object"
] dybaselib "rapi_get_root"

dybase_set_root: make routine! [
    "Set database root object"
    db [long] "Database handler"
    root [long] "OID of root object"
] dybaselib "rapi_set_root"

dybase_deallocate: make routine! [
    "Deallocate object from the database"
    db [long] "Database handler"
    oid [long] "OID of deallocated object"
] dybaselib "rapi_deallocate"

dybase_allocate: make routine! [
    "Allocate object in the database"
    db [long] "Database handler"
    return: [long] "OID of allocated object"
] dybaselib "rapi_allocate"

dybase_begin_store: make routine! [
    "Store object in the database"
    db [long] "Database handler"
    oid [long] "OID of stored object"
    class-name [char*] "Object class name"
    return: [long] "Store handler"
] dybaselib "rapi_begin_store"

dybase_store_ref_field: make routine! [
    "Store object reference field in the database"
    hnd [long] "Store handler"
    field [char*] "Name od stored field"
    oid [long] "OID of referenced object"
] dybaselib "rapi_store_ref_field"

dybase_store_int_field: make routine! [
    "Store object integer field in the database"
    hnd [long] "Store handler"
    field [char*] "Name od stored field"
    value [int] "Field value"
] dybaselib "rapi_store_int_field"

dybase_store_bool_field: make routine! [
    "Store object integer field in the database"
    hnd [long] "Store handler"
    field [char*] "Name od stored field"
    value [int] "Field value: 0 - false, 1 - true"
] dybaselib "rapi_store_bool_field"

dybase_store_real_field: make routine! [
    "Store object integer field in the database"
    hnd [long] "Store handler"
    field [char*] "Name od stored field"
    value [double] "Field value"
] dybaselib "rapi_store_real_field"

dybase_store_str_field: make routine! [
    "Store object string field in the database"
    hnd [long] "Store handler"
    field [char*] "Name od stored field"
    value [char*] "Field value"
] dybaselib "rapi_store_str_field"

dybase_store_array_field: make routine! [
    "Store object block field in the database"
    hnd [long] "Store handler"
    field [char*] "Name od stored field"
    len [int] "Block length"
] dybaselib "rapi_store_array_field"

dybase_store_map_field: make routine! [
    "Store object hash field in the database"
    hnd [long] "Store handler"
    field [char*] "Name od stored field"
    len [int] "Number of pairs in hash"
] dybaselib "rapi_store_map_field"

dybase_end_store: make routine! [
    "End storing of object fields"
    hnd [long] "Store handler"
] dybaselib "rapi_end_store"

dybase_create_str_index: make routine! [
    "Create string index"
    db [long] "Database handler"
    unique [int] "If index is unique"
    return: [long] "OID of created index"
] dybaselib "rapi_create_str_index"

dybase_create_int_index: make routine! [
    "Create integer index"
    db [long] "Database handler"
    unique [int] "If index is unique"
    return: [long] "OID of created index"
] dybaselib "rapi_create_int_index"

dybase_create_real_index: make routine! [
    "Create decimal index"
    db [long] "Database handler"
    unique [int] "If index is unique"
    return: [long] "OID of created index"
] dybaselib "rapi_create_real_index"

dybase_gc: make routine! [
    "Perform garbage collection in database"
    db [long] "Database handler"
] dybaselib "rapi_gc"

dybase_set_gc_threshold: make routine! [
    "Set garbage collection threshold"
    db [long] "Database handler"
    threshold [long] "gc threshold"
] dybaselib "rapi_set_gc_threshold"


dybase_begin_load: make routine! [
    "Begin object loading"
    db [long] "Database handler"
    oid [long] "Object OID"
    return: [long] "Load handler"
] dybaselib "rapi_begin_load"

dybase_get_class_name:  make routine! [
    "Get loaded object class name"
    hnd [long] "Load handler"
    return: [char*] "Class name"
] dybaselib "rapi_get_class_name"

dybase_next_field: make routine! [
    "Get next object field"
    hnd [long] "Load handler"
    return: [char*] "field name or none if there are no more fields"
] dybaselib "rapi_next_field"

dybase_next_elem: make routine! [
    "Get next array or map element"
    hnd [long] "Load handler"
] dybaselib "rapi_next_elem"

dybase_get_type: make routine! [
    "Get component type"
    hnd [long] "Load handler"
    return: [int] "Dybase type code"
] dybaselib "rapi_get_type"

dybase_get_ref: make routine! [
    "Get value of reference component"
    hnd [long] "Load handler"
    return: [long] "OID"
] dybaselib "rapi_get_ref"

dybase_get_bool: make routine! [
    "Get value of logic component"
    hnd [long] "Load handler"
    return: [int] "o - false, 1 - true"
] dybaselib "rapi_get_bool"

dybase_get_int: make routine! [
    "Get value of integer component"
    hnd [long] "Load handler"
    return: [int] "integer value"
] dybaselib "rapi_get_int"

dybase_get_real: make routine! [
    "Get value of decimal component"
    hnd [long] "Load handler"
    return: [double] "decimal value"
] dybaselib "rapi_get_real"

dybase_get_str: make routine! [
    "Get value of string component"
    hnd [long] "Load handler"
    return: [char*] "string value"
] dybaselib "rapi_get_str"

dybase_get_length: make routine! [
    "Get length of array or map component"
    hnd [long] "Load handler"
    return: [int] "hash or block length"
] dybaselib "rapi_get_length"


dybase_store_ref_elem: make routine! [
    "Store object reference element in the database"
    hnd [long] "Store handler"
    oid [long] "OID of referenced object"
] dybaselib "rapi_store_ref_elem"

dybase_store_int_elem: make routine! [
    "Store object integer element in the database"
    hnd [long] "Store handler"
    value [int] "Elem value"
] dybaselib "rapi_store_int_elem"

dybase_store_bool_elem: make routine! [
    "Store object integer element in the database"
    hnd [long] "Store handler"
    value [int] "Elem value: 0 - false, 1 - true"
] dybaselib "rapi_store_bool_elem"

dybase_store_real_elem: make routine! [
    "Store object integer element in the database"
    hnd [long] "Store handler"
    value [double] "Elem value"
] dybaselib "rapi_store_real_elem"

dybase_store_str_elem: make routine! [
    "Store object string element in the database"
    hnd [long] "Store handler"
    value [char*] "Elem value"
] dybaselib "rapi_store_str_elem"

dybase_store_array_elem: make routine! [
    "Store object block element in the database"
    hnd [long] "Store handler"
    len [int] "Block length"
] dybaselib "rapi_store_array_elem"

dybase_store_map_elem: make routine! [
    "Store object hash element in the database"
    hnd [long] "Store handler"
    len [int] "Number of pairs in hash"
] dybaselib "rapi_store_map_elem"

; ------------------------------------------------------------

load-persistent: func ["If object is in raw state than load object from the storage"
      obj [object!] "persistent object"]
[
    if obj/__raw__ [obj/__storage__/load-object obj] 
]
        
loaded?: func ["Check if object is already loaded or explicit invocation of load() method is required"
    obj [object!] "persistent object"]
[
    not obj/__raw__
]

persistent?: func ["Check if object is persistent (assigned persistent OID)"
    obj [object!] "persistent object"]
[
    not none? obj/__oid__
]

modified?: func ["Check if object was modified during current transaction"
    obj [object!] "persistent object"]
[
    obj/__dirty__ 
]

modify: func ["Mark object as modified. This object will be automaticaly stored to the database during transaction commit" 
    obj [object!] "persistent object"]
[
    if all [obj/__storage__ not obj/__dirty__] [obj/__storage__/modify-object obj]
]

store: func ["If object is not yet persistent, then make it persistent and store in the storage"
             obj [object!] "persistent object"]
[
    if obj/__storage__ [obj/__storage__/store-object obj]
]   

storage: func["Get storage in which object is stored, none if object is not yet persistent"
         obj [object!] "persistent object"]
[
    obj/__storage__
]

deallocate: func["Remove object from the storage"
    obj [object!] "persistent object"]
[
    if obj/__storage__ 
    [
        obj/__storage__/deallocate-object obj
        obj/__storage__: none
    ]
]

persistent: make object!
[
    "Base class for all persistent capable objects "
    __raw__: false "object is not loaded"
    __dirty__: false "object was modified"
    __oid__: none "object OID"
    __storage__: none "object storage handler"
    __class__: 'persistent "class name - word containing prototype object"
    __collision_chain__: none "object hash collision chain"
  
    { These methods are commented and replaced with global functions because
      Rebol very ineffiiently handle method objects - for each object instance, 
      method body is compiled and bounded. It case very significant space and memory overhead.
 
    load: func ["If object is in raw state than load object from the storage"]
    [
        if __raw__ [__storage__/load-object self] 
    ]
        
    loaded?: func ["Check if object is already loaded or explicit invocation of load() method is required"]
    [
        not __raw__
    ]

    persistent?: func ["Check if object is persistent (assigned persistent OID)"]
    [
        __oid__
    ]

    modified?: func ["Check if object was modified during current transaction"]
    [
        __dirty__ 
    ]

    modify: func ["Mark object as modified. This object will be automaticaly stored to the database during transaction commit"]
    [
        if all [__storage__ not __dirty__] [__storage__/modify-object self]
    ]

    store: func ["If object is not yet persistent, then make it persistent and store in the storage"]
    [
        if __storage__ [__storage__/store-object self]
    ]   

    storage: func["Get storage in which object is stored, none if object is not yet persistent"]
    [
        __storage__
    ]

    deallocate: func["Remove object from the storage"]
    [
        if __storage__ 
        [
            __storage__/deallocate-object self
            __storage__: none
        ]
    ]
    }
]



index-iterator: make object! 
[
    "Index iterator"

    storage: none
    iterator: none

    next: function["Get next selected object. Returns none if there are no more objects"][oid]
    [
        oid: dybase_iterator_next iterator 
        storage/_lookup-object oid true
    ]
        
    close: func["Close iterator"]
    [ 
        dybase_free_iterator iterator
    ]
]

any-index: make persistent 
[
    "Indexed collection of persistent objects. This collection is implemented using B+Tree"

    index: none

    drop: func["Delete index"]
    [
        dybase_drop_index __storage__/db index
    ]
    
    clear: func["Remove all entries from the index"]
    [
        dybase_clear_index __storage__/db index
    ]
    
    get: function[{Find object in the index with specified key.
                  If no key is found none is returned;
                  If one entry is found then the object associated with this key is returned;
                  Otherwise list of selected object is returned}
                  key "search key"]
                 [result]
    [ 
        result: self/find/from/till key key     
        switch/default length? result [
            1 [first result] 
            0 none
        ] [result]
    ]
]

to-bool: func[x] [either x[1][0]]
to-char*: func[x] [either x[x][""]]

index-factory: context [
    type:
    type-name:
    ins-func:
    rem-func:
    mk-iter-func:
    from-til-desc-param:    ; common param spec for a couple funcs
        none

    literal: func ['val][:val]

    set 'make-index-object func [
        datatype [datatype!]
        /local type-abbr
    ][
        type-abbr: select reduce [string! 'str integer! 'int decimal! 'real] datatype
        set [type type-name ins-func rem-func mk-iter-func] reduce [
            type?/word to datatype 0
            form :datatype
            to word! rejoin ["dybase_insert_in_"   type-abbr '_index]
            to word! rejoin ["dybase_remove_from_" type-abbr '_index]
            to word! rejoin ["dybase_create_"      type-abbr '_iterator]
        ]
        from-til-desc-param: compose/deep from-til-desc-param-spec
        make any-index compose/deep idx-spec
    ]

    from-til-desc-param-spec: [
        /from "low inclusive boundary is specified"
        low [(type)] "inclusive low key boundary"

        /till "high inclusive boundary is specified"
        high [(type)] "inclusive high key boundary"

        /descent "descent traverse order"
    ]

    idx-spec: [
        __class__: (to lit-word! join type-name '-index)

        insert: func["Insert new entry in the index"
            key [(type)] "entry key"
            value [object!] "entry value"
            /replace "replace existed value"]
        [
            __storage__/make-object-persistent value
            to logic! (ins-func) __storage__/db index key value/__oid__ (literal (to-bool replace))
        ]

        remove: function ["Remove entry from the index"
            key [(type)] "removed key"
            /object "To remove entry from non unique index object should be specified"
            value [object!] "removed object"] [oid]
        [
            oid: either object [value/__oid__][0]
            to logic! (rem-func) __storage__/db index key oid
        ]

        find: function[
           {Find objects in the index with key belonging to the specified range
            If /from or /till refinements are not present, then there is no correpondent
            boundary. So "find/from x" will search all ojbects with keys greater or equal than x.
            Returns list of selected objects}

            (from-til-desc-param)

        ][
            iterator selection obj
        ][
            selection: make block! []
            iterator: make index-iterator [
                storage: __storage__
                iterator: (mk-iter-func) __storage__/db index
                (either type = 'string! [literal (to-char* low)]['low])
                    (literal (to-bool from))
                (either type = 'string! [literal (to-char* high)]['high])
                    (literal (to-bool till))
                (literal (to-bool descent))
            ]
            while [obj: iterator/next] [
                append selection obj
            ]
            iterator/close
            selection
        ]

        iterator: func [
            "Get iterator for index objects which key belongs to the specified range"
            (from-til-desc-param)
        ][
            make index-iterator [
                storage: __storage__
                iterator: (mk-iter-func) __storage__/db index
                (either type = 'string! [literal (to-char* low)]['low])
                    (literal (to-bool from))
                (either type = 'string! [literal (to-char* high)]['high])
                    (literal (to-bool till))
                (literal (to-bool descent))
            ]
        ]
    ]
]

string-index:  make-index-object string!
integer-index: make-index-object integer!
decimal-index: make-index-object decimal!



storage: make object! 
[  
    "Main dybase API class" 
    db: none
    page-pool-size: 4194304 "size of database page pool in bytes (larger page pool usually leads to better performance)"
    obj-by-oid-map: none
    hash-size: 0
    modified-list: none

    open: func ["Open database" 
        path "path to database"]
    [
        db: dybase_open path page-pool-size
        either db <> 0 [
            hash-size: 10007
            obj-by-oid-map: array hash-size
            modified-list: make block! []
            true
        ] [
            false
        ]
    ]

    close: func["Close the storage"]
    [
        if db [
            dybase_close db
            db: none
        ]
    ]

    commit: func["Commit current transaction"]
    [
        foreach obj modified-list
        [
            store-object obj
        ]
        clear modified-list
        dybase_commit db
    ]

    rollback: func["Rollback current transaction"]
    [
        clear modified-list
        dybase_rollback db
        reset-hash
    ]

    get-root-object: func["Get storage root object (none if root was not yet specified)"]
    [
        _lookup-object dybase_get_root db true
    ]

    set-root-object: func["Specify new storage root object"
        root "storage root"]
    [
        make-object-persistent root
        dybase_set_root db root/__oid__
    ]

    deallocate-object: function["Deallocate object from the storage" 
        obj "removed object"][hash prev next]
    [
        if oid: obj/__oid__
        [
            hash: (obj/__oid__ // hash-size) + 1
            dybase_deallocate db obj/__oid__
            obj/__oid__: none
            next: pick obj-by-oid-map hash
            prev: none
            while [next] [
                if next = obj [
                    either none? prev [ 
                       poke obj-by-oid-map hash obj/__collision_chain__
                    ] [
                       prev/__collision_chain__: obj/__collision_chain__
                    ]
                    break
                ]                    
                prev: next 
                next: next/__collision_chain__
            ]
        ]
    ]


    make-object-persistent: func ["Make object peristent (assign OID to the object"
        obj "object to be assigned OID"]
    [
        if not obj/__oid__ [store-object obj]
    ]


    modify-object: func [
        "Mark object as modified. This object will be automaticaly stored to the database during transaction commit"
        obj "modified object"]
    [
        obj/__dirty__: true
        append modified-list obj
    ]

    store-object: function["Make object persistent (if it is not yet peristent) and save it to the storage" 
        obj "stored object"]
        [oid hash hnd cls name fields values value]
    [
        oid: obj/__oid__
        if not oid [
            obj/__oid__: oid: dybase_allocate db
            obj/__storage__: self
            hash: (oid // hash-size) + 1        
            obj/__collision_chain__: pick obj-by-oid-map hash
            poke obj-by-oid-map hash obj
        ]
        obj/__dirty__: false
        cls: obj/__class__
        hnd: dybase_begin_store db oid (form cls)
        either find [string-index integer-index decimal-index] cls [
            dybase_store_ref_field hnd "index" obj/index
        ] [
            fields: skip first obj 7 ; skip fields of persistent class
            values: skip second obj 7 ; skip fields of persistent class
            foreach field fields [
                value: first values
                values: next values             
                name: form field
                if #"_" <> first name [
                    do any [
                        select [
                            integer! [dybase_store_int_field hnd name value] 
                            decimal! [dybase_store_real_field hnd name value] 
                            string! [dybase_store_str_field hnd name value]
                            logic! [dybase_store_bool_field hnd name to-bool value]
                            block! [
                                dybase_store_array_field hnd name length? value
                                foreach elem value [_store-element hnd elem]
                            ]
                            hash! [
                                dybase_store_map_field hnd name (length? value) / 2
                                foreach elem value [_store-element hnd elem]
                            ]
                            object! [
                                if not value/__oid__ [store-object value]
                                dybase_store_ref_field hnd name value/__oid__
                            ]
                            none! [dybase_store_ref_field hnd name 0]
                            function! [none]                       
                        ] type?/word :value 
                        [dybase_store_str_field hnd name to string! value]
                    ]
                ]
            ]
        ]
        dybase_end_store hnd             
        obj
    ]

    create-index: func ["Create index for keys of the specified type"
        type [word!] "type of index: integer, string or decimal"
        /unique "index is unique"
        /local map index-oid]
    [
        map: [
            string  [string-index   dybase_create_str_index]
            integer [integer-index  dybase_create_int_index]
            decimal [decimal-index  dybase_create_real_index]
        ] 
        index-oid: do get map/:type/2 db to-bool unique
        store-object make get map/:type/1 [
            index: index-oid
        ]
    ]

    create-string-index: func ["Create index for keys of string type" 
        /unique "index is unique"]
    [
        store-object make string-index [index: dybase_create_str_index db to-bool unique]
    ]

    create-integer-index: func ["Create index for keys of integer type" 
        /unique "index is unique"]
    [
        store-object make integer-index [index: dybase_create_int_index db to-bool unique]
    ]

    create-decimal-index: func ["Create index for keys of decimal type" 
        /unique "index is unique"]
    [
        store-object make decimal-index [index: dybase_create_real_index db to-bool unique]
    ]

    load-object: function ["Resolve references in raw object" 
        obj "target object"]
        [values fields value field]
    [
        obj/__raw__: false
        fields: skip first obj 7 ; skip fields of persistent class
        values: skip second obj 7 ; skip fields of persistent class
        foreach field fields [
            value: first values
            values: next values
            if #"_" <> first form field [
                switch type?/word :value [
                    hash! [
                        _load-series value
                    ]
                    block! [
                        _load-series value
                    ]
                    object! [
                        if value/__class__ = 'stub [ 
                            set in obj field _lookup-object value/__oid__ false 
                        ]
                    ]
                ]
            ]
        ]
        if in obj 'on-load [obj/on-load]
    ]

    reset-hash: func [
        {Reset object hash. Each fetched object is stored in objByOidMap hash table.
         It is needed to provide OID->instance mapping. Since placing object in hash increase its access counter,
         such object can not be deallocated by garbage collector. So after some time all peristent objects from
         the storage will be loaded to the memory. To solve the problem almost all languages with implicit
         memory deallocation (garbage collection) provides weak references. But no Rebol.
         So to prevent memory overflow you should use resetHash() method.
         This method just clear hash table. After invocation of this method, you should not use any variable
         referening persistent objects. Instead you should invoke getRootObject method and access all other
         persistent objects only through the root.}]
    [
        obj-by-oid-map: array hash-size
    ]        

    gc: func ["Start garbage collection"] 
    [
        dybase_gc db
    ]

    set-gc-threshold: func [
        {Set garbage collection threshold.
         By default garbage collection is disable (threshold is set to 0).
         If it is set to non zero value, GC will be started each time when
         delta between total size of allocated and deallocated objects exeeds specified threshold OR
         after reaching end of allocation bitmap in allocator.
        }
        threshold "allocated_delta delta between total size of allocated and deallocated object since last GC or storage openning"]
    [
        dybase_set_gc_threshold db threshold
    ]
        
    _load-series: function[arr] [i]
    [ 
        i: 1
        foreach elem arr [
            switch type?/word elem [
                hash! [
                    _load-series elem
                ]
                block! [
                    _load-series elem
                ]
                object! [
                    if elem/__class__ = 'stub [ 
                        poke arr i _lookup-object elem/__oid__ false 
                    ]
                ]
            ]
            i: i + 1
        ]
    ]

    _fetch-component: function[hnd recursive] [oid hash value length this]
    [
    	switch/default (dybase_get_type hnd) [
            0 ; dybase_object_type
            [
                oid: dybase_get_ref hnd
                either oid = 0 [none] [ 
                    either recursive [ 
                        _lookup-object oid false
                    ] [ 
                        hash: (oid // hash-size) + 1
                        value: pick obj-by-oid-map hash 
                        while [value] [
                            if value/__oid__ = oid [return value]
                            value: value/__collision_chain__
                        ]
                        this: self
                        make persistent [__oid__: oid __storage__: this __class__: 'stub]
                    ]    
                ]
            ]
            1 ; dybase_bool_type
            [
                to logic! dybase_get_bool hnd
            ]
            2 ; dybase_int_type
            [
                dybase_get_int hnd
            ]
            4 ; dybase_real_type
            [
                dybase_get_real hnd
            ]
            5 ; dybase_string_type
            [
                dybase_get_str hnd
            ]
            6 ; dybase_array_type 
            [
                _fetch-array hnd (dybase_get_length hnd) recursive
            ]
            7 ; dybase_map_type
            [
                _fetch-map hnd (dybase_get_length hnd) recursive
            ]
        ] [none]
    ]

    _lookup-object: function[oid recursive] [this obj hnd class-name field-name hash chain body]
    [
        either oid = 0 [
            none
        ] [
            hash: (oid // hash-size) + 1
            chain: obj: pick obj-by-oid-map hash 
            while [all [obj obj/__oid__ <> oid]] [
                obj: obj/__collision_chain__
            ]
            either not obj [
                hnd: dybase_begin_load db oid
                cls: to word! dybase_get_class_name hnd
                this: self

                either find [string-index integer-index decimal-index] cls [
                    obj: make get cls [__oid__: oid __storage__: this __class__: cls __collision_chain__:chain]
                    dybase_next_field hnd
                    obj/index: dybase_get_ref hnd
                    dybase_next_field hnd
                ] [        
                    body: make block! 16
                    while [not empty? field-name: dybase_next_field hnd] [
                        insert insert tail body (to-set-word field-name) _fetch-component hnd false
                    ]
                    insert tail body [__oid__: oid __storage__: this  __class__: cls __collision_chain__:chain]
                    obj: make get cls body
                    either all [not recursive in obj '__nonrecursive__] [
                       obj/__raw__: true
                    ] [
                       load-object obj   
                    ]
                ] 
                poke obj-by-oid-map hash obj
            ] [ 
                if recursive and obj/__raw__ [load-object obj]
            ]
            obj
        ]
    ]

    _fetch-array: function[hnd len recursive] [arr]
    [
        arr: make block! [] 
	repeat i len [
            dybase_next_elem hnd
	    append arr _fetch-component hnd recursive
        ]
        arr
    ]

    _fetch-map: function[hnd len recursive] [hash key value]
    [
        hash: make hash! len
	repeat i len [
            dybase_next_elem hnd
            key: _fetch-component hnd recursive
            dybase_next_elem hnd
            value: _fetch-component hnd recursive
            insert insert tail hash key value
        ]
        hash
    ]

    _store-element: func [hnd value] 
    [
        switch/default type?/word value [
            integer! [dybase_store_int_elem hnd value] 
            decimal! [dybase_store_real_field hnd field value] 
            string! [dybase_store_str_elem hnd value]
            logic! [dybase_store_bool_elem hnd (to-bool value)]
            block! [
                dybase_store_array_elem hnd (length? value)
                foreach elem value [_store-element hnd elem]
            ]
            hash! [
                dybase_store_map_elem hnd field ((length? value) / 2)
                foreach elem value [_store-element hnd elem]
            ]
            object! [
                if not value/__oid__ [store-object value]
                dybase_store_ref_elem hnd value/__oid__
            ]
            none! [dybase_store_ref_elem hnd 0]
        ] [dybase_store_str_elem hnd (to string! value)]
    ]
]

