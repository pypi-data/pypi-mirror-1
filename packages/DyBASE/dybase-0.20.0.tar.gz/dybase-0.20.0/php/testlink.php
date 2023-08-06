<?php

/**
 * Example: Supplier-Order-Detail database
 * This examle illustrates usage of one-to-many link in dybase
 */

include "dybase.php";

$fp = fopen("php://stdin", "r");
function input($prompt) { 
    global $fp;
    do {
        print($prompt);
        $in = trim(fgets($fp, 4094));
    } while (strlen($in) == 0);
    return $in;
}
     
 
class Detail extends Persistent { 
    var $name;
    var $color;
    var $weight;
    var $orders;

    function Detail($name, $weight, $color) { 
        $this->name = $name;
        $this->color = $color;
        $this->weight = $weight;
        $this->orders = array();
    }
}


class Supplier extends Persistent { 
    var $name;
    var $address;
    var $orders;

    function Supplier($name, $address) {
        $this->name = $name;
        $this->address = $address;
        $this->orders = array();
    }
}

class Order extends Persistent {
    var $detail;
    var $supplier;
    var $quantity;
    var $price;

    function Order(&$detail, &$supplier, $quantity, $price) {
        $this->detail = &$detail;
        $this->supplier = &$supplier;
        $this->quantity = $quantity;
        $this->price = $price;
    }
}
 
class Root extends Persistent { 
    var $suppliers;
    var $details;
}


$db = new Storage();
if ($db->open("testlink.dbs")) {
    $root = &$db->getRootObject();
    if ($root == null) { 
        $root = &new Root();
        $root->suppliers = &$db->createStrIndex();
        $root->details = &$db->createStrIndex();
        $db->setRootObject($root);
    }
    while (true) {
        print("------------------------------------------\n");
        print("1. Add supplier\n");
        print("2. Add detail\n");
        print("3. Add order\n");
        print("4. Search suppliers\n");
        print("5. Search details\n");
        print("6. Suppliers of detail\n");
        print("7. Deails shipped by supplier\n");
        print("8. Exit\n");
        switch (@intval(input("> "))) { 
          case 1:
            $name = input("Supplier name: ");
            $address = input("Supplier address: ");
            $supplier = &new Supplier($name, $address);
            $root->suppliers->insert($name, $supplier);
            $db->commit();
            break;
          case 2:
            $name = input("Detail name: ");
            $weight = floatval(input("Detail weight: "));
            $color = input("Detail color: ");
            $detail = &new Detail($name, $weight, $color);
            $root->details->insert($name, $detail);
            $db->commit();
            break;
          case 3:
            $supplierName = input("Supplier name: ");
            $supplier = &$root->suppliers->get($supplierName);
            if ($supplier == null) { 
                print("No such supplier $supplierName\n");
                continue;
            }
            $detailName = input("Detail name: ");
            $detail = &$root->details->get($detailName);
            if ($detail == null) { 
                print("No such detail $detailName\n");
                continue;
            }
            $quantity = intval(input("Quantity: "));
            $price = intval(input("Price: "));
            $order = &new Order($detail, $supplier, $quantity, $price);
            $detail->orders[] = &$order;
            $supplier->orders[] = &$order;
            $detail->store();
            $supplier->store();
            $db->commit();
            break;
          case 4:
            $supplierName = input("Supplier name prefix: ");
            $suppliers = &$root->suppliers->find($supplierName, true, $supplierName . chr(255), false);
            if ($suppliers == null) { 
                print("No such suppliers found\n");
            } else { 
                foreach ($suppliers as $s) {
                    print($s->address . "\n");
                    print($s->name . "\t" . $s->address . "\n");
                }
            }
            break;
          case 5:
            $detailName = input("Detail name prefix: ");
            $details = &$root->details->find($detailName, true, $detailName . chr(255), false);
            if ($details == null) { 
                print("No such details found\n");
            } else { 
                foreach ($details as $d) {
                    print($d->name . "\t" . $d->weight . "\t" . $d->color . "\n");
                }
            }
            break;
          case 6:
            $detailName = input("Detail name: ");
            $detail = &$root->details->get($detailName);
            if ($detail == null) { 
                print("No such detail\n");
            } else { 
                foreach ($detail->orders as $o) { 
                    print($o->supplier->name . "\n");
                }
            }
            break;
          case 7:
            $supplierName = input("Supplier name: ");
            $supplier = &$root->suppliers->get($supplierName);
            if ($supplier == null) { 
                print("No such supplier\n");
            } else { 
                foreach ($supplier->orders as $o) { 
                    print($o->detail->name . "\n");
                }
            }
            break;
          case 8:
            $db->close();
            exit("End of session");
          default:
            print("Invalid command\n");
        }
        $db->commit();
    }
}

?>
