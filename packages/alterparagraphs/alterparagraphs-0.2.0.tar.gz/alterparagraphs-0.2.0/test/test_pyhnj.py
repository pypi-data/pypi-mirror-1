#!/bin/env/python
# -*- coding: utf-8 -*-

import pyHnj
import unittest


class PyHnjTestCase(unittest.TestCase):
    "Test hyphenation in Python standard library."

    def setUp(self):
        self.output = "output"


    def test0(self):
        "Test hyphenation."

        # h = pyHnj.Hyphen("../alterparagraphs/dict/hyphen.mashed")
        h = pyHnj.Hyphen()
        res = h.hyphenate('hyphenation')
        exp = "hy-phen-ation"
        self.assertEqual(res, exp)
        

if __name__ == "__main__":
    unittest.main()
