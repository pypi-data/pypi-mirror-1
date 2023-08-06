#!/bin/env/python
# -*- coding: utf-8 -*-

"An example for a hyphenated paragraph subclass."

import re, sys
import random, re
from pprint import pprint
from os.path import join, dirname

from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

from wordaxe.DCWHyphenator import DCWHyphenator
from wordaxe.PyHnjHyphenator import PyHnjHyphenator

from minimalparagraph import MinimalParagraph

# Colour from stabilo.com
YELLOW = colors.Color(253/255., 253/255., 23/255.)
BLUE = colors.Color(63/255., 230/255., 255/255.)
GREEN = colors.Color(138/255., 255/255., 86/255.)
RED = colors.Color(255/255., 29/255., 43/255.)
TURQUOISE = colors.Color(0/255., 177/255., 177/255.)
ORANGE = colors.Color(255/255., 179/255., 7/255.)
LAVENDER = colors.Color(177/255., 61/255., 255/255.)
PINK = colors.Color(255/255., 15/255., 255/255.)
LILAC = colors.Color(237/255., 0/255., 237/255.)

import pyHnj
# HYPHENATOR = pyHnj.Hyphen("dict/hyphen.mashed")
# HYPHENATOR = pyHnj.Hyphen("dict/hyph_de_DE.dic")
dictPath = join(dirname(__file__), "dict", "hyph_de_DE.dic")
HYPHENATOR = pyHnj.Hyphen(dictPath)
H = DCWHyphenator("DE", 2)
H = PyHnjHyphenator()


def hyphenate(unicodeWord):
    "Return list of hyphenation components."
    
    points = H.hyphenate(unicodeWord).hyphenations
    idxs = [p.indx for p in points]
    slices = [(idxs[i], idxs[i+1]) for i, el in enumerate(idxs[:-1])]
    if slices:
        slices = [(0, idxs[0])] + slices + [(idxs[-1], None)]
    parts = [unicodeWord[slice(*s)] for s in slices]
    
    return parts
    

class HyphenlightedParagraph(MinimalParagraph):
    "A hyphenated subclass of MinimalParagraph."

    def parse(self, text):
        "Parse text and build a word list with string widths out of it."

        MinimalParagraph.parse(self, text)

        for i, w in enumerate(self.words):
            w = self.words[i]
            vowels = len(set(re.findall("a|e|i|o|u", w["text"].lower())))
            if vowels == 3:
                w["highlight"] = YELLOW
            elif vowels == 4:
                w["highlight"] = GREEN
            elif vowels == 5:
                w["highlight"] = BLUE


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


    # overwritten methods from Flowable class
    
    def wrap(self, availWidth, availHeight):
        "Determine the area this paragraph really needs."

        if self.words == None:
            self.parse(self.text)

        if self.debug:
            print "*** wrap (%f, %f)" % (availWidth, availHeight)
            
        if not self.words:
            if self.debug:
                print "*** wrap (%f, %f) needed" % (0, 0)
            return 0, 0

        style = self.style
        styfn, styfs = style.fontName, style.fontSize
        blankWidth = stringWidth(" ", styfn, styfs)
        dashWidth = stringWidth("-", styfn, styfs)

        x0, y0 = style.leftIndent, availHeight
        if self.containsFirstLine:
            x0 += style.firstLineIndent
        x, y = x0, y0 - style.leading

        self.splitIndex = 0
        i = 0
        while i < len(self.words):
            word = self.words[i]
            width = word["width"]
                            
            # does it fit entirely into current line?
            if x + width <= availWidth - style.rightIndent:
                x, y = self.doPlace(word, x, y)
            # or does it overlap the end of the current line?
            else:
                hyphenated = self.doHyphenate(word["text"])
                if hyphenated == word["text"]:
                    x, y = self.doLineBreak(x, y)
                    x, y = self.doPlace(word, x, y)
                else:
                    # find longest list of fragments fitting 
                    # into current line
                    frags = hyphenated
                    # print "***", word["text"], frags
                    try:
                        frags = [(f, stringWidth(f, styfn, styfs)) for f in frags]
                    except:
                        raise
                        frags = [f.decode("latin1") for f in frags]
                        frags = [(f, stringWidth(f, styfn, styfs)) for f in frags]
                    if self.debug: 
                        print "*** frags", frags
                    fragsSums = []
                    for k, frag in enumerate(frags):
                        fs = "".join([f for (f, sw) in frags[:k+1]])
                        sws = sum([sw for (f, sw) in frags[:k+1]])
                        if k < len(frags) - 1:
                            fs += "-"
                            sws += dashWidth
                        fragsSums.append((fs, sws))
                    if self.debug: 
                        pprint(fragsSums)
                    fragsSums = [fs for fs in fragsSums 
                        if x + fs[1] < availWidth]
                    if self.debug: 
                        pprint(fragsSums)
                    if fragsSums != []:
                        # we have fragments fitting on the current line
                        pre = word.copy()
                        pre["text"] = fragsSums[-1][0]
                        pre["highlight"] = ORANGE
                        try:
                            pre["width"] = stringWidth(pre["text"], styfn, styfs)
                        except:
                            raise
                            pre["width"] = stringWidth(pre["text"].decode("latin1"), styfn, styfs)
                        post = word.copy()
                        post["text"] = "".join(hyphenated)[len(pre["text"])-1:]
                        post["highlight"] = ORANGE
                        try:
                            post["width"] = stringWidth(post["text"], styfn, styfs)
                        except:
                            raise
                            post["width"] = stringWidth(post["text"].decode("latin1"), styfn, styfs)
                        if self.debug: 
                            print "...", pre, post
                        self.words[i] = pre
                        x, y = self.doPlace(pre, x, y)
                        self.words.insert(i+1, post)
                        x, y = self.doPlace(post, x, y)
                    else:
                        x, y = self.doLineBreak(x, y)
                        x, y = self.doPlace(word, x, y)
                
            # add space to current line if it fits there
            if x + blankWidth <= availWidth:
                x += blankWidth

            # if we need too much height, memorize current index and break loop
            if y < y0 - availHeight:
                self.splitIndex = i
                break
            
            i += 1

        neededWidth, neededHeight = availWidth, y0 - y
        self.dy = y
        if self.debug:
            print "*** wrap (%f, %f) needed" % (neededWidth, neededHeight)
        
        return neededWidth, neededHeight


    def draw(self):
        "Render words in paragraph on randomly coloured background."

        if self.debug:
            print "*** draw"

        if not self.words:
            return
            
        canvas = self.canv
        style = self.style

        canvas.saveState()

        canvas.setFont(style.fontName, style.fontSize)

        for word in self.words:
            if "meta" in word or not "pos" in word:
                continue
            text, (x, y) = word["text"], word["pos"]
            if "highlight" in word:
                mx = stringWidth(" ", style.fontName, style.fontSize) / 2.0
                my = style.fontSize * 0.2
                col = word["highlight"]
                canvas.setStrokeColor(col)
                canvas.setFillColor(col)
                canvas.rect(x-mx, y - self.dy-my, word["width"]+2*mx, style.fontSize,
                    fill=True, stroke=True)
            canvas.setFillColor(style.textColor)
            canvas.drawString(x, y - self.dy, text)

        canvas.restoreState()