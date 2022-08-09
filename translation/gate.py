from typing import Any
from template import template, impl
from pinManager import PinManager
from codeManager import CodeManager
from utils import castTuple, flatten
import math

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
        if len(l) == 1:
            return l[0] + r[0]
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

def COPY(pins):
    res = []
    for pin in pins:
        res += PinManager.requestPin()
        CodeManager.code.append(f'pins[{res[-1]}] = pins[{pin}];')
    return res

def DEBUGOUTPUT(pins, message=''):
    if message != '':
        CodeManager.code.append(f'std::cout << "{message}" << " ";')
    CodeManager.code.append(f'std::cout << {" << ".join([f"int(pins[{pin}])" for pin in pins])} << std::endl;')

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
    @implio({'w': Any}, ('w',), ('1',))
    def wide(input, w):
        last = COPY([input[0]])
        for i in range(w - 1):
            new = AND(last, [input[i + 1]])
            PinManager.freePin(last)
            last = new
        return last

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
    @implio({'w': Any}, ('w',), ('1',))
    def wide(input, w):
        last = COPY([input[0]])
        for i in range(w - 1):
            new = OR(last, [input[i + 1]])
            PinManager.freePin(last)
            last = new
        return last 

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
        sum2, carry2 = FADD(l[b // 2:], r[b // 2:], carry, shape={'b': b - b // 2})
        PinManager.freePin(carry)
        return sum1 + sum2, carry2
    
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
        sum2, carry2 = FADD(l[b // 2:], r[b // 2:], carry, shape={'b': b - b // 2})
        PinManager.freePin(carry)
        return sum1 + sum2, carry2
    
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
class HINC(Gate):
    @implio({'b': Any,}, ('b',), ('b', '1'))
    def parallel(input, b):
        sum1, carry = HINC(input[:b // 2], shape={'b':b // 2})
        sum2, carry2 = INC(input[b // 2:], carry, shape={'b': b - b // 2})
        PinManager.freePin(carry)
        return sum1 + sum2, carry2
    
    @implio({'b': 1,}, ('1', '1'), ('1', '1'))
    def compile(input, b):
        return INC(input, ONE())

@template
class INC(Gate):
    @implio({'b': Any,}, ('b',), ('b', '1'))
    def parallel(input, carry, b):
        sum1, carry = INC(input[:b // 2], carry, shape={'b':b // 2})
        sum2, carry2 = INC(input[b // 2:], carry, shape={'b': b - b // 2})
        PinManager.freePin(carry)
        return sum1 + sum2, carry2
    
    @implio({'b': 1,}, ('1', '1'), ('1', '1'))
    def compile(input, carry, b):
        return HADD(input, carry)

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
class ADEMUX(Gate):
    @implio({'s': Any, 'b': Any})
    def compile(select, input, *regs, s=0, b=0):
        nregs = DEMUX(select, input, shape={'s': s, 'b': b})
        one = ONE()
        nselect = DEMUX(select, one, shape={'s': s, 'b': 1})
        nnregs = ()
        PinManager.freePin(one)
        for i in range(len(regs)):
            nreg = MUX(nselect[i], regs[i], nregs[i])
            PinManager.freePin(nselect[i], nregs[i])
            nnregs += (nreg,)
        return regs

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
        register = COPY(register)
        for i in range(b):
            alternate = zero * 2**i + register[:-2**i]
            nregister = MUX([shift[i]], register, alternate, shape={'s': 1, 'b': 2**b})
            PinManager.freePin(register)
            register = nregister
        PinManager.freePin(zero)
        return register

@template
class BSR(Gate):
    @implio({'b': Any}, ('2**b', 'b'), ('2**b',))
    def compile(register, shift, b):
        zero = ZERO()
        register = COPY(register)
        for i in range(b):
            alternate = register[2**i:] + zero * 2**i
            nregister = MUX([shift[i]], register, alternate, shape={'s': 1, 'b': 2**b})
            PinManager.freePin(register)
            register = nregister
        PinManager.freePin(zero)
        return register

@template
class ALU(Gate):
    @implio({'b': Any}, ('b', 'b', '7'), ('b', '3'))
    def compile(A, B, microcode, b):
        nota = NOT(A, shape={'b': b})
        A = MUX([microcode[0]], A, nota, shape={'s': 1, 'b': b})
        PinManager.freePin(nota)
        
        inca, carrya = HINC(A, shape={'b': b})
        A = MUX([microcode[1]], A, inca, shape={'s': 1, 'b': b})
        PinManager.freePin(inca, carrya)

        notb = NOT(B, shape={'b': b})
        B = MUX([microcode[2]], B, notb, shape={'s': 1, 'b': b})
        PinManager.freePin(notb)
        
        incb, carryb = HINC(B, shape={'b': b})
        B = MUX([microcode[3]], B, incb, shape={'s': 1, 'b': b})
        PinManager.freePin(incb, carryb)

        add, carryFlag = HADD(A, B, shape={'b': b})
        bsl            = BSL (A, B, shape={'b': round(math.log(b, 2))})
        bsr            = BSR (A, B, shape={'b': round(math.log(b, 2))})
        and_           = AND (A, B, shape={'b': b})
        or_            = OR  (A, B, shape={'b': b})
        xor            = XOR (A, B, shape={'b': b})
        
        ret = MUX(microcode[4:7], A, B, add, bsl, bsr, and_, or_, xor, shape={'s': 3, 'b': b})
        PinManager.freePin(add, bsl, bsr, and_, or_, xor)

        nonzeroFlag = OR(ret, shape={'w': b})
        zeroFlag = NOT(nonzeroFlag)
        negativeFlag = [ret[b - 1]]
        positiveFlag = NOT(negativeFlag)
        
        return ret, carryFlag + zeroFlag + nonzeroFlag + positiveFlag + negativeFlag

@template
class RAM(Gate):
    @implio({'b': Any, 's': Any, 'init': 1})
    def init(b, s, init):
        CodeManager.defines.append(f'std::bitset<{2**s}> RAM;')
        CodeManager.code.append('size_t RAMINDEX = 0;')

    @implio({'b': Any, 's': Any}, ('s',), ('b',))
    def compile(ptr, b, s):
        CodeManager.code.append(f'RAMINDEX = {" + ".join([f"(pins[{ptr[i]}] << {i})" for i in range(s)])};')
        # CodeManager.code.append('std::cout << RAMINDEX << std::endl;')
        ret = []
        for i in range(b):
            ret += PinManager.requestPin()
            CodeManager.code.append(f'pins[{ret[-1]}] = RAM[RAMINDEX + {i}];')
        return ret

@template
class CPUMicrocodeLookup(Gate):
    @implio({'init': 1}, (), ())
    def init(init):
        codes = [
            '00000001000',
            '00000011001',
            '00000001001',
            '01000011001',
            '00000101001',
            '00110101001',
            '11000101001',
            '00110101000',
            '00001011001',
            '10101101001',
            '00001101001',
            '10101011001',
            '00001111001',
            '10001111001',
            '00000111001',
            '00001001001',
            '00000000000',
            '00000010001',
            '00000010010',
            '00000010011',
            '00000010100',
            '00000010101',
            '00000010110',
        ]
        cppcodes = ', '.join([f'0b{code[::-1]}' for code in codes])
        CodeManager.defines.append(f'std::bitset<11> CPUMicrocodeLookup[{len(codes)}] = {"{"}{cppcodes}{"}"};')
        CodeManager.defines.append('size_t CPUMicrocodeLookupIndex = 0;')

    @implio({'b': Any,}, ('b',), ('7', '1', '3',))
    def compile(opcode, b):
        CodeManager.code.append(f'CPUMicrocodeLookupIndex = {" + ".join([f"(pins[{opcode[i]}] << {i})" for i in range(b)])};')
        # CodeManager.code.append('std::cout << "CPUMicrocodeLookupIndex " << CPUMicrocodeLookupIndex << std::endl;')
        ret = []
        for i in range(11):
            ret += PinManager.requestPin()
            CodeManager.code.append(f'pins[{ret[-1]}] = CPUMicrocodeLookup[CPUMicrocodeLookupIndex][{i}];')
        return ret[:7], [ret[7]], ret[8:]

@template
class CPU(Gate):
    @implio({'b': Any, 'reg': Any, 'ram': Any})
    def compile(regs, b, reg, ram):
        RAM(shape={'b': b, 's': ram, 'init': 1})
        CPUMicrocodeLookup(shape={'init': 1})
        
        zero = ZERO()
        opCodeLen = 5

        command = RAM(regs[0][:ram], shape={'b': b, 's': ram})
        # DEBUGOUTPUT(command, 'command')
        ALUMicrocode, incpc, save = CPUMicrocodeLookup(command[:5], shape={'b': 5})
        # DEBUGOUTPUT(ALUMicrocode, 'alu microcode');

        A = MUX(command[opCodeLen:opCodeLen + reg], *regs, shape={'s': reg, 'b': b})
        B = MUX(command[opCodeLen + reg:opCodeLen + 2 * reg], *regs, shape={'s': reg, 'b': b})

        ret, flags = ALU(A, B, ALUMicrocode, shape={'b': b})
        PinManager.freePin(ALUMicrocode, B)

        retCarry    = MUX([regs[1][0]], zero * b, ret, shape={'s': 1, 'b': b})
        retZero     = MUX([regs[1][1]], zero * b, ret, shape={'s': 1, 'b': b})
        retNonZero  = MUX([regs[1][2]], zero * b, ret, shape={'s': 1, 'b': b})
        retPositive = MUX([regs[1][3]], zero * b, ret, shape={'s': 1, 'b': b})
        retNegative = MUX([regs[1][4]], zero * b, ret, shape={'s': 1, 'b': b})
        regs[1] = flags + zero * (b - len(flags))

        nA = MUX(save, A, ret, retCarry, retZero, retNonZero, retPositive, retNegative, A, shape={'s': 3, 'b': b})
        PinManager.freePin(save, A, retCarry, retZero, retNonZero, retPositive, retNegative)
        A = nA

        regs = list(ADEMUX(command[opCodeLen:opCodeLen + reg], nA, *regs, shape={'s': reg, 'b': b}))
        PinManager.freePin(nA)

        incregs1, carry = HINC(regs[0], shape={'b': b})
        PinManager.freePin(carry)
        regs[0] = MUX(incpc, regs[0], incregs1, shape={'s': 1, 'b': b})
        PinManager.freePin(incpc, incregs1)
        
        PinManager.freePin(zero)
        return regs

@template
class CPUP(Gate):
    @implio({'b': Any, 'reg': Any, 'ram': Any}, ('b*2**reg',), (('b*2**reg',)))
    def compile(regs, b, reg, ram):
        regs = list(regs[b * i: b * (i + 1)] for i in range(2**reg))
        regs = CPU(regs, shape={'b': b, 'reg': reg, 'ram': ram})
        return flatten(regs)
