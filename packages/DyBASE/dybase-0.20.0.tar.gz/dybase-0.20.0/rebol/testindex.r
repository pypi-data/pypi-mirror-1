REBOL [
    Title: "Test of DyBASE indices"
    File:  %testindex.r
    Author: "knizhnik@garret.ru"
    Date:  11-Dec-2003
    Version: 1.1
    Purpose: {
        Test of dybase indices
        This test can be also used for measuring DYBASE perfrormance
    }
]

do %dybase.r

record: make persistent [
    __class__: 'record
    str-key: none
    int-key: none
]

indices: make persistent [
    __class__: 'indices
    str-index: none
    int-index: none
]

n-records: 100000

db: make storage[page-pool-size:  32 * 1024 * 1024]


if db/open "testidx.dbs"
[
    print ["Start at" now]
    root: db/get-root-object
    if not root
    [
        root: make indices[str-index: db/create-index/unique 'string int-index: db/create-integer-index/unique]
        db/set-root-object root
    ]
    int-index: root/int-index
    str-index: root/str-index
    start: now/time
    key: 1
    repeat i n-records [ 
        key: to-integer (3141592621 * key + 2718281829) // 2000000007
        rec: make record[str-key: to-string key int-key: key]
        inserted: int-index/insert rec/int-key rec
        if not inserted [
            print "Failed to insert record in integer index"
            halt
        ]        
        inserted: str-index/insert rec/str-key rec
        if not inserted [
            print "Failed to insert record in string index"
            halt
        ] 
        if (i // 100) = 0 [db/reset-hash]
    ]
    db/commit
    print ["Elapsed time for inserting"  n-records "records:" (now/time - start)]
    start: now/time
    key: 1
    repeat i n-records [ 
        key: to-integer (3141592621 * key + 2718281829) // 2000000007
        rec1: int-index/get key
        rec2: str-index/get to-string key
        if ((type? rec1) <> object!) or ((type? rec2) <> object!) or (rec1 <> rec2) [
            print ["FAILED: rec1=" rec1 "rec2=" rec2]
            halt
        ]
        if (i // 100) = 0 [db/reset-hash]
    ]
    print ["Elapsed time for performing" (n-records * 2) "index searches:" (now/time - start)]
    start: now/time
    key: -1
    i: 0
    iterator: int-index/iterator
    while [rec: iterator/next] [
        if rec/int-key < key [
            print "invalid itertion order"
            halt
        ]
        key: rec/int-key
        if (i // 100) = 0 [db/reset-hash]
        i: i + 1
    ]
    iterator/close
    if i <> n-records [
        print ["Invalid number of iterated objects:" i "instead of" n-records]
    ]
    key: ""
    i: 0
    iterator: str-index/iterator
    while [rec: iterator/next] [
        if rec/str-key < key [
            print "invalid itertion order"
            halt
        ]
        key: rec/str-key
        if (i // 100) = 0 [db/reset-hash]
        i: i + 1
    ]
    iterator/close
    if i <> n-records [
        print ["Invalid number of iterated objects" i "instead of" n-records]
    ]
    print ["Elapsed time for iterating through" (n-records * 2) "records:" (now/time - start)]
    start: now/time
    key: 1
    repeat i n-records [ 
        key: to-integer (3141592621 * key + 2718281829) // 2000000007
        rec: int-index/get key
        if not rec [
            print "FAILED: record not found"
            halt
        ]
        removed: int-index/remove key
        if not removed [
            print "Failed to remove record from integer index"
            halt
        ]        
        removed: str-index/remove/object (to-string key) rec
        if not removed [
            print "Failed to remove record from string index" 
            halt
        ] 
        deallocate rec
        if (i // 100) = 0 [db/reset-hash]
    ]

    print ["Elapsed time for deleting" n-records "records:" (now/time - start)]
    db/close
]

ask "Done?"



