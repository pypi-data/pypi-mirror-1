#!/bin/env/python
# -*- coding: utf-8 -*-

"An paragraph with a line counter left to the paragraph lines."


from reportlab.pdfbase.pdfmetrics import stringWidth

from simpleparagraph import SimpleParagraph


class CountingParagraph(SimpleParagraph):
    """A SimpleParagraph subclass with a simple line counter.
    """
    
    def draw(self):
        "Render the content of the paragraph."

        if self.debug:
            print "*** draw"

        if not self.words:
            return
            
        canvas = self.canv
        style = self.style
        fn, fs = style.fontName, style.fontSize

        canvas.saveState()

        canvas.setFont(fn, fs)
        canvas.setFillColor(style.textColor)

        lineNum = 0
        lineNumChanged = True
        for word in self.words:
            if "pos" in word:
                text, (x, y) = word["text"], word["pos"]
                canvas.drawString(x, y - self.dy, text)
            if lineNumChanged:
                ln = str(lineNum)
                sw = stringWidth(ln + " ", fn, fs)
                canvas.drawString(0-sw, y - self.dy, ln)
                lineNumChanged = False
            if word.get("meta", "") == "newline":
                lineNumChanged = True
                lineNum += 1

        canvas.restoreState()
