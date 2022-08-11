
from pinManager import PinManager

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path().parent.absolute()))
from utils import castTuple

class CodeManager:
    includes = ['#include <iostream>', '#include <bitset>']
    defines = []
    precode = ['char pins[ASIZE];', 'std::bitset<OSIZE> solve(const std::bitset<ISIZE> & ipins) {']
    input = []
    code = []
    output = ['std::bitset<OSIZE> opins;']
    postcode = ['return opins;', '}']

    @staticmethod
    def writeLines(filename, method, lines):
        with open(filename, method) as f:
            f.write('\n'.join(lines) + '\n')

    @staticmethod
    def saveCode(filename):
        CodeManager.writeLines(filename, 'w', CodeManager.includes)
        CodeManager.writeLines(filename, 'a', CodeManager.defines)
        CodeManager.writeLines(filename, 'a', CodeManager.precode)
        CodeManager.writeLines(filename, 'a', CodeManager.input)
        CodeManager.writeLines(filename, 'a', CodeManager.code)
        CodeManager.writeLines(filename, 'a', CodeManager.output)
        CodeManager.writeLines(filename, 'a', CodeManager.postcode)
        
    
    @staticmethod
    def translateCode(gateInfo, mode='a', ramFilename=None):
        if mode == 'a':
            CodeManager.defines.append('#define AUTOMATIC')
        elif mode == 'm':
            CodeManager.defines.append('#define MANUAL')
        elif mode == 'r':
            CodeManager.defines.append('#define REPEAT')
        else:
            raise f'Unknown mode: {mode}'
        
        if ramFilename is not None:
            CodeManager.defines.append(f'#define ramFilename "{ramFilename}"')

        iShape = gateInfo[0](shape=gateInfo[1], channel='i')
        CodeManager.defines.append(f'#define ISIZE {sum(iShape)}')
        if len(iShape) > 0:
            CodeManager.defines.append(f'#define ISHAPE {"{"}{", ".join([str(i) for i in iShape])}{"}"}')

        ipins = []
        i = 0
        for pinSet in iShape:
            ipins.append([])
            for pin in range(pinSet):
                ipins[-1] = ipins[-1] + PinManager.requestPin()
                CodeManager.input.append(f'pins[{ipins[-1][-1]}] = ipins[{i}];')
                i += 1

        opins = castTuple(gateInfo[0](*ipins, shape=gateInfo[1]))
        CodeManager.defines.append(f'#define ASIZE {PinManager.maxNum}')

        o = 0
        for pinSet in opins:
            for pin in pinSet:
                CodeManager.output.append(f'opins[{o}] = pins[{pin}];')
                o += 1

        oShape = gateInfo[0](shape=gateInfo[1], channel='o')
        CodeManager.defines.append(f'#define OSIZE {sum(oShape)}')
        if len(oShape) > 0:
            CodeManager.defines.append(f'#define OSHAPE {"{"}{", ".join([str(o) for o in oShape])}{"}"}')
