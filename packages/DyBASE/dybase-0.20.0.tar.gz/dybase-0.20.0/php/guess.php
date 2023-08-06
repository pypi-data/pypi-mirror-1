<?php

/**
 * Sample "Guess an animal"
 * Very simple game storing its tree in the storage
 */

include "dybase.php";

$fp = fopen("php://stdin", "r");
function input($prompt) { 
    global $fp;
    do {
        print($prompt);
        flush();
        $in = trim(fgets($fp, 4094));
    } while (strlen($in) == 0);
    return $in;
}
     
        
function askQuestion($question) { 
    $answer = strtolower(input($question));
    return $answer[0] == 'y';
}

function &whoIsIt(&$parent) {
    $animal = input("What is it ? ");
    $difference = input("What is a difference from other ? ");
    $yes = null;
    $no = null;
    return new Guess($parent, $difference, new Guess($no, $animal, $yes));
}


class Guess extends Persistent {
    var $yes;
    var $no;
    var $question;
 
    function Guess(&$no, $question, &$yes) {
	$this->yes = &$yes;
	$this->question = $question;
	$this->no = &$no;
    }

    function &dialog() {
	if (askQuestion("May be, " . $this->question . " (y/n) ? ")) { 
	    if ($this->yes == null) { 
		print("It was very simple question for me...\n");
	    } else { 
        	$clarify = &$this->yes->dialog();
		if ($clarify != null) { 
		    $this->yes = &$clarify;
                    $this->store();
                }
            }
	} else { 
	    if ($this->no == null) { 
		if ($this->yes == null) { 
		    return whoIsIt($this);
                }
                $parent = null;
   	        $this->no = &whoIsIt($parent);
                $this->store();
	    } else { 
        	$clarify = &$this->no->dialog();
		if ($clarify != null) { 
		    $this->no = &$clarify;
                    $this->store();
                }
            }
        }
	return null;
    }
}
    
$db = &new Storage();
if ($db->open("guess.dbs")) { 
    $root = &$db->getRootObject();
    while (askQuestion("Think of an animal. Ready (y/n) ? ")) {  
       if ($root == null) { 
           $parent = null;
           $root = &whoIsIt($parent);
           $db->setRootObject($root);
       } else { 
           $root->dialog();
       }
       $db->commit();
    }
    print("End of the game\n");
    $db->close();
}

?>
