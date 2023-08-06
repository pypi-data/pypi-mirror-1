DYBASEAPI_LIB=dybaseapi.so

CC=g++
COMMON_FLAGS = -I../inc -c -fPIC
CFLAGS = $(COMMON_FLAGS) -DNDEBUG -O3 -Wall -g
SHFLAGS=-shared


$(DYBASEAPI_LIB): dybaseapi.o
	$(CC) $(SHFLAGS) -o $(DYBASEAPI_LIB) dybaseapi.o ../lib/libdybase.a

dybaseapi.o: dybaseapi.c
	$(CC) $(CFLAGS) dybaseapi.c 


