PHP_INC=/usr/local/include/php
DYBASEAPI_LIB=dybaseapi.so

CC=g++
COMMON_FLAGS = -I. -I../inc -I$(PHP_INC)/Zend -c -fPIC
CFLAGS = $(COMMON_FLAGS) -O0 -Wall -g
SHFLAGS=-shared -fPIC -ldl


$(DYBASEAPI_LIB): php_dybaseapi.o
	$(CC) $(SHFLAGS) -o $(DYBASEAPI_LIB) php_dybaseapi.o ../lib/libdybase.a

php_dybasepapi.o: php_dybaseapi.c
	$(CC) $(CFLAGS) php_dybaseapi.c
