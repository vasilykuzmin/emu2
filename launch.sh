#!/bin/sh
b=16
reg=2
ram=16

./assembler/assembler.py ./assembler/main.asm ./tmp/ram.bin $b $reg
if [ $? != 0 ]
then
    exit 1
fi

./translation/translator.py $b $reg $ram ./tmp/ram.bin ./tmp/translation.hpp
if [ $? != 0 ]
then
    exit 1
fi
make
if [ $? != 0 ]
then
    exit 1
fi
# clear
./tmp/main
if [ $? != 0 ]
then
    exit 1
fi
