#!/bin/python3
from codeManager import CodeManager
import gate


if __name__ == '__main__':
    CodeManager.translateCode((gate.ALU, {'b': 32}), 'm')
    CodeManager.saveCode('translation.hpp')
