#!/bin/env/python
# -*- coding: utf-8 -*-

"An minimalist paragraph class to be used with ReportLab Platypus."

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.flowables import Flowable

# import psyco

class MinimalParagraph(Flowable): # , psyco.compact):
    """A minimal Paragraph class.

    Does only left-justified text without tags.
    
    Uses only the following global style attributes: 
      fontName, fontSize, leading, textColor, 
      firstLineIndent, leftIndent, rightIndent.
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

    def __init__(self, text, style, **kwDict):
        Flowable.__init__(self)
        
        self.text = text
        self.style = style

        # handle named arguments        
        self.words = kwDict.get("words", None) # previously parsed text
        self.containsFirstLine = kwDict.get("containsFirstLine", False)
        self.debug = kwDict.get("debug", False)

        # set later...
        self.dy = None
        self.words = None
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
        return text.split()


    def doLineBreak(self, x, y):
        "Break current line, return 'cursor' position at start of next line."

        x, y = self.style.leftIndent, y - self.style.leading

        return x, y


    def doPlace(self, word, x, y):
        "Add position of word to word entry, return pos. after this word."

        style = self.style
        word["pos"] = (x, y + style.leading - style.fontSize)

        return x + word["width"], y


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
            # or does it overlap the end of the current line?
            else:
                # break line if not at top
                # if i != 0:
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
            para2 = paraClass(t2, self.style, containsFirstLine=False)
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