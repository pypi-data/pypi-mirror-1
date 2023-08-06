#!/usr/local/bin/ruby

=begin
= Sample "Guess an animal"
  Very simple game storing its tree in the storage
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

def askQuestion(question)
    answer = input(question)
    yes = false
    if answer != nil
        answer = answer.downcase()
        yes = (answer == 'yes' or answer == 'y')
    end
    yes
end

def whoIsIt(parent)
    animal = input('What is it ? ')
    difference = input('What is a difference from other ? ')
    return Guess.new(parent, difference, Guess.new(nil, animal, nil))
end

class Guess<Persistent
    def initialize(no, question, yes)
	@yes = yes
	@question = question
	@no = no
    end

    def dialog()
	if askQuestion('May be, ' + @question + ' (y/n) ? ')
	    if @yes == nil 
		puts('It was very simple question for me...')
	    else 
        	clarify = @yes.dialog()
		if clarify != nil
		    @yes = clarify
                    store()
                end
            end
	else
	    if @no == nil
		if @yes == nil
		    return whoIsIt(self)
                end
   	        @no = whoIsIt(nil)
                store()
	    else
        	clarify = @no.dialog()
		if clarify != nil
		    @no = clarify
                    store()
                end
            end
        end
	nil
    end
end

db = Storage.new()
if db.open('guess.dbs')
    root = db.getRootObject()
    while askQuestion('Think of an animal. Ready (y/n) ? ') 
       if root == nil
           root = whoIsIt(nil)
           db.setRootObject(root)
       else
           root.dialog()
       end
       db.commit()
    end
    puts('End of the game')
    db.close()
end
