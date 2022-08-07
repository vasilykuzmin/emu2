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