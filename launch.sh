#!/bin/sh

./translation/translator.py
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