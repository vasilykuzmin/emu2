#!/bin/python3
from codeManager import CodeManager
import gate


if __name__ == '__main__':
    CodeManager.translateCode((gate.XNOR, {'b': 3}))
    CodeManager.saveCode('translation.hpp')
