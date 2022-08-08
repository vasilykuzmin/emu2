#!/bin/python3
from codeManager import CodeManager
import gate


if __name__ == '__main__':
    CodeManager.translateCode((gate.MUXP, {'s': 1, 'b': 1}))
    CodeManager.saveCode('translation.hpp')
