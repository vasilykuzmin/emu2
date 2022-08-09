#!/bin/python3
from codeManager import CodeManager
import gate


if __name__ == '__main__':
    CodeManager.translateCode((gate.CPUP, {'b': 16, 'reg': 2, 'ram': 16}), 'r', 'ram.bin')
    CodeManager.saveCode('translation.hpp')
