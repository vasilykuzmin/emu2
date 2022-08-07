#!/bin/python3
from codeManager import CodeManager
import gate


if __name__ == '__main__':
    CodeManager.translateCode((gate.AND, {'b': 6}))
    CodeManager.saveCode('translation.hpp')
