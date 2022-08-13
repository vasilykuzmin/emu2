#!/bin/python3

import math

class OpCodeMetaclass(type):
    def __new__(cls, clsname, superclasses, attributedict):
        _type = attributedict['_type']
        _enum = attributedict['_enum']
        for name, val in _enum.items():
            assert type(val) == _type, f'OpCode type mismatch must be {_type}, got {type(val)}'
            setattr(cls, name, val)
        return type.__new__(cls, clsname, superclasses, attributedict)
    
    def __len__(self):
        return math.ceil(math.log2(len(self._enum)))


class OpCode(metaclass=OpCodeMetaclass):
    _type = int
    _enum = {}

    def __new__(self, opCode) -> bool:
        if type(opCode) == int:
            return list(self._enum.items())[opCode][1]
        elif type(opCode) == str:
            return self._enum[opCode]
        else:
            raise f'Unknown opCode key: {opCode}'


class OpCodeBit(OpCode):
    _type = int
    _enum = {
        'ZERO': 0,
        'ONE': 1,
    }

print(OpCodeBit.ONE)