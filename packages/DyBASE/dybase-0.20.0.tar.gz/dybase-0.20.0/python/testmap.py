"""Test of storing dictionary in DyBASE
"""

import dybase

class Node: 
    def __init__(self, name, parent):
    	self.name = name
        self.parent = parent
	if parent != None:
	    parent.addSibling(self) 
        self.siblings = []
	self.attributes = {}

    def addSibling(self, sibling):
    	self.siblings.append(sibling)

    def addAttribute(self, name, value):
        self.attributes[name] = value
 
    def dump(self, indent):
    	tab = '        '[0:indent]
    	print tab, '<', self.name,
    	for e in self.attributes.iteritems():
	    print ' ', e[0], '=', e[1],
        print '>'
	for s in self.siblings:
	    s.dump(indent+1)
    	print tab, '</', self.name, '>'

class Document:
    def __init__(self, root):
        self.root = root

    def dump(self):
        self.root.dump(0)

pagePoolSize = 32*1024*1024
db = dybase.Storage(pagePoolSize)

if db.open("testmap.dbs"):
    doc = db.getRootObject()
    if doc == None:
        root = Node('root', None)
	n1 = Node('node1', root)	
	n1.addAttribute('align', 'center')
	n2 = Node('node2', n1) 
	n2.addAttribute('width', 100)
	n2.addAttribute('height', 100)
	n3 = Node('node3', n1)
	n4 = Node('node4', n3)
	n4.addAttribute('font', 'system')
        doc = Document(root)
        db.setRootObject(doc)
	print 'Database initialized'
    else: 
        doc.dump()
    db.close()
