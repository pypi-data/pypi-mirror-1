#!/bin/env/python
# -*- coding: utf-8 -*-

"An paragraph with a versal first letter in the first line."


from reportlab.pdfbase.pdfmetrics import stringWidth

from simpleparagraph import SimpleParagraph


class VersalParagraph(SimpleParagraph):
    """A SimpleParagraph subclass with a versal letter.
    """

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
        lineNum = 0
        wordNum = 0 # index in line
        fn, fs = self.style.fontName, self.style.fontSize
        leading = self.style.leading 
        if hasattr(self, "versal"):
            sw = stringWidth(self.versal, fn, 2*leading*1.2)
            # print "sw", sw
            vWidth = 1.1 * sw
        else:
            vWidth = 0
        
        while i < len(self.words):
            word = self.words[i]
            width = word["width"]

            # does it fit entirely into current line?
            if x + width <= availWidth - style.rightIndent:
                x, y = self.doPlace(word, x, y)
                if self.containsFirstLine and lineNum == 0 and wordNum == 0:
                    # print ":", lineNum, wordNum, i, word["text"]
                    xw, yw = word["pos"]
                    if not hasattr(self, "versal"):
                        self.versal = word["text"][0]
                        word["text"] = word["text"][1:]
                        word["width"] = stringWidth(word["text"][1:], fn, fs)
                    word["pos"] = (xw + vWidth, yw)
                    x += vWidth
                    wordNum += 1
            # or does it overlap the end of the current line?
            else:
                # print word
                # break line if not at top
                # if i != 0:
                x, y, i = self.doLineBreak(x, y, i)
                x, y = self.doPlace(word, x, y)
                lineNum += 1
                wordNum = 0
                if self.containsFirstLine and lineNum < 2 and wordNum == 0:
                    xw, yw = word["pos"]
                    word["pos"] = (xw + vWidth, yw)
                    x += vWidth
                
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


    def visitFirstParagraph(self, para):
        para.versal = self.versal
        return para


    def draw(self):
        "Render the content of the paragraph."

        SimpleParagraph.draw(self)
    
        if not self.containsFirstLine:
            return
            
        canvas = self.canv
        style = self.style

        canvas.saveState()

        text = self.versal
        (x, y) = self.words[0]["pos"]
        x = style.leftIndent
        y -= (style.leading)
        canvas.setFont(style.fontName, 2*style.leading*1.2)
        canvas.setFillColor(style.textColor)
        canvas.drawString(x, y - self.dy, text)

        canvas.restoreState()
