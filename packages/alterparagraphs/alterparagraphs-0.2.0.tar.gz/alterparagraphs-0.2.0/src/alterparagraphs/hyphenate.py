#!/bin/env/python
# -*- coding: utf-8 -*-

"Utils for hyphenating a word."

import re, sys, getopt

from wordaxe.DCWHyphenator import DCWHyphenator
from wordaxe.PyHnjHyphenator import PyHnjHyphenator


import pyHnj
# HYPHENATOR = pyHnj.Hyphen("dict/hyphen.mashed")
HYPHENATOR = pyHnj.Hyphen("dict/hyph_de_DE.dic")
H = DCWHyphenator("DE", 2)


def hyphenate(unicodeWord):
    "Return list of hyphenation components."
    
    points = H.hyphenate(unicodeWord).hyphenations
    idxs = [p.indx for p in points]
    slices = [(idxs[i], idxs[i+1]) for i, el in enumerate(idxs[:-1])]
    if slices:
        slices = [(0, idxs[0])] + slices + [(idxs[-1], None)]
    parts = [unicodeWord[slice(*s)] for s in slices]
    
    return parts
    

def doHyphenate(self, word):
    "Return word fragment list if hyphenatable or the word itself if not."

    # uncomment this to disable hyphenation
    # print "###", word, type(word)
    return hyphenate(word)
    
    # uncomment this to disable hyphenation
    # return word

    # punctuationPat = "[\.\!\?\(\)\[\]\{\}\:\;]"
    # components = re.split(punctuationPat, word)
    # if "" in components:
    #     pass
        
    knownWordList = {
        "Restaurant,": ["Re", "stau", "rant,"],
        # "Gelegenheiten.": ["Ge", "le", "gen", "hei", "ten."],
        # "Mobiltelefon": ["Mo", "bil", "te", "le", "fon"],
        # "verbieten?": ["ver", "bie", "ten?"],
    }
    
    try:
        hw = HYPHENATOR.hyphenate(word)
    except:
        # print "???", word, type(word), word.encode("latin1")
        hw = HYPHENATOR.hyphenate(word.encode("latin1"))
        print word.encode("latin1"), ">>>", hw, type(hw)
        hw = hw.decode("latin1").encode("utf8")
        # sys.exit()
    # hw = unicode(HYPHENATOR.hyphenate(word).decode("utf8"))
    
    # isURL = lambda u: re.search("(http|ftp)\://", u)
    # if len(word.split("-")) > 1:
    #     return word.split("-")
    # ... urlparse.urlsplit(...)
    if 0:
        if re.search("(http|ftp)\://", word):
                return word.split("-")
        elif word in knownWordList.keys():
            res = knownWordList[word]
    
    if "-" in hw:
        return hw.split("-")
    else:
        res = word

    return res
