CC=g++
CFLAGS=-Wall

all: clean
	$(CC) $(CFLAGS) translation.hpp emu.cpp -o main

clean:
	rm -rf *.o emu