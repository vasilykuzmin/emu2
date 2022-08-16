CC=g++
CFLAGS=-Wall -o3

all: clean
	$(CC) $(CFLAGS) tmp/translation.hpp emu.cpp -o tmp/main

clean:
	rm -rf *.o emu
