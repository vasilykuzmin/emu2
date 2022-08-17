#!/bin/python3

from re import S
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


    def handleToken(self, token):
        type_ = 'R' if token[0] == 'R' else ('M' if token[0] == '*' else 'C')
        token = token if type_ == 'C' else token[1:]
        if '__' + token + str(self.macronum) in self.tags.keys():
            token = str(self.tags['__' + token + str(self.macronum)])
        if token in self.tags.keys():
            token = str(self.tags[token])
        if not token.isnumeric():
            token = '0'
        return type_, token

    def emptyHandler(self, tokens):
        self.OC(self.rawOpCodes[tokens[0]], [0, 0])
    
    def OMCHandler(self, tokens):
        atype, tokens[1] = self.handleToken(tokens[1])
        btype, tokens[2] = self.handleToken(tokens[2])
        
        if   atype == 'R' and btype == 'R':
            self.AB(self.rawOpCodes[tokens[0] + '_RR'], tokens)
        elif atype == 'R' and btype == 'C' and int(tokens[1]) == 0:
            self.OC(self.rawOpCodes[tokens[0] + '_OC'], [0, tokens[2]])
        # elif atype == 'R' and btype == 'C' and int(tokens[2]) < self.sC:
        #     self.AC(self.rawOpCodes[tokens[0] + '_RsC'], tokens)
        elif atype == 'R' and btype == 'C':
            self.AbC(self.rawOpCodes[tokens[0] + '_RbC'], tokens)
        elif atype == 'R' and btype == 'M':
            self.AB(self.rawOpCodes[tokens[0] + '_RM'], tokens)
        elif atype == 'M' and btype == 'C' and int(tokens[1]) == 0 and int(tokens[2]) < self.oC:
            self.OC(self.rawOpCodes[tokens[0] + '_OMC'], [0, tokens[2]])
        # elif atype == 'M' and btype == 'C' and int(tokens[2]) < self.sC:
        #     self.AC(self.rawOpCodes[tokens[0] + '_MsC'], tokens)
        elif atype == 'M' and btype == 'C':
            self.AbC(self.rawOpCodes[tokens[0] + '_MbC'], tokens)
        else:
            raise Exception(f'Wrond OMC: {tokens}')
    
    def JMPHandler(self, tokens):
        # hereTag = len(self.code)
        type_, tokens[1] = self.handleToken(tokens[1])

        if   type_ == 'R':
            self.AB(self.rawOpCodes[tokens[0] + '_R'], [0, 0, tokens[1]])
        elif type_ == 'M':
            self.AB(self.rawOpCodes[tokens[0] + '_M'], [0, 0, tokens[1]])
        # elif abs(int(tokens[1]) - hereTag) < self.oC:
        #     if int(tokens[1]) < hereTag:
        #         self.OC(self.rawOpCodes[tokens[0] + '_LC'], [0, hereTag - int(tokens[1])])
        #     else:
        #         self.OC(self.rawOpCodes[tokens[0] + '_RC'], [0, int(tokens[1]) - hereTag])
        else:
            self.AbC(self.rawOpCodes[tokens[0] + '_bC'], [0, 0, tokens[1]])

    def compileLines(self, lines, generateTags=True):
        self.macro = None

        for line in lines:
            tokens = line.split()
            if len(tokens) > 0:
                if tokens[0][0] == '#':
                    continue
                elif tokens[0] == '@macro':
                    self.macro = [tokens[1], tokens[2:], []]
                elif tokens[0] == '@endmacro':
                    self.macros[self.macro[0]] = (self.macro[1], self.macro[2])
                    self.macro = None
                elif self.macro is not None:
                    self.macro[2].append(line)
                elif tokens[0] in self.handlers.keys():
                    self.handlers[tokens[0]](tokens)
                elif tokens[0] in self.macros.keys():
                    macros = self.macros[tokens[0]]
                    overrides = {macros[0][i]: tokens[i + 1] for i in range(len(macros[0]))}
                    override = lambda token: overrides[token] if token in overrides.keys() else (f'R{overrides[token[1:]]}' if token[0] == 'R' and token[1:] in overrides.keys() else (f'R{overrides[token[1:]]}' if token[0] == '*' and token[1:] in overrides.keys() else token))
                    modifiedMacroCode = [' '.join(override(token) for token in line.split()) for line in macros[1]]
                    self.macronum += 1
                    self.compileLines(modifiedMacroCode, generateTags)
                elif tokens[0][-1] == ':':
                    if generateTags:
                        if tokens[0][-2] == '!':
                            self.tags['__' + tokens[0][:-2] + str(self.macronum)] = len(self.code)
                        else:
                            self.tags[tokens[0][:-1]] = len(self.code)
                else:
                    raise Exception(f'No such token: {tokens[0]}')

    def compile(self, ifilename, ofilename, generateTags=True):
        with open(ifilename, 'r') as f:
            lines = f.readlines()

        self.compileLines(lines, generateTags)

        with open(ofilename, 'w') as f:
            f.writelines(self.code)
    
    def __init__(self, ifilename, ofilename, b=16, reg=5) -> None:
        self.b = b
        self.reg = reg
        self.opCodeLen = len2(OCCPU)
        self.sC = 2 ** (b - self.opCodeLen - self.reg)
        self.oC = 2 ** (b - self.opCodeLen)
        self.code = []
        self.macronum = 0
        self.macros = {}
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
        self.macronum = 0
        self.code = []
        self.compile(ifilename, ofilename, generateTags=False)


if __name__ == '__main__':
    Assembler(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
