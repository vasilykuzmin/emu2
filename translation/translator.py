#!/bin/python3
import sys
from codeManager import CodeManager
import gate


if __name__ == '__main__':
    CodeManager.translateCode((gate.CPUP, {'b': int(sys.argv[1]), 'reg': int(sys.argv[2]), 'ram': int(sys.argv[3])}), 'r', sys.argv[4])
    CodeManager.saveCode(sys.argv[5])
