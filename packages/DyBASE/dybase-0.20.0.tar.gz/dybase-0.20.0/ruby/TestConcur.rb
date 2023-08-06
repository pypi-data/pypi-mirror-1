#!/usr/local/bin/ruby

=begin
= Test of concurrent execution and locking
=end

require "dybase"
require "thread"
include Dybase

class L2List<Persistent
    def initialize()
        @head = L2Elem.new(0)
    end
    attr_reader :head
end

class L2Elem<Persistent
    def initialize(count)
        @next = self
        @prev = self
        @count = count
    end

    def recursiveLoading()
        return false
    end

    def unlink()
        @next.prev = @prev
        @prev.next = @next
        @next.store()
        @prev.store()
    end

    def linkAfter(elem)         
        elem.next.prev = self
        @next = elem.next
        elem.next = self
        @prev = elem
        store()
        @next.store()
        @prev.store()
    end

    attr_reader :next, :prev, :count
    attr_writer :next, :prev, :count
end

class TestConcur
    @@nElements = 100000
    @@nIterations = 10
    @@nThreads = 4

    def run()
        list = @db.getRootObject()
        for i in 0...@@nIterations 
            sum = 0
            n = 0
            list.sharedLock()
            head = list.head 
            elem = head
            while true 
                elem.load()
                sum += elem.count
                n += 1
                elem = elem.next
                if elem == head
                    break
                end
            end
            if n != @@nElements or sum != @@nElements*(@@nElements-1)/2
                raise "Corrupted list"
            end
            list.unlock()
            list.exclusiveLock()
            last = list.head.prev
            last.unlink()
            last.linkAfter(list.head)
            list.unlock()
        end
    end

    def initialize()
        @db = Storage.new()
        if @db.open("testconcur.dbs")
            list = @db.getRootObject()
            if list == nil
                list = L2List.new()
                @db.setRootObject(list)
                for i in 1...@@nElements
                    elem = L2Elem.new(i)
                    elem.linkAfter(list.head) 
                end
            end
        end
        threads = []
        for i in 0...@@nThreads 
            threads << Thread.new { run() }
        end
        for thread in threads 
            thread.join()
        end
        @db.close()
    end
end

test = TestConcur.new()
