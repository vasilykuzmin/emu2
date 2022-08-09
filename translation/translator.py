#!/bin/python3
from codeManager import CodeManager
import gate


if __name__ == '__main__':
    CodeManager.translateCode((gate.CPUP, {'b': 32, 'reg': 5, 'ram': 16}), 'r')
    CodeManager.saveCode('translation.hpp')
