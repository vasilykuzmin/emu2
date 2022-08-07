from sortedcontainers import SortedSet

class PinManager:
    maxNum = 0
    availablePins = SortedSet()
    
    @staticmethod
    def requestPin(n=1):
        if not len(PinManager.availablePins):
            PinManager.availablePins.add(PinManager.maxNum)
            PinManager.maxNum += 1
        return [PinManager.availablePins.pop()]
    
    @staticmethod
    def freePin(*args):
        for arg in args:
            for i in arg:
                assert i not in PinManager.availablePins, f'Invalid free!'
                PinManager.availablePins.add(i)