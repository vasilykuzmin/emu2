import math

import sys, pathlib
sys.path.insert(0, str(pathlib.Path().parent.absolute()))
from utils import tobin


def len2(o):
    return o.__len2__()

class EnumMeta(type):
    @staticmethod
    def _recRender(obj):
        if type(obj) == str:
            return obj
        else:
            return ''.join(EnumMeta._recRender(nobj) for nobj in obj)
    
    def _recShape(obj):
        if type(obj) == str:
            return len(obj)
        else:
            return tuple(EnumMeta._recShape(nobj) for nobj in obj)

    def __new__(cls, clsname, superclasses, attributedict):
        cls = type.__new__(cls, clsname, superclasses, attributedict)
        if type(cls._enum) == list:
            cls._render = {cls._enum[i]: tobin(i, len2(cls)) for i in range(len(cls._enum))}
        else:
            cls._render = {name: EnumMeta._recRender(value) for name, value in cls._enum.items()}
        for name, value in cls._render.items():
            setattr(cls, name, value)
        return cls
    
    def __len__(cls):
        return len(cls._enum)
    
    def __len2__(cls):
        return math.ceil(math.log2(len(cls._enum)))

    def __getitem__(self, opCode):
        if type(opCode) == int:
            return list(self._render.values())[opCode]
        elif type(opCode) == str:
            return self._render[opCode]
        else:
            raise Exception(f'Unknown opCode key: {opCode}')

    def _shape(self):
        value = list(self._enum.values())[0]
        return EnumMeta._recShape(value)


class Enum(metaclass=EnumMeta):
    _enum = {}

class BitEnum(Enum):
    _enum = ['OFF', 'ON']


class OCALU(Enum):
    class ANOT(BitEnum):
        pass
    class AINC(BitEnum):
        pass
    class BNOT(BitEnum):
        pass
    class BINC(BitEnum):
        pass
    class OPC(Enum):
        _enum = [
            'A',
            'B',
            'ADD',
            'BSL',
            'BSR',
            'AND',
            'OR',
            'XOR',
        ]

class OCCPU(Enum):
    class LOADALU(Enum):
        _enum = [
            'AB',
            'AC',
            'OC',
        ]
    
    class SAVEALU(Enum):
        _enum = [
            'NOTSAVE',
            'SAVE',
            'CARRY',
            'ZERO',
            'NONZERO',
            'POSITIVE',
            'NEGATIVE',
        ]

    class PCINC(BitEnum):
        pass
    
    _enum = {
        'NOP': (LOADALU.OC, (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.A  ), SAVEALU.NOTSAVE, PCINC.ON ),
        'ADD': (LOADALU.AB, (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.ADD), SAVEALU.SAVE   , PCINC.ON ),
        'JMP': (LOADALU.OC, (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.B  ), SAVEALU.SAVE   , PCINC.OFF),
    }
