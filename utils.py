import itertools

def castTuple(smth):
    if type(smth) != tuple:
        smth = (smth,)
    return smth

def flatten(smth):
    return list(itertools.chain.from_iterable(smth))

def tobin(num, limit=None):
    if limit is not None:
        return bin(int(num))[2:].zfill(limit)[::-1]
    else:
        return bin(int(num))[2:][::-1]
