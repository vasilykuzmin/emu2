#!/bin/python3

import sys

def tobin(num, reg):
    num = int(num)
    if num > 2 ** reg:
        raise 'Number is too large'
    return ''.join('1' if num & (2 ** i) else '0' for i in range(reg))

def compile(ifilename, ofilename, b=16, reg=5):
    code = []

    opCodeLen = 5

    with open(ifilename, 'r') as f:
        lines = f.readlines()

    for line in lines:
        tokens = line.split()
        if len(tokens) > 0:
            if tokens[0] == 'NOP':
                code.append('0' * b)
            elif tokens[0] == 'MOV':
                code.append('10000' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'SET':
                code.append('01000' + tobin(tokens[1], b - opCodeLen))
                
            elif tokens[0] == 'INC':
                code.append('11000' + tobin(tokens[1], reg) + tobin(tokens[2], b - opCodeLen - reg))
            elif tokens[0] == 'ADD':
                code.append('00100' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'SUB':
                code.append('10100' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'ASUB':
                code.append('01100' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'NSUB':
                code.append('11100' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'AND':
                code.append('00010' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'NAND':
                code.append('10010' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'OR':
                code.append('01010' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'NOR':
                code.append('11010' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'XOR':
                code.append('00110' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'XNOR':
                code.append('10110' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'BSL':
                code.append('01110' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            elif tokens[0] == 'BSR':
                code.append('11110' + tobin(tokens[1], reg) + tobin(tokens[2], reg) + '0' * (b - opCodeLen - 2 * reg))
            
            elif tokens[0] == 'STOP':
                code.append('00001' + '0' * (b - opCodeLen))
            elif tokens[0] == 'JMP':
                code.append('10001' + '0' * reg + tobin(tokens[1], b - opCodeLen - reg))
            elif tokens[0] == 'JC':
                code.append('01001' + '0' * reg + tobin(tokens[1], b - opCodeLen - reg))
            elif tokens[0] == 'JZ':
                code.append('11001' + '0' * reg + tobin(tokens[1], b - opCodeLen - reg))
            elif tokens[0] == 'JNZ':
                code.append('00101' + '0' * reg + tobin(tokens[1], b - opCodeLen - reg))
            elif tokens[0] == 'JP':
                code.append('10101' + '0' * reg + tobin(tokens[1], b - opCodeLen - reg))
            elif tokens[0] == 'JN':
                code.append('01101' + '0' * reg + tobin(tokens[1], b - opCodeLen - reg))

    with open(ofilename, 'w') as f:
        f.writelines(code)

if __name__ == '__main__':
    compile(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
