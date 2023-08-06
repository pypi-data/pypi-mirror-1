#!/usr/local/bin/ruby

=begin
= Test of dybase indices
  This test can be also used for measuring DYBASE perfrormance
=end

require "dybase"
include Dybase

class Record<Persistent
    def initialize(key)
        @strKey = key.to_s
        @intKey = key
    end

    attr_reader :intKey, :strKey
end

class Root<Persistent
    def initialize(db)
        @strIndex = db.createStrIndex(true)
        @intIndex = db.createIntIndex(true)
    end

    attr_reader :intIndex, :strIndex
end

N_RECORDS = 100000
PAGE_POOL_SIZE = 32*1024*1024

db = Storage.new(PAGE_POOL_SIZE)

if db.open("testidx.dbs")
    root = db.getRootObject()
    if root == nil
        root = Root.new(db)
        db.setRootObject(root)
    end
    intIndex = root.intIndex
    strIndex = root.strIndex
    start = Time.now.to_i
    key = 1999
    for i in 0...N_RECORDS
        key = (3141592621*key + 2718281829) % 1000000007
        rec = Record.new(key)
        if not intIndex.insert(rec.intKey, rec)                
            raise "Duplicate int key"
        end
        if not strIndex.insert(rec.strKey, rec)                
            raise "Duplicate str key"
        end
    end
    db.commit()
    puts('Elapsed time for inserting ' + N_RECORDS.to_s + ' records: ' + (Time.now.to_i-start).to_s + ' seconds')
        
    start = Time.now.to_i
    key = 1999
    for i in 0...N_RECORDS
        key = (3141592621*key + 2718281829) % 1000000007
        rec1 = intIndex.get(key)
        rec2 = strIndex.get(key.to_s)
        if rec1 == nil or rec1 != rec2 or rec1.intKey != key
            print("rec1=" + rec1.to_s + ", rec2=" + rec2.to_s + ", rec1.key=" + rec1.intKey.to_s + ", rec2.key=" + rec2.intKey.to_s + ", key=" + key.to_s + "\n")
            raise "incorrect index"
        end
    end
    puts('Elapsed time for performing ' + (N_RECORDS*2).to_s + ' index searches: ' + (Time.now.to_i-start).to_s + ' seconds')
        
    start = Time.now.to_i
    key = -1
    i = 0
    intIndex.iterate { |rec| 
        if rec.intKey < key
            raise "Iterating order is not correct"
        end
        key = rec.intKey
        i += 1
    }
    if i != N_RECORDS
        raise "Iterator doen't work"
    end
    key = ""
    i = 0
    strIndex.iterate { |rec| 
        if rec.strKey < key
            raise "Iterating order is not correct"
        end
        key = rec.strKey
        i += 1
    }
    if i != N_RECORDS
        raise "Iterator doen't work"
    end
    puts('Elapsed time for iterating through ' + (N_RECORDS*2).to_s + ' records: ' + (Time.now.to_i-start).to_s + ' seconds')

    start = Time.now.to_i
    key = 1999
    for i in 0...N_RECORDS
        key = (3141592621*key + 2718281829) % 1000000007
        rec = intIndex.get(key)
        if not intIndex.remove(key)
            raise "Remove int key failed"
        end
        if not strIndex.remove(key.to_s, rec)
            raise "Remove str key failed"
        end
        rec.deallocate()
    end

    puts('Elapsed time for deleting ' + N_RECORDS.to_s + ' records: ' + (Time.now.to_i-start).to_s + ' seconds')
    db.close()
end
