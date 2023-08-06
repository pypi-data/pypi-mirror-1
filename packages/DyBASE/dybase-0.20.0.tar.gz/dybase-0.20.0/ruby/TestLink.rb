#!/usr/local/bin/ruby

=begin
= Example: Supplier-Order-Detail database
  This examle illustrates usage of one-to-many link in dybase
=end

require "dybase"
include Dybase

def input(prompt)
    begin
        print(prompt)
        s = gets()
        if s == nil
            break
        end
        s = s.strip()
    end until s.length != 0
    s
end


class Detail<Persistent
    def initialize(name, weight, color)
        @name = name
        @color = color
        @weight = weight
        @orders = []
    end
    attr_reader :name, :color, :weight, :orders
end

class Supplier<Persistent
    def initialize(name, address)
        @name = name
        @address = address
        @orders = []
    end
    attr_reader :name, :address, :orders
end

class Order<Persistent
    def initialize(detail, supplier, quantity, price)
        @detail = detail
        @supplier = supplier
        @quantity = quantity
        @price = price
    end
    attr_reader :detail, :supplier, :quantity, :price
end

class Root<Persistent
    def initialize( db)
        @suppliers = db.createStrIndex
        @details = db.createStrIndex
    end
    attr_reader :suppliers, :details
end


db = Storage.new
if db.open('testlist.dbs')
    root = db.getRootObject()
    if root == nil
        root = Root.new(db)
        db.setRootObject(root)
    end

    while true
        puts '------------------------------------------'
        puts '1. Add supplier'
        puts '2. Add detail'
        puts '3. Add order'
        puts '4. Search suppliers'
        puts '5. Search details'
        puts '6. Suppliers of detail'
        puts '7. Deails shipped by supplier'
        puts '8. Exit'
        cmd = input('> ')
        if cmd == '1'
            name = input('Supplier name: ')
            address = input('Supplier address: ')
            supplier = Supplier.new(name, address)
            root.suppliers.insert(name, supplier)
            db.commit()
        elsif cmd == '2'
            name = input('Detail name: ')
            weight = input('Detail weight: ').to_f
            color = input('Detail color: ')
            detail = Detail.new(name, weight, color)
            root.details.insert(name, detail)
            db.commit()
        elsif cmd == '3'
            supplierName = input('Supplier name: ')
            supplier = root.suppliers.get(supplierName)
            if supplier == nil
                puts 'No such supplier'
                retry
            end
            detailName = input('Detail name: ')
            detail = root.details.get(detailName)
            if detail == nil
                puts 'No such detail'
                retry
            end
            quantity = input('Quantity: ').to_i
            price = input('Price: ').to_i
            order = Order.new(detail, supplier, quantity, price)
            detail.orders << order
            supplier.orders << order
            detail.store()
            supplier.store()
            db.commit()
        elsif cmd == '4'
            supplierName = input('Supplier name prefix: ')
            suppliers = root.suppliers.find(supplierName, true, supplierName + "\xFF", false)   
            if suppliers == nil
                puts 'No such suppliers found'
            else
                for supplier in suppliers
                    puts supplier.name + "\t" + supplier.address
                end
            end
        elsif cmd == '5'
            detailName = input('Detail name prefix: ')
            details = root.details.find(detailName, true, detailName + "\xFF", false)   
            if details == nil
                puts('No such details found')
            else
                for d in details
                    puts d.name + "\t" + d.weight.to_s + "\t" +  d.color
                end
            end
        elsif cmd == '6'
            detailName = input('Detail name: ')
            detail = root.details.get(detailName)
            if detail == nil
                puts 'No such detail'
            else
                for order in detail.orders
                    puts order.supplier.name    
                end
            end
        elsif cmd == '7'
            supplierName = input('Supplier name: ')
            supplier = root.suppliers.get(supplierName)
            if supplier == nil
                puts 'No such supplier'
            else
                for order in supplier.orders
                    puts order.detail.name    
                end
            end
        elsif cmd == '8'
            break
        else
            puts 'Invalid command'
        end
    end
    db.close()
    puts 'End of session'
end 



