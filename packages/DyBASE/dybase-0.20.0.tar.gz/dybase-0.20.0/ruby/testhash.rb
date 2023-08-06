#!/usr/local/bin/ruby

=begin
= Test of storing hashes and arrays
=end

require "dybase"
include Dybase

class Node<Persistent
    def initialize(name, parent)
    	@name = name
        @parent = parent
	if parent != nil
	    parent.addSibling(self) 
	end
        @siblings = []
	@attributes = {}
    end

    def addSibling(sibling)
    	@siblings << sibling
    end

    def addAttribute(name, value)
        @attributes[name] = value
    end 

    def dump(indent)
    	tab = '        '[0..indent]
    	print tab, '<', @name
    	for name,value in @attributes
	    print ' ', name, '=', value
        end
        puts '>'
	for s in @siblings
	    s.dump(indent+1)
        end
    	puts tab + '</' + @name + '>'
    end
end

class Document<Persistent
    def initialize(root)
        @root = root
    end

    def dump()
        @root.dump(0)
    end
end

pagePoolSize = 32*1024*1024
db = Storage.new(pagePoolSize)

if db.open("testhash.dbs")
    doc = db.getRootObject()
    if doc == nil
        root = Node.new('root', nil)
	n1 = Node.new('node1', root)	
	n1.addAttribute('align', 'center')
	n2 = Node.new('node2', n1) 
	n2.addAttribute('width', 100)
	n2.addAttribute('height', 100)
	n3 = Node.new('node3', n1)
	n4 = Node.new('node4', n3)
	n4.addAttribute('font', 'system')
        doc = Document.new(root)
        db.setRootObject(doc)
	print 'Database initialized'
    else 
        doc.dump()
    end
    db.close()
end
