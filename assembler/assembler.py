#!/bin/python3

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path().parent.absolute()))
from utils import castTuple

class Assembler:
    def tobin(self, num, *args, mode='reg'):
        num = int(num)
        if mode == 'reg':
            b = self.reg
        elif mode == 'manual':
            b = args[0]

        if num > 2 ** b:
            raise 'Number is too large'
            
        return ''.join('1' if num & (2 ** i) else '0' for i in range(b))

    def caempty(self, opCode):
        rest = '0' * (self.b - self.opCodeLen)
        if len(self.tokens) >= 3:
            rest = self.tobin(self.tokens[3], self.b - self.opCodeLen, mode='manual')
        self.code.append(opCode + rest)
    
    def ca1reg(self, opCode):
        rest = '0' * (self.b - self.opCodeLen - self.reg)
        if len(self.tokens) >= 3:
            rest = self.tobin(self.tokens[3], self.b - self.opCodeLen - self.reg, mode='manual')
        self.code.append(opCode + self.tobin(self.tokens[1]) + rest)

    def ca2reg(self, opCode):
        rest = '0' * (self.b - self.opCodeLen - 2 * self.reg)
        if len(self.tokens) >= 3:
            rest = self.tobin(self.tokens[3], self.b - self.opCodeLen - 2 * self.reg, mode='manual')
        self.code.append(opCode + self.tobin(self.tokens[1]) + self.tobin(self.tokens[2]) + rest)
    
    def cajmp(self, opcode):
        self.code.append(opcode + '0' * self.reg + self.tobin(self.tokens[1], self.b - self.opCodeLen - self.reg, mode='manual'))


    def compile(self, ifilename, ofilename, b=16, reg=5):
        with open(ifilename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            self.tokens = line.split()
            if len(self.tokens) > 0:
                if self.tokens[0] in self.opCodes.keys():
                    fun, args = self.opCodes[self.tokens[0]]
                    fun(*castTuple(args))

        with open(ofilename, 'w') as f:
            f.writelines(self.code)
    
    def __init__(self, ifilename, ofilename, b=16, reg=5) -> None:
        self.b = b
        self.reg = reg
        self.code = []
        self.opCodeLen = 5
        self.opCodes = {
                'NOP' : (self.caempty, '00000'),
                'MOV' : (self.ca2reg , '10000'),
                'SET' : (self.ca1reg , '01000'),
                'INC' : (self.ca1reg , '11000'),
                'ADD' : (self.ca2reg , '00100'),
                'SUB' : (self.ca2reg , '10100'),
                'ASUB': (self.ca2reg , '01100'),
                'NSUB': (self.ca2reg , '11100'),
                'AND' : (self.ca2reg , '00010'),
                'NAND': (self.ca2reg , '10010'),
                'OR'  : (self.ca2reg , '01010'),
                'NOR' : (self.ca2reg , '11010'),
                'XOR' : (self.ca2reg , '00110'),
                'XNOR': (self.ca2reg , '10110'),
                'BSL' : (self.ca2reg , '01110'),
                'BSR' : (self.ca2reg , '11110'),
                'STOP': (self.caempty, '00001'),
                'JMP' : (self.cajmp  , '10001'),
                'JC'  : (self.cajmp  , '01001'),
                'JZ'  : (self.cajmp  , '11001'),
                'JNZ' : (self.cajmp  , '00101'),
                'JP'  : (self.cajmp  , '10101'),
                'JN'  : (self.cajmp  , '01101'),
            }

        self.compile(ifilename, ofilename)


if __name__ == '__main__':
    Assembler(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
