import itertools

def castTuple(smth):
    if type(smth) != tuple:
        smth = (smth,)
    return smth

def flatten(smth):
    return list(itertools.chain.from_iterable(smth))
