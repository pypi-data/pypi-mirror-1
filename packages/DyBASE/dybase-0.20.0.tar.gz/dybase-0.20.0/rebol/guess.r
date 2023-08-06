REBOL [
    Title: "Guess an Animal"
    File:  %guess.r
    Author: "knizhnik@garret.ru"
    Date:  11-Dec-2003
    Version: 1.1
    Purpose: {
        Example: Guess an Animal Game
        This examle illustrates storing hierarchical data structure in database
    }
]

do %dybase.r

who-is-it: function[parent][animal difference]
[
    animal: ask "What is it ? "
    difference: ask "What is a difference from other ? "
    return make guess [no: parent question: difference yes: make guess [question: animal]]
]


ask-question: function[question] [answer] 
[
    answer: ask question
    return (answer = "y") or (answer = "yes")
]

guess: make persistent 
[
    __class__: 'guess
    yes: none
    no:  none
    question: none
 
    dialog: function[][clarify] [
	either ask-question reduce ["May be," question "(y/n) ? "] [
	    either yes [
        	clarify: yes/dialog
		if clarify [
		    yes: clarify
                    store self
                ]
            ] [
		print "It was very simple question for me..."
	    ]
	] [ 
	    either no [
        	clarify: no/dialog
		if clarify [
		    no: clarify
                    store self
                ]
            ] [
		if not yes [
		    return who-is-it self
                ]
   	        no: who-is-it none
                store self
            ]
        ]
	none
    ]
]
    
db: make storage[]
if db/open "guess.dbs" [
    root: db/get-root-object
    while [ask-question "Think of an animal. Ready (y/n) ? "] [  
       either root [ 
           root/dialog
       ] [
           root: who-is-it none
           db/set-root-object root
       ]
       db/commit
    ]
    print "End of the game"
    db/close
]