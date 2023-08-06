#!/bin/env/python
# -*- coding: utf-8 -*-

"An example for a hyphenated paragraph subclass."


import re, sys, pyHnj
from pprint import pprint

from reportlab.pdfbase.pdfmetrics import stringWidth

try:
    from wordaxe.DCWHyphenator import DCWHyphenator
    from wordaxe.PyHnjHyphenator import PyHnjHyphenator
    HAVE_WORDAXE = True
except ImportError:
    HAVE_WORDAXE = False
    
from minimalparagraph import MinimalParagraph


# Try using wordaxe, a hyphenation package byHenning von Bargen, 
# see http://deco-cow.sourceforge.net 
# but for English text it could also just use pyHnj...

if HAVE_WORDAXE:
    # dictPath = os.path.join(os.path.dirname(__file__), "dict", "hyph_de_DE.dic")
    # H = HYPHENATOR = pyHnj.Hyphen(dictPath)
    # H = DCWHyphenator("DE", 2)
    # H = pyHnj.Hyphen()
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
else:
    H = pyHnj.Hyphen()

    def hyphenate(unicodeWord):
        "Return list of hyphenation components."
        
        parts = unicodeWord.split("-")
        return parts
    

class HyphenatedParagraph(MinimalParagraph):
    "A hyphenated subclass of MinimalParagraph."

    def doHyphenate(self, word):
        "Return word fragment list if hyphenatable or the word itself if not."

        return hyphenate(word)
        
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
                        # pre = {"text":fragsSums[-1][0]}
                        pre = word.copy()
                        pre["text"] = fragsSums[-1][0]
                        try:
                            pre["width"] = stringWidth(pre["text"], styfn, styfs)
                        except:
                            raise
                            pre["width"] = stringWidth(pre["text"].decode("latin1"), styfn, styfs)
                        # post = {"text":"".join(hyphenated)[len(pre["text"])-1:]}
                        post = word.copy()
                        post["text"] = "".join(hyphenated)[len(pre["text"])-1:]
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
