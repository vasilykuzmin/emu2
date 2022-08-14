#!/bin/python3

import math

class EnumMeta(type):
    def __getitem__(self, opCode):
        if type(opCode) == int:
            return list(self._enum.items())[opCode][1]
        elif type(opCode) == str:
            return self._enum[opCode][0]
        else:
            raise f'Unknown opCode key: {opCode}'
    
    def __new__(cls, clsname, superclasses, attributedict):
        cls = type.__new__(cls, clsname, superclasses, attributedict)
        if type(cls._type) != tuple:
            cls._type = (cls._type,)
        cls._strtype = tuple(t.__qualname__ for t in cls._type)
        if type(cls._enum) == list:
            cls._enum = {cls._enum[i]: i for i in range(len(cls._enum))}
        for name, value in cls._enum.items():
            value = (cls.__qualname__, value)
            setattr(cls, name, value)
        return cls
    
    def __len__(self):
        return math.ceil(math.log2(len(self._enum)))

class Enum(metaclass=EnumMeta):
    _type = int
    _enum = {}

    def __new__(self, *args) -> None:
        argtype = tuple(arg[0] for arg in args)
        assert argtype == self._strtype, f'Init types mismatch: expected: {self._strtype}, got {argtype}'
        return (self.__qualname__, args)

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
    _type = (ANOT, AINC, BNOT, BINC, OPC,)

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
    
    _type = (LOADALU, OCALU, SAVEALU, PCINC)
    _enum = {
        'ADD': (LOADALU.AB, OCALU(OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.ADD), SAVEALU.SAVE, PCINC.ON),
    }


print(OCCPU[0])
