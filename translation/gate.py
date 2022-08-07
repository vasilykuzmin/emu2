from typing import Any
from template import template, impl
from pinManager import PinManager
from codeManager import CodeManager

class Gate:
    def __new__(cls, *args, shape={}, channel='compile', **kwargs):
        return cls._template_call(channel, *args, shape=shape, **kwargs)
    
    @classmethod
    def parallelTemplate(cls, *args, b=1):
        return cls(*[arg[:len(arg) // 2] for arg in args], shape={'b': b // 2}) + cls(*[arg[len(arg) - len(arg) // 2:] for arg in args], shape={'b': b - b // 2})


def implio(shape, ival=('0',), oval=('0',)):
    def decorate(fun):
        def i(*args, **kwargs):
            return [eval(i, kwargs) for i in ival]
        impl(shape, 'i')(i)
        def o(*args, **kwargs):
            return [eval(o, kwargs) for o in oval]
        impl(shape, 'o')(o)
        return impl(shape, 'compile')(fun)
    return decorate


@template
class NAND(Gate):
    @implio({'b': Any,}, ('b', 'b'), ('b'))
    def parallel(l, r, b):
        return NAND.parallelTemplate(l, r, b=b),
    
    @implio({'b': 1,}, ('1', '1'), ('1'))
    def compile(l, r, b):
        o = PinManager.requestPin()
        CodeManager.code.append(f'pins[{o[0]}] = (pins[{l[0]}] & pins[{r[0]}]) ^ 1;')
        return o,