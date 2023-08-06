"""
Example: Supplier-Order-Detail database
This examle illustrates usage of one-to-many link in dybase
"""

import dybase

class Detail(dybase.Persistent):
    def __init__(self, name, weight, color):
        self.name = name
        self.color = color
        self.weight = weight
        self.orders = []
        

class Supplier(dybase.Persistent):
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.orders = []
   

class Order(dybase.Persistent):
    def __init__(self, detail, supplier, quantity, price):
        self.detail = detail
        self.supplier = supplier
        self.quantity = quantity
        self.price = price

class Root(dybase.Persistent):
    def __init__(self, db):
        self.suppliers = db.createStrIndex(True)
        self.details = db.createStrIndex(True)
        

db = dybase.Storage()
if db.open('testlist.dbs'):
    root = db.getRootObject()
    if root == None:
        root = Root(db)
        db.setRootObject(root)

    while True: 
        print '------------------------------------------'
        print '1. Add supplier'
        print '2. Add detail'
        print '3. Add order'
        print '4. Search suppliers'
        print '5. Search details'
        print '6. Suppliers of detail'
        print '7. Deails shipped by supplier'
        print '8. Exit'
        cmd = raw_input('> ')
        if cmd == '1':
            name = raw_input('Supplier name: ')
            address = raw_input('Supplier address: ')
            supplier = Supplier(name, address)
            root.suppliers.insert(name, supplier)
            db.commit()
        elif cmd == '2':
            name = raw_input('Detail name: ')
            weight = float(raw_input('Detail weight: '))
            color = raw_input('Detail color: ')
            detail = Detail(name, weight, color)
            root.details.insert(name, detail)
            db.commit()
        elif cmd == '3':
            supplierName = raw_input('Supplier name: ')
            supplier = root.suppliers.get(supplierName)
            if supplier == None:
                print 'No such supplier'
                continue
            detailName = raw_input('Detail name: ')
            detail = root.details.get(detailName)
            if detail == None:
                print 'No such detail'
                continue
            quantity = int(raw_input('Quantity: '))
            price = long(raw_input('Price: '))
            order = Order(detail, supplier, quantity, price)
            detail.orders.append(order)
            supplier.orders.append(order)
            detail.store()
            supplier.store()
            db.commit()
        elif cmd == '4':
            supplierName = raw_input('Supplier name prefix: ')
            suppliers = root.suppliers.find(supplierName, True, supplierName + chr(255), False)   
            if suppliers == None:
                print 'No such suppliers found'
            else:
                for supplier in suppliers:
                    print supplier.name, supplier.address
        elif cmd == '5':
            detailName = raw_input('Detail name prefix: ')
            details = root.details.find(detailName, True, detailName + chr(255), False)   
            if details == None:
                print('No such details found')
            else:
                for d in details:
                    print d.name, d.weight, d.color
        elif cmd == '6':
            detailName = raw_input('Detail name: ')
            detail = root.details.get(detailName)
            if detail == None:
                print 'No such detail'
            else:
                for order in detail.orders:
                    print order.supplier.name    
        elif cmd == '7':
            supplierName = raw_input('Supplier name: ')
            supplier = root.suppliers.get(supplierName)
            if supplier == None:
                print 'No such supplier'
            else:
                for order in supplier.orders:
                    print order.detail.name    
        elif cmd == '8':
            break
        else:
            print 'Invalid command'
    db.close()
    print 'End of session'
        



