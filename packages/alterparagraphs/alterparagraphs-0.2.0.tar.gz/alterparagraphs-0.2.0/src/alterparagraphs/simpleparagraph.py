#!/bin/env/python
# -*- coding: utf-8 -*-

"A simple paragraph class to be used with ReportLab Platypus."

import re

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.flowables import Flowable


class SimpleParagraph(Flowable):
    """A simple Paragraph class respecting alignment.

    Does text without tags.
    
    Respects only the following global style attributes: 
    fontName, fontSize, leading, firstLineIndent, leftIndent, 
    rightIndent, textColor, alignment.
    (spaceBefore, spaceAfter are handled by the Platypus framework.)

    text = "foo and bar"
    
    after parsed():
    words = [
        {"text":"foo", "width":...},
        {"text":"and", "width":...},
        {"text":"bar", "width":...},
    ]

    after wrap():
    words = [
        {"text":"foo", "width":..., "pos":(x, y)},
        {"text":"and", "width":..., "pos":(x, y)},
        {"text":"", "meta":"newline"},
        {"text":"bar", "width":..., "pos":(x, y)},
    ]
    """
    
    def __init__(self, text, style, words=None, containsFirstLine=True, 
            debug=False, **kwDict):
        
        Flowable.__init__(self)
        
        self.text = text
        self.style = style

        self.words = words
        self.containsFirstLine = containsFirstLine
        self.debug = debug
        for k, v in kwDict.items():
            setattr(self, k, v)
        
        # set later...
        self.dy = None
        self.words = None # important!
        self.splitted = None
        self.splitIndex = None


    def parse(self, text):
        "Parse text and build a word list with string widths out of it."

        if self.debug:
            print "*** parse", text
            
        fn, fs = self.style.fontName, self.style.fontSize
        self.words = [{"text":w, "width":stringWidth(w, fn, fs)} 
            for w in self.doSplitIntoWords(text)]


    def doSplitIntoWords(self, text):
        "Return text split into words."

        # vanilla version
        # return text.split()

        # split at white space, if not preceeded by backslash
        words = re.split(r"(?<!\\)\s", text)
        words = [w.replace(r"\ ", " ") for w in words]
        return words
        

    def _NOT_NEEDED_getPreviousLine(self):
        "Get elements on previous line."

        words = self.words
        i = -1
        while True:
            try:
                p = words[i]
                # if "meta" in p and p["meta"] == "newline":
                if p.get("meta", None) == "newline":
                    break
            except IndexError:
                break
            i = i - 1

        return self.words[i+1:]


    def doAlign(self, isLast=False):
        "Align words in previous line."

        alignment = self.style.alignment
        if alignment != TA_LEFT:
            words = self.words
            i = -1
            while True:
                try:
                    p = words[i]
                    # if "meta" in p and p["meta"] == "newline":
                    if p.get("meta", None) == "newline":
                        break
                except IndexError:
                    break
                i = i - 1
            prevLine = words[i+1:]
            minX = min([w["pos"][0] for w in prevLine if "pos" in w])
            maxX = max([w["pos"][0]+w["width"] for w in prevLine if "pos" in w])
            lineWidth = maxX - minX
            emptySpace = self.avWidth - lineWidth
            for j, elem in enumerate(prevLine):
                if not "pos" in elem:
                    continue
                text, width, (x, y) = elem["text"], elem["width"], elem["pos"]
                if alignment == TA_RIGHT:
                    elem["pos"] = (x + emptySpace, y)
                elif alignment == TA_CENTER:
                    elem["pos"] = (x + emptySpace / 2.0, y)
                elif alignment == TA_JUSTIFY: 
                    # and not isLast and not self.isLast:
                    delta = emptySpace / (len(words[i+1:]) - 1)
                    elem["pos"] = (x + j * delta, y)


    def doLineBreak(self, x, y, i):
        "Break current line, return 'cursor' position at start of next line."

        self.doAlign()
        self.words.insert(i, {"text":"", "width":0, "meta":"newline"})
        x, y = self.style.leftIndent, y - self.style.leading

        return x, y, i+1


    def doPlace(self, word, x, y):
        "Add position of word to word entry, return pos. after this word."

        style = self.style
        word["pos"] = (x, y + style.leading - style.fontSize)

        return x + word["width"], y


    # overwritten methods from Flowable class
    
    def wrap(self, availWidth, availHeight):
        "Determine the rectangle this paragraph really needs."

        # memorize available space
        self.avWidth = availWidth
        self.avHeight = availHeight

        if self.words == None:
            self.parse(self.text)

        if self.debug:
            print "*** wrap (%f, %f)" % (availWidth, availHeight)

        if not self.words:
            if self.debug:
                print "*** wrap (%f, %f) needed" % (0, 0)
            return 0, 0

        style = self.style
        blankWidth = stringWidth(" ", style.fontName, style.fontSize)

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
            # does it overlap the end of the current line?
            else:
                # print "wrapped:", word
                # break line if not at top
                # if i != 0:
                x, y, i = self.doLineBreak(x, y, i)
                x, y = self.doPlace(word, x, y)
                
            # add space to current line if it fits there
            if x + blankWidth <= availWidth:
                x += blankWidth

            # if we need too much height, memorize index and break
            if y < y0 - availHeight:
                self.words.insert(i, {"text":"", "width":0, "meta":"endpara"})
                self.splitIndex = i
                break
            
            i += 1

        self.doAlign(isLast=True)

        neededWidth, neededHeight = availWidth, y0 - y
        self.dy = y
        if self.debug:
            print "*** wrap (%f, %f) needed" % (neededWidth, neededHeight)
        
        return neededWidth, neededHeight


    def visitFirstParagraph(self, para):
        return para
        

    def visitOtherParagraph(self, para):
        return para
        

    def split(self, availWidth, availHeight):
        "Split ourself in two paragraphs."
        
        if self.debug:
            print "*** split (%f, %f)" % (availWidth, availHeight)

        if self.splitIndex:
            si = self.splitIndex
            if self.debug:
                print '*** splitIndex %d' % si
            t1 = " ".join([w["text"] for w in self.words[:si] if w["text"]])
            t2 = " ".join([w["text"] for w in self.words[si:] if w["text"]])
            if self.debug:
                print "t1", t1
                print "t2", t2
                
            paraClass = self.__class__
            para1 = paraClass(t1, self.style, words=self.words[:si], 
                containsFirstLine=self.containsFirstLine)
            para1 = self.visitFirstParagraph(para1)
            # the following gets no 'words' arg on purpose
            para2 = paraClass(t2, self.style, containsFirstLine=False)
            para2 = self.visitOtherParagraph(para2)
            self.splitted = [para1, para2]
        else:
            # don't split
            self.splitted = []

        if self.debug:
            print '*** return %s' % self.splitted

        return self.splitted


    def draw(self):
        "Render the content of the paragraph."

        if self.debug:
            print "*** draw"

        if not self.words:
            return
            
        canvas = self.canv
        style = self.style

        canvas.saveState()

        canvas.setFont(style.fontName, style.fontSize)
        canvas.setFillColor(style.textColor)

        for word in self.words:
            if "meta" in word or not "pos" in word:
                continue
            text, (x, y) = word["text"], word["pos"]
            canvas.drawString(x, y - self.dy, text)

        canvas.restoreState()