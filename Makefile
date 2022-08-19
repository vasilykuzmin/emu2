CC=g++
CFLAGS=-Wall

all: clean
	$(CC) $(CFLAGS) devices/screen.hpp tmp/translation.hpp emu.cpp -o tmp/main -l sfml-graphics -l sfml-window -l sfml-system

clean:
	rm -rf *.o emu
