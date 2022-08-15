#!/bin/python3

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path().parent.absolute()))
from utils import castTuple
from translation.opcode import OCCPU, len2

class Assembler:
    def tobin(self, num, limit=None):
        num = int(num)
        if limit is None:
            limit = self.reg

        if num > 2 ** limit:
            raise 'Number is too large'
            
        return ''.join('1' if num & (2 ** i) else '0' for i in range(limit))

    def caempty(self, opCode):
        rest = '0' * (self.b - self.opCodeLen)
        if len(self.tokens) > 1:
            rest = self.tobin(self.tokens[1], self.b - self.opCodeLen)
        self.code.append(opCode + rest)
    
    def ca1reg(self, opCode):
        rest = '0' * (self.b - self.opCodeLen - self.reg)
        if len(self.tokens) > 2:
            rest = self.tobin(self.tokens[2], self.b - self.opCodeLen - self.reg)
        self.code.append(opCode + self.tobin(self.tokens[1]) + rest)

    def ca2reg(self, opCode):
        rest = '0' * (self.b - self.opCodeLen - 2 * self.reg)
        if len(self.tokens) > 3:
            rest = self.tobin(self.tokens[3], self.b - self.opCodeLen - 2 * self.reg)
        self.code.append(opCode + self.tobin(self.tokens[1]) + self.tobin(self.tokens[2]) + rest)



    def compile(self, ifilename, ofilename, b=16, reg=5):
        with open(ifilename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            self.tokens = line.split()
            if len(self.tokens) > 0:
                if self.tokens[0] in self.opCodes.keys():
                    fun, args = self.opCodes[self.tokens[0]]
                    fun(*castTuple(args))
                else:
                    raise Exception(f'No such token: {self.tokens[0]}')

        with open(ofilename, 'w') as f:
            f.writelines(self.code)
    
    def __init__(self, ifilename, ofilename, b=16, reg=5) -> None:
        self.b = b
        self.reg = reg
        self.code = []
        self.opCodeLen = len2(OCCPU)
        self.opCodes = {}
        _opcode = 0
        for name, value in OCCPU._enum.items():
            load = value[0]
            self.opCodes[name] = (self.ca2reg if load == 0 else (self.ca1reg if load == 1 else self.caempty), self.tobin(_opcode, limit=self.opCodeLen))
            _opcode += 1

        self.compile(ifilename, ofilename)


if __name__ == '__main__':
    Assembler(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
