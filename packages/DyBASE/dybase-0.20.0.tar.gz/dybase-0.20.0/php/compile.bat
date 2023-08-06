if not defined PHP_INC set PHP_INC=\php-4.3.4\Zend
if not defined PHP_LIB set PHP_LIB=\php-4.3.4-Win32\php4ts.lib

cl -ML  /GX -LD -Zi -DZTS -DZEND_DEBUG=0 -DZEND_WIN32 -DWIN32 -I%PHP_INC% -I..\inc -Fephp_dybaseapi.dll php_dybaseapi.c  ..\lib\dybasedll.lib %PHP_LIB%



