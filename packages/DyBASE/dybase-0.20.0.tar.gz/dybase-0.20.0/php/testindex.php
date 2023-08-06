<?php

/**
 * Test of dybase indices
 * This test can be also used for measuring DYBASE perfrormance
 */

include "dybase.php";

class Record extends Persistent {
    var $strKey;
    var $intKey;

    function Record($key) { 
        $this->strKey = strval($key);
        $this->intKey = $key;
    }
}

class Root extends Persistent {
    var $strIndex;
    var $intIndex;
}

function nextKey($key) { 
    return intval(fmod(3141592621*$key + 2718281829, 2000000007));
}
        
define("nRecords", 100000);
define("pagePoolSize", 32*1024*1024);

$db = new Storage(pagePoolSize);

if ($db->open("testidx.dbs")) { 
    $root = &$db->getRootObject();
    if ($root == null) {
        $root = &new Root();
        $root->strIndex = &$db->createStrIndex(true);
        $root->intIndex = &$db->createIntIndex(true);
        $db->setRootObject($root);
    }
    $intIndex = &$root->intIndex;
    $strIndex = &$root->strIndex;
    $start = time();
    $key = 1;
    for ($i = 0; $i < nRecords; $i++) { 
        $key = nextKey($key);
        $rec = &new Record($key);
        $inserted = $intIndex->insert($rec->intKey, $rec);                
        if (!$inserted) { 
            user_error("Failed to insert record in integer index i=$i\n"); 
            exit();
        }        
        $inserted = $strIndex->insert($rec->strKey, $rec);
        if (!$inserted) { 
            user_error("Failed to insert record in string index\n"); 
        }        
        if ($i % 1000 == 0) { 
            $db->resetHash();
        }
    }
    $db->commit();
    print("Elapsed time for inserting " . nRecords . " records: " . (time() - $start) . " seconds\n");
        
    $start = time();
    $key = 1;
    for ($i = 0; $i < nRecords; $i++) { 
        $key = nextKey($key);
        $rec1 = &$intIndex->get($key);
        $rec2 = &$strIndex->get(strval($key));
        if ($rec1 == null || $rec2 == null || $rec1->intKey != $rec2->intKey) {
            user_error("FAILED: rec=$rec1 rec2=$rec2\n"); 
        }
        if ($i % 1000 == 0) { 
            $db->resetHash();
        }
    }       
    print("Elapsed time for performing " . nRecords*2 . " index searches: " . (time() - $start) . " seconds\n");

    $start = time();
    $key = -1;
    $i = 0;
    $iterator = $intIndex->iterator();
    while (($rec = $iterator->next()) != null) {
        if ($rec->intKey < $key) {
            user_error("invalid itertion order");
        }
        $key = $rec->intKey;
        $i += 1;
        if ($i % 1000 == 0) { 
            $db->resetHash();
        }
    }
    $iterator->close();
    if ($i != nRecords) { 
        user_error("invalid number of iterated objects");
    }
    $key = "";
    $i = 0;
    $iterator = $strIndex->iterator();
    while (($rec = $iterator->next()) != null) {
        if (strcmp($rec->strKey, $key) < 0) {
            $recKey = $rec->strKey;
            user_error("invalid itertion order: $recKey < $key");
        }
        $key = $rec->strKey;
        $i += 1;
        if ($i % 1000 == 0) { 
            $db->resetHash();
        }
    }
    $iterator->close();
    if ($i != nRecords) { 
        user_error("invalid number of iterated objects");
    }
    print("Elapsed time for iterating through " . nRecords*2 . " records: " . (time() - $start) . " seconds\n");

 
    $start = time();
    $key = 1;
    for ($i = 0; $i < nRecords; $i++) { 
        $key = nextKey($key);
        $rec = &$intIndex->get($key);
        if ($rec == null) { 
            print("failed at i=$i key=$key\n");
        }
        $removed = $intIndex->remove($key);
        if (!$removed) { 
            user_error("Failed to remove record from integer index\n"); 
        }        
        $removed = $strIndex->remove(strval($key), &$rec);
        if (!$removed) { 
            user_error("Failed to remove record from string index\n"); 
        }        
        $rec->deallocate();
        if ($i % 1000 == 0) { 
            $db->resetHash();
        }
    }

    print("Elapsed time for deleting " . nRecords . " records: " . (time() - $start) . " seconds\n");
    $db->close();
}    

?>

