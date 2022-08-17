#!/bin/python3

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path().parent.absolute()))
from utils import castTuple, tobin
from translation.opcode import OCCPU, len2

class Assembler:
    def AB(self, opCode, tokens):
        rest = '0' * (self.b - self.opCodeLen - 2 * self.reg)
        self.code.append(opCode + tobin(tokens[1], self.reg) + tobin(tokens[2], self.reg) + rest)
    
    def AC(self, opCode, tokens):
        self.code.append(opCode + tobin(tokens[1], self.reg) + tobin(tokens[2], self.b - self.opCodeLen - self.reg))

    def OC(self, opCode, tokens):
        self.code.append(opCode + tobin(tokens[1], self.b - self.opCodeLen))
    
    def AbC(self, opCode, tokens):
        rest = '0' * (self.b - self.opCodeLen - self.reg)
        self.code.append(opCode + tobin(tokens[1], self.reg) + rest)
        self.code.append(tobin(tokens[2], self.b))


    def emptyHandler(self, tokens):
        self.OC(self.rawOpCodes[tokens[0]], [0, 0])
    
    def OMCHandler(self, tokens):
        atype = 'R' if tokens[1][0] == 'R' else ('M' if tokens[1][0] == '*' else 'C')
        btype = 'R' if tokens[2][0] == 'R' else ('M' if tokens[2][0] == '*' else 'C')
        tokens[1] = tokens[1] if atype == 'C' else tokens[1][1:]
        tokens[2] = tokens[2] if btype == 'C' else tokens[2][1:]

        if   atype == 'R' and btype == 'R':
            self.AB(self.rawOpCodes[tokens[0] + '_RR'], tokens)
        elif atype == 'R' and btype == 'C' and int(tokens[1]) == 0:
            self.OC(self.rawOpCodes[tokens[0] + '_OC'], [0, tokens[2]])
        elif atype == 'R' and btype == 'C' and int(tokens[2]) < self.sC:
            self.AC(self.rawOpCodes[tokens[0] + '_RsC'], tokens)
        elif atype == 'R' and btype == 'C':
            self.AbC(self.rawOpCodes[tokens[0] + '_RbC'], tokens)
        elif atype == 'R' and btype == 'M':
            self.AB(self.rawOpCodes[tokens[0] + '_RM'], tokens)
        elif atype == 'M' and btype == 'C' and int(tokens[1]) == 0 and int(tokens[2]) < self.oC:
            self.OC(self.rawOpCodes[tokens[0] + '_OMC'], [0, tokens[2]])
        elif atype == 'M' and btype == 'C' and int(tokens[2]) < self.sC:
            self.AC(self.rawOpCodes[tokens[0] + '_MsC'], tokens)
        elif atype == 'M' and btype == 'C':
            self.AbC(self.rawOpCodes[tokens[0] + '_MbC'], tokens)
    
    def JMPHandler(self, tokens):
        hereTag = len(self.code)
        if tokens[1] in self.tags.keys():
            tokens[1] = str(self.tags[tokens[1]])
        if   tokens[1][0] == 'R':
            self.AB(self.rawOpCodes[tokens[0] + '_M'], [0, tokens[1][1:]])
        elif abs(int(tokens[1]) - hereTag) < self.oC:
            if int(tokens[1]) < hereTag:
                self.OC(self.rawOpCodes[tokens[0] + '_LC'], [0, hereTag - int(tokens[1])])
            else:
                self.OC(self.rawOpCodes[tokens[0] + '_RC'], [0, int(tokens[1]) - hereTag])
        else:
            self.AbC(self.rawOpCodes[tokens[0] + '_bC'], tokens)

    def compile(self, ifilename, ofilename, b=16, reg=5):
        with open(ifilename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            tokens = line.split()
            if len(tokens) > 0:
                if tokens[0] in self.handlers.keys():
                    self.handlers[tokens[0]](tokens)
                elif tokens[0][-1] == ':':
                    self.tags[tokens[0][:-1]] = len(self.code)
                else:
                    raise Exception(f'No such token: {tokens[0]}')

        with open(ofilename, 'w') as f:
            f.writelines(self.code)
    
    def __init__(self, ifilename, ofilename, b=16, reg=5) -> None:
        self.b = b
        self.reg = reg
        self.opCodeLen = len2(OCCPU)
        self.sC = 2 ** (b - self.opCodeLen - self.reg)
        self.oC = 2 ** (b - self.opCodeLen)
        self.code = []
        self.tags = {}
        self.rawOpCodes = {}
        _opcode = 0
        for name in OCCPU._enum.keys():
            self.rawOpCodes[name] = tobin(_opcode, self.opCodeLen)
            _opcode += 1
        
        self.handlers = {
            'NOP' : self.emptyHandler,
            'STOP': self.emptyHandler,

            'ADD' : self.OMCHandler,
            'SUB' : self.OMCHandler,
            'SUBL': self.OMCHandler,
            'CP'  : self.OMCHandler,
            'AND' : self.OMCHandler,
            'NAND': self.OMCHandler,
            'OR'  : self.OMCHandler,
            'NOR' : self.OMCHandler,
            'XOR' : self.OMCHandler,
            'XNOR': self.OMCHandler,
            'BSL' : self.OMCHandler,
            'BSR' : self.OMCHandler,
            'SET' : self.OMCHandler,

            'JMP' : self.JMPHandler,
            'JC'  : self.JMPHandler,
            'JZ'  : self.JMPHandler,
            'JNZ' : self.JMPHandler,
            'JP'  : self.JMPHandler,
            'JN'  : self.JMPHandler,
        }

        self.compile(ifilename, ofilename)


if __name__ == '__main__':
    Assembler(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
