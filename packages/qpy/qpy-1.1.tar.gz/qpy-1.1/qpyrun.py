#!/usr/bin/env python
import sys
from qpy.compile import compile
if __name__ == '__main__':
    exec compile(sys.argv[1])

