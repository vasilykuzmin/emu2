CC=g++
CFLAGS=-Wall -o3

all: clean
	$(CC) $(CFLAGS) translation.hpp emu.cpp -o main

clean:
	rm -rf *.o emu
