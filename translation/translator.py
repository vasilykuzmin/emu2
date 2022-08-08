#!/bin/python3
from codeManager import CodeManager
import gate


if __name__ == '__main__':
    CodeManager.translateCode((gate.DEMUXP, {'s': 2, 'b': 2}))
    CodeManager.saveCode('translation.hpp')
