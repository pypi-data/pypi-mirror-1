RUBY_HOME=/usr/local/lib/ruby/1.8/i686-linux/
DYBASEAPI_LIB=dybaseapi.so

CC=g++
COMMON_FLAGS = -I. -I../inc -I$(RUBY_HOME) -c -fPIC -L ../lib/
CFLAGS = $(COMMON_FLAGS) -O2 -Wall -g
SHFLAGS=-shared


$(DYBASEAPI_LIB): dybaseapi.o ../lib/libdybase.a
	$(CC) $(SHFLAGS) -o $(DYBASEAPI_LIB) dybaseapi.o  -ldybase -lc

dybaseapi.o: dybaseapi.c
	$(CC) $(CFLAGS) dybaseapi.c 


