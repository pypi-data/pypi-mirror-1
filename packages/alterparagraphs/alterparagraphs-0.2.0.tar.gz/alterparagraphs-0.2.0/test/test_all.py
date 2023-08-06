#!/bin/env/python
# -*- coding: utf-8 -*-

"Run all available test cases in this directory."


import unittest
from glob import glob
from os.path import splitext


def main():
    "Run all available test cases from test modules in this directory."

    # get modules names    
    pyFiles = glob("*.py")
    modNames = [splitext(fn)[0] for fn in pyFiles if fn != __file__]

    # import modules and build test suite
    loader = unittest.TestLoader()    
    for mn in modNames:
        mod = None
        try:
            mod = __import__(mn)
        except:
            pass
        if mod:
            suite = loader.loadTestsFromModule(mod)
            unittest.TextTestRunner().run(suite)
    

if __name__ == "__main__":
    main()
