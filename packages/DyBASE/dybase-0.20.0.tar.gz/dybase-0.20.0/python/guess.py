"""
Sample "Guess an animal"
Very simple game storing its tree in the storage
"""

import dybase

def askQuestion(question):
     answer = raw_input(question)
     return answer.lower().startswith('y')

def whoIsIt(parent):
    animal = raw_input('What is it ? ')
    difference = raw_input('What is a difference from other ? ')
    return Guess(parent, difference, Guess(None, animal, None))


class Guess(dybase.Persistent):
    def __init__(self, no, question, yes):
	self.yes = yes
	self.question = question
	self.no = no

    def dialog(self):
	if askQuestion('May be, ' + self.question + ' (y/n) ? '):
	    if self.yes == None: 
		print('It was very simple question for me...')
	    else: 
        	clarify = self.yes.dialog()
		if clarify != None:
		    self.yes = clarify
                    self.store()
	else:
	    if self.no == None:
		if self.yes == None:
		    return whoIsIt(self)
   	        self.no = whoIsIt(None)
                self.store()
	    else: 
        	clarify = self.no.dialog()
		if clarify != None:
		    self.no = clarify
                    self.store()
	return None

    
db = dybase.Storage()
if db.open('guess.dbs'):
    root = db.getRootObject()
    while askQuestion('Think of an animal. Ready (y/n) ? '): 
       if root == None:
           root = whoIsIt(None)
           db.setRootObject(root)
       else: 
           root.dialog()
       db.commit()
    print('End of the game')
    db.close()
