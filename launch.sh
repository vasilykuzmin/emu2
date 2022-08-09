#!/bin/sh
b=16
reg=1
ram=16

./assembler/assembler.py ./assembler/main.asm ./ram.bin $b $reg
if [ $? != 0 ]
then
    exit 1
fi

./translation/translator.py $b $reg $ram ./ram.bin
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
./main
if [ $? != 0 ]
then
    exit 1
fi