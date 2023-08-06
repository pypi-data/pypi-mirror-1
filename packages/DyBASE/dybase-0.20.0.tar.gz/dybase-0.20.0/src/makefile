# -*- makefile -*-
# Makefile for GNU C


# Place where to copy DYBASE header files
INCSPATH=/usr/local/include/dybase

#Place where to copy DYBASE library
LIBSPATH=/usr/local/lib


OBJS = btree.o database.o dybase.o file.o pagepool.o 

INCS = database.h btree.h buffer.h file.h hashtab.h pagepool.h stdtp.h sync.h ../inc/dybase.h

DYBASE_LIB = ../lib/libdybase.a
DYBASE_DLL = ../lib/libdybase.so


#
# threads settings - please comment this lines for single-threaded libs
#
ifdef NO_PTHREADS
TFLAGS=-DNO_PTHREADS
else
TFLAGS=-pthread
endif


CC = g++
COMMON_FLAGS = $(TFLAGS) -I. -I../inc -c -fPIC
CFLAGS = $(COMMON_FLAGS) -O0 -Wall -g
#CFLAGS = $(COMMON_FLAGS) -O5 -Wall 

SHFLAGS=-shared

LD = $(CC)
LDFLAGS = -MDd -Zi -nologo
#LDFLAGS = -MT -Zi -nologo

AR = ar
ARFLAGS = -cru

ifneq (,$(findstring freebsd,$(OSTYPE)))
RANLIB = ranlib
else
RANLIB = true
endif

all: $(DYBASE_LIB) $(DYBASE_DLL)

btree.o: btree.cpp $(INCS)
	$(CC) $(CFLAGS) btree.cpp

database.o: database.cpp $(INCS)
	$(CC) $(CFLAGS) database.cpp

file.o: file.cpp $(INCS)
	$(CC) $(CFLAGS) file.cpp

pagepool.o: pagepool.cpp $(INCS)
	$(CC) $(CFLAGS) pagepool.cpp

dybase.o: dybase.cpp $(INCS)
	$(CC) $(CFLAGS) -DDYBASE_DLL dybase.cpp

$(DYBASE_LIB): $(OBJS)
	rm -f $(DYBASE_LIB)
	$(AR) $(ARFLAGS) $(DYBASE_LIB) $(OBJS)
	$(RANLIB) $(DYBASE_LIB)

$(DYBASE_DLL): $(OBJS)
	rm -f $(DYBASE_DLL)
	$(CC) $(SHFLAGS) -o $(DYBASE_DLL) $(OBJS)

cleanobj:
	find .. -name "*.o" -exec rm {} \;

cleanlib:
	find .. -name "*.dll" -exec rm {} \;
	find .. -name "*.a" -exec rm {} \;
	find .. -name "*.so" -exec rm {} \;

cleandbs:
	find .. -name "*.dbs" -exec rm {} \;

tgz:	cleanobj cleanlib cleandbs
	cd ../..; tar cvzf dybase.tgz dybase

install: $(DYBASE_LIB) $(DYBASE_DLL)
	mkdir -p $(INCSPATH)
	cp ../inc/dybase.h $(INCSPATH)
	mkdir -p $(LIBSPATH)
	cp $(DYBASE_LIB) $(DYBASE_DLL) $(LIBSPATH)
