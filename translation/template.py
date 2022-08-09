from calendar import c
from typing import Any
from collections import defaultdict

class TemplateManager:
    impls = {str: {str: []}}
    unnamedImpls = {str: []}
    
    @staticmethod
    def nameImpls(name):
        if name not in TemplateManager.impls.keys():
            TemplateManager.impls[name] = {}
        for channel in TemplateManager.unnamedImpls.keys():
            if channel not in TemplateManager.impls[name].keys():
                TemplateManager.impls[name][channel] = []
            TemplateManager.impls[name][channel] += TemplateManager.unnamedImpls[channel]
        TemplateManager.unnamedImpls.clear()

@classmethod
def _template_call(cls, channel, *args, shape={}, **kwargs):
    fil = lambda tu : tu[0].keys() == shape.keys() and all(value == Any or shape[name] == value for name, value in tu[0].items())
    met = lambda tu : sum(value == Any for name, value in tu[0].items())

    assert cls.__name__ in TemplateManager.impls, f'No templates for class {cls.__name__}! Did you use @template ?'
    assert channel in TemplateManager.impls[cls.__name__], f'No templates for channel {channel} in class {cls.__name__}! Did you use @impl(channel) ?'
    filtered = list(filter(fil, TemplateManager.impls[cls.__name__][channel]))
    assert len(filtered) >= 1, f'No implementation for shape {shape} in class {cls.__name__}'
    fun = min(filtered, key=met)[1]

    return fun(*args, **shape, **kwargs)


def template(templateClass):
    TemplateManager.nameImpls(templateClass.__name__)
    setattr(templateClass, '_template_call', _template_call)
    return templateClass

def impl(shape={}, channel='main'):
    def decorator(func):
        if channel not in TemplateManager.unnamedImpls.keys():
            TemplateManager.unnamedImpls[channel] = []
        TemplateManager.unnamedImpls[channel].append((shape, func))
        return func
    return decorator
