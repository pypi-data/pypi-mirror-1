REBOL [
    Title: "Supplier-Order-Detail database"
    File:  %testlink.r
    Author: "knizhnik@garret.ru"
    Date:  11-Dec-2003
    Version: 1.1
    Purpose: {
        Example: Supplier-Order-Detail database
        This examle illustrates usage of one-to-many link in dybase
    }
]

do %dybase.r

detail: make persistent [
    __class__: 'detail
    name: none
    weight: none
    color: none
    orders: []
]

supplier: make persistent [
    __class__: 'supplier
    name: none
    address: none
    orders: []
]

order: make persistent [
    __class__: 'order
    detail: none
    supplier: none
    quantity: none
    price: none
]

suppliers-details: make persistent [
    __class__: 'suppliers-details
    suppliers: none
    details: none
]


db: make storage []
if db/open "testlink.dbs" [
    root: db/get-root-object
    if not root [
        root: make suppliers-details [
            suppliers: db/create-string-index/unique 
            details: db/create-string-index/unique
        ]
        db/set-root-object root
    ]

    while [true] [
        print "------------------------------------------"
        print "1. Add supplier"
        print "2. Add detail"
        print "3. Add order"
        print "4. Search suppliers"
        print "5. Search details"
        print "6. Suppliers of detail"
        print "7. Deails shipped by supplier"
        print "8. Exit"
        if error? try [
            cmd: to-integer ask ">>"
            switch/default cmd [
            1 [
                s: make supplier[name:  ask "Supplier name: " address: ask "Supplier address: "]
                root/suppliers/insert s/name s
                db/commit
            ]
            2 [
                d: make detail[name: ask "Detail name: " 
                               weight: to-decimal ask "Detail weight: "  
                               color: ask "Detail color: "]
                root/details/insert d/name d
                db/commit
            ]
            3 [
                s: root/suppliers/get ask "Supplier name: "
                either not s [
                    print "No such supplier"
                ] [
                    either d: root/details/get ask "Detail name: " [
                        o: make order [detail: d 
                                       supplier: s 
                                       quantity: to-integer ask "Quantity: "
                                       price: to-integer ask "Price: "]
                        append d/orders o
                        append s/orders o
                        store d
                        store s
                        db/commit
                    ] [
                        print "No such detail"
                    ]
                ]
            ]
            4 [
                supplier-name: ask "Supplier name prefix: "
                suppliers: root/suppliers/find/from/till supplier-name (join supplier-name "zzz")
                either (length? suppliers) = 0 [
                    print "No such suppliers found"
                ] [
                    foreach s suppliers [
                        print [s/name s/address]
                    ]
                ]
            ]
            5 [
                detail-name: ask "Detail name prefix: "
                details: root/details/find/from/till detail-name (join detail-name "zzz")   
                either (length? details) = 0 [
                    print "No such details found"
                ] [
                    foreach d details [
                        print [d/name d/weight d/color]
                    ]
                ]
            ]
            6 [
                detail-name: ask "Detail name prefix: "
                either d: root/details/get detail-name [
                    foreach o d/orders [
                        print o/supplier/name    
                    ]
                ] [
                    print "No such detail"
                ]
            ]
            7 [
                supplier-name: ask "Supplier name: "
                either s: root/suppliers/get supplier-name [
                    foreach o s/orders [
                        print o/detail/name    
                    ]
                ] [ 
                    print "No such supplier"
                ]
            ]
            8 [
                break
            ]
            ] [print "Invalid command"]
        ] [print "Invalid input"]
    ]
    db/close
    print "End of session"
]



