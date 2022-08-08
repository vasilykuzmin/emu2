from email.policy import default
from typing import Any
from template import template, impl
from pinManager import PinManager
from codeManager import CodeManager
from utils import castTuple, flatten

class Gate:
    defaultShape = {'b': 1}

    def __new__(cls, *args, shape=None, channel='compile', **kwargs):
        if shape is None:
            shape = cls.defaultShape
        return cls._template_call(channel, *args, shape=shape, **kwargs)
    
    @classmethod
    def parallelTemplate(cls, *args, b=1):
        l = castTuple(cls(*[arg[:len(arg) // 2] for arg in args], shape={'b': b // 2}))
        r = castTuple(cls(*[arg[len(arg) // 2:] for arg in args], shape={'b': b - b // 2}))
        return tuple(l[i] + r[i] for i in range(len(l)))


def implio(shape={}, ival=(), oval=()):
    def decorate(fun):
        def i(*args, **kwargs):
            return [eval(i, kwargs) for i in ival]
        impl(shape, 'i')(i)
        def o(*args, **kwargs):
            return [eval(o, kwargs) for o in oval]
        impl(shape, 'o')(o)
        return impl(shape, 'compile')(fun)
    return decorate


def ZERO():
    pin = PinManager.requestPin()
    CodeManager.code.append(f'pins[{pin[0]}] = 0;')
    return pin

def ONE():
    pin = PinManager.requestPin()
    CodeManager.code.append(f'pins[{pin[0]}] = 1;')
    return pin


@template
class NAND(Gate):
    @implio({'b': Any,}, ('b', 'b'), ('b'))
    def parallel(l, r, b):
        return NAND.parallelTemplate(l, r, b=b)
    
    @implio({'b': 1,}, ('1', '1'), ('1'))
    def compile(l, r, b):
        o = PinManager.requestPin()
        CodeManager.code.append(f'pins[{o[0]}] = (pins[{l[0]}] & pins[{r[0]}]) ^ 1;')
        return o

@template
class NOT(Gate):
    @implio({'b': Any,}, ('b'), ('b'))
    def parallel(i, b):
        return NOT.parallelTemplate(i, b=b)
    
    @implio({'b': 1,}, ('1'), ('1'))
    def compile(i, b):
        return NAND(i, i)

@template
class DOUBLER(Gate):
    @implio({'b': Any,}, ('b'), ('b', 'b'))
    def parallel(i, b):
        return DOUBLER.parallelTemplate(i, b=b)
    
    @implio({'b': 1,}, ('1'), ('2'))
    def compile(i, b):
        return i, i

@template
class AND(Gate):
    @implio({'b': Any,}, ('b', 'b'), ('b'))
    def parallel(l, r, b):
        return AND.parallelTemplate(l, r, b=b)
    
    @implio({'b': 1,}, ('1', '1'), ('1'))
    def compile(l, r, b):
        nand = NAND(l, r)
        nt = NOT(nand)
        PinManager.freePin(nand)
        return nt

@template
class OR(Gate):
    @implio({'b': Any,}, ('b', 'b'), ('b'))
    def parallel(l, r, b):
        return OR.parallelTemplate(l, r, b=b)
    
    @implio({'b': 1,}, ('1', '1'), ('1'))
    def compile(l, r, b):
        nt1 = NOT(l)
        nt2 = NOT(r)
        nand = NAND(nt1, nt2)
        PinManager.freePin(nt1, nt2)
        return nand

@template
class NOR(Gate):
    @implio({'b': Any,}, ('b', 'b'), ('b'))
    def parallel(l, r, b):
        return NOR.parallelTemplate(l, r, b=b)
    
    @implio({'b': 1,}, ('1', '1'), ('1'))
    def compile(l, r, b):
        or_ = OR(l, r)
        nt = NOT(or_)
        PinManager.freePin(or_)
        return nt

@template
class XOR(Gate):
    @implio({'b': Any,}, ('b', 'b'), ('b'))
    def parallel(l, r, b):
        return XOR.parallelTemplate(l, r, b=b)
    
    @implio({'b': 1,}, ('1', '1'), ('1'))
    def compile(l, r, b):
        m = NAND(l, r)
        l = NAND(l, m)
        r = NAND(m, r)
        PinManager.freePin(m)
        ret = NAND(l, r)
        PinManager.freePin(l, r)
        return ret

@template
class XNOR(Gate):
    @implio({'b': Any,}, ('b', 'b'), ('b'))
    def parallel(l, r, b):
        return XNOR.parallelTemplate(l, r, b=b)
    
    @implio({'b': 1,}, ('1', '1'), ('1'))
    def compile(l, r, b):
        xor = XOR(l, r)
        nt = NOT(xor)
        PinManager.freePin(xor)
        return nt

@template
class HADD(Gate):
    @implio({'b': Any,}, ('b', 'b'), ('b', '1'))
    def parallel(l, r, b):
        sum1, carry = HADD(l[:b // 2], r[:b // 2], shape={'b':b // 2})
        sum2, carry = FADD(l[b // 2:], r[b // 2:], carry, shape={'b': b - b // 2})
        return sum1 + sum2, carry
    
    @implio({'b': 1,}, ('1', '1'), ('1', '1'))
    def compile(l, r, b):
        sum = XOR(l, r)
        carry = AND(l, r)
        return sum, carry

@template
class FADD(Gate):
    @implio({'b': Any,}, ('b', 'b', '1'), ('b', '1'))
    def parallel(l, r, carry, b):
        sum1, carry = FADD(l[:b // 2], r[:b // 2], carry, shape={'b':b // 2})
        sum2, carry = FADD(l[b // 2:], r[b // 2:], carry, shape={'b': b - b // 2})
        return sum1 + sum2, carry
    
    @implio({'b': 1,}, ('1', '1', '1'), ('1', '1'))
    def compile(l, r, carry, b):
        xor1 = XOR(l, r)
        sum = XOR(xor1, carry)
        and1 = AND(l, r)
        and2 = AND(xor1, carry)
        PinManager.freePin(xor1)
        carry = OR(and1, and2)
        PinManager.freePin(and1, and2)
        return sum, carry

@template
class MUX(Gate):
    defaultShape = {'s': 1}

    @implio({'s': Any, 'b': Any})
    def width(select, *input, s, b):
        mux1 = MUX(select[:-1], *(input[:2**(s - 1)]), shape={'s': s - 1, 'b': b})
        mux2 = MUX(select[:-1], *(input[2**(s - 1):]), shape={'s': s - 1, 'b': b})
        mux3 = MUX([select[-1]], mux1, mux2, shape={'s': 1, 'b': b})
        PinManager.freePin(mux1, mux2)
        return mux3

    @implio({'s': 1, 'b': Any})
    def parallel(select, l, r, s=0, b=0):
        return flatten(MUX(select, [l[i]], [r[i]]) for i in range(b))

    @implio({'s': 1,}, ('1', '1', '1'), ('1'))
    def compile(select, l, r, s=0):
        nt = NOT(select)
        and1 = AND(l, nt)
        PinManager.freePin(nt)
        and2 = AND(r, select)
        or_ = OR(and1, and2)
        PinManager.freePin(and1, and2)
        return or_

@template
class MUXP(Gate):
    @implio({'s': Any, 'b': Any}, ('s', 'b*2**s'), ('b',))
    def decorate(select, input, s, b):
        unpacked = [input[i * b:(i + 1) * b] for i in range(2**s)]
        return flatten(castTuple(MUX(select, *unpacked, shape={'s':s, 'b':b})))

@template
class DEMUX(Gate):
    defaultShape = {'s': 1}

    @implio({'s': Any, 'b': Any})
    def width(select, input, s, b):
        demux1i, demux2i = DEMUX([select[-1]], input, shape={'s': 1, 'b': b})
        demux1 = DEMUX(select[:-1], demux1i, shape={'s': s - 1, 'b': b})
        demux2 = DEMUX(select[:-1], demux2i, shape={'s': s - 1, 'b': b})
        PinManager.freePin(demux1i, demux2i)
        return demux1 + demux2
    
    @implio({'s': 1, 'b': Any})
    def parallel(select, input, s, b):
        ll, rr = [], []
        for i in range(b):
            l, r = DEMUX(select, [input[i]])
            ll, rr = ll + l, rr + r
        return ll, rr
    
    @implio({'s': 1,}, ('1', '1'), ('2'))
    def compile(select, input, s):
        nt = NOT(select)
        and1 = AND(input, nt)
        PinManager.freePin(nt)
        and2 = AND(input, select)
        return and1, and2

@template
class DEMUXP(Gate):
    @implio({'s': Any, 'b': Any}, ('s', 'b'), ('b*2**s',))
    def decorate(select, input, s, b):
        return flatten(DEMUX(select, input, shape={'s': s, 'b': b}))

@template
class BSL(Gate):
    @implio({'b': Any}, ('2**b', 'b'), ('2**b',))
    def compile(register, shift, b):
        zero = ZERO()
        for i in range(b):
            alternate = zero * 2**i + register[:-2**i]
            nregister = MUX([shift[i]], register, alternate, shape={'s': 1, 'b': 2**b})
            if i != 0:
                PinManager.freePin(register)
            register = nregister
        PinManager.freePin(zero)
        return register

@template
class BSR(Gate):
    @implio({'b': Any}, ('2**b', 'b'), ('2**b',))
    def compile(register, shift, b):
        zero = ZERO()
        for i in range(b):
            alternate = register[2**i:] + zero * 2**i
            nregister = MUX([shift[i]], register, alternate, shape={'s': 1, 'b': 2**b})
            if i != 0:
                PinManager.freePin(register)
            register = nregister
        PinManager.freePin(zero)
        return register
