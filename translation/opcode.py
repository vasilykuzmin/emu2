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
        cls._lateInit()
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
    @classmethod
    def _lateInit(cls):
        pass

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
    class ALUIN(Enum):
        _enum = [
            'AB',
            'AC',
            'OC',
            'AbC',
        ]
    class RAMIN(Enum):
        _enum = [
            'NO',
            'ZERO',
            'A',
            'B',
        ]

    
    class ALUOUT(Enum):
        _enum = [
            'NO',
            'SAVE',
            'CARRY',
            'ZERO',
            'NONZERO',
            'POSITIVE',
            'NEGATIVE',
        ]

    class RAMOUT(Enum):
        _enum = [
            'NO',
            'ZERO',
            'A',
            'B',
        ]

    class PCINC(Enum):
        _enum = [
            'P0',
            'P1',
            'P2',
            'P3',
        ]
    
    _enum = {
        'NOP' : (ALUIN.OC , RAMIN.NO, (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.A  ), ALUOUT.NO     , RAMOUT.NO, PCINC.P1),
        'STOP': (ALUIN.OC , RAMIN.NO, (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.A  ), ALUOUT.NO     , RAMOUT.NO, PCINC.P0),
    }
    
    @classmethod
    def addOMC(cls, name, alu, save):
        cls._enum[f'{name}_RR' ] = (cls.ALUIN.AB , cls.RAMIN.NO, alu, save, cls.RAMOUT.NO, cls.PCINC.P1)
        cls._enum[f'{name}_OC' ] = (cls.ALUIN.OC , cls.RAMIN.NO, alu, save, cls.RAMOUT.NO, cls.PCINC.P1)
        cls._enum[f'{name}_RsC'] = (cls.ALUIN.AC , cls.RAMIN.NO, alu, save, cls.RAMOUT.NO, cls.PCINC.P1)
        cls._enum[f'{name}_RbC'] = (cls.ALUIN.AbC, cls.RAMIN.NO, alu, save, cls.RAMOUT.NO, cls.PCINC.P2)
        cls._enum[f'{name}_RM' ] = (cls.ALUIN.AB , cls.RAMIN.B , alu, save, cls.RAMOUT.B , cls.PCINC.P1)
        cls._enum[f'{name}_MR' ] = (cls.ALUIN.AB , cls.RAMIN.A , alu, save, cls.RAMOUT.A , cls.PCINC.P1)
        cls._enum[f'{name}_OMC'] = (cls.ALUIN.OC , cls.RAMIN.A , alu, save, cls.RAMOUT.A , cls.PCINC.P1)
        cls._enum[f'{name}_MsC'] = (cls.ALUIN.AC , cls.RAMIN.A , alu, save, cls.RAMOUT.A , cls.PCINC.P1)
        cls._enum[f'{name}_MbC'] = (cls.ALUIN.AbC, cls.RAMIN.A , alu, save, cls.RAMOUT.A , cls.PCINC.P2)

    @classmethod
    def addJMP(cls, name, save):
        cls._enum[f'{name}_LC'] = (cls.ALUIN.OC , cls.RAMIN.NO, (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.ON , OCALU.BINC.ON , OCALU.OPC.ADD), save, cls.RAMOUT.NO, cls.PCINC.P0)
        cls._enum[f'{name}_RC'] = (cls.ALUIN.OC , cls.RAMIN.NO, (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.ADD), save, cls.RAMOUT.NO, cls.PCINC.P0)
        cls._enum[f'{name}_bC'] = (cls.ALUIN.AbC, cls.RAMIN.NO, (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.B  ), save, cls.RAMOUT.NO, cls.PCINC.P0) # A = R0
        cls._enum[f'{name}_R' ] = (cls.ALUIN.AB , cls.RAMIN.NO, (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.B  ), save, cls.RAMOUT.NO, cls.PCINC.P0) # A = R0
        cls._enum[f'{name}_M' ] = (cls.ALUIN.AB , cls.RAMIN.B , (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.B  ), save, cls.RAMOUT.NO, cls.PCINC.P0) # A = R0

    @classmethod
    def _lateInit(cls):
        cls.addOMC('ADD' , (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.ADD), cls.ALUOUT.SAVE)
        cls.addOMC('SUB' , (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.ON , OCALU.BINC.ON , OCALU.OPC.ADD), cls.ALUOUT.SAVE)
        cls.addOMC('SUBL', (OCALU.ANOT.ON , OCALU.AINC.ON , OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.ADD), cls.ALUOUT.SAVE)
        cls.addOMC('CP'  , (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.ON , OCALU.BINC.ON , OCALU.OPC.ADD), cls.ALUOUT.NO  )
        cls.addOMC('AND' , (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.AND), cls.ALUOUT.SAVE)
        cls.addOMC('NAND', (OCALU.ANOT.ON , OCALU.AINC.OFF, OCALU.BNOT.ON , OCALU.BINC.OFF, OCALU.OPC.OR ), cls.ALUOUT.SAVE)
        cls.addOMC('OR'  , (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.OR ), cls.ALUOUT.SAVE)
        cls.addOMC('NOR' , (OCALU.ANOT.ON , OCALU.AINC.OFF, OCALU.BNOT.ON , OCALU.BINC.OFF, OCALU.OPC.AND), cls.ALUOUT.SAVE)
        cls.addOMC('XOR' , (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.XOR), cls.ALUOUT.SAVE)
        cls.addOMC('XNOR', (OCALU.ANOT.ON , OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.XOR), cls.ALUOUT.SAVE)
        cls.addOMC('BSL' , (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.BSL), cls.ALUOUT.SAVE)
        cls.addOMC('BSR' , (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.BSR), cls.ALUOUT.SAVE)
        cls.addOMC('SET' , (OCALU.ANOT.OFF, OCALU.AINC.OFF, OCALU.BNOT.OFF, OCALU.BINC.OFF, OCALU.OPC.B  ), cls.ALUOUT.SAVE)

        cls.addJMP('JMP', cls.ALUOUT.SAVE    )
        cls.addJMP('JC' , cls.ALUOUT.CARRY   )
        cls.addJMP('JZ' , cls.ALUOUT.ZERO    )
        cls.addJMP('JNZ', cls.ALUOUT.NONZERO )
        cls.addJMP('JP' , cls.ALUOUT.POSITIVE)
        cls.addJMP('JN' , cls.ALUOUT.NEGATIVE)