#!/bin/env/python
# -*- coding: utf-8 -*-

"An simple paragraph class with marginal text to be used with ReportLab Platypus."


from reportlab.lib.units import cm 
from reportlab.pdfbase.pdfmetrics import stringWidth

from simpleparagraph import SimpleParagraph


class MarginalParagraph(SimpleParagraph):
    """A Paragraph class with marginal text.

    Does text without tags.
    """

    def __init__(self, text, style, **kwDict):
        SimpleParagraph.__init__(self, text, style, **kwDict)
        if not hasattr(self, "marginalWidth"):
            self.marginalWidth = 3*cm


    # overwritten methods from SimpleParagraph class
    
    def wrap(self, availWidth, availHeight):
        "Determine the area this paragraph really needs."

        w, h = SimpleParagraph.wrap(self, availWidth, availHeight)

        if getattr(self, "marginalText", None) \
            and getattr(self, "marginalWidth", None):
            aW, aH = self.marginalWidth, self.avHeight
            wm, hm = self.marginalText.wrap(aW, aH)
            
        return w, h


    def visitFirstParagraph(self, para):
        if getattr(self, "marginalText", None):
            para.marginalText = self.marginalText
        para.marginalWidth = self.marginalWidth
        return para
        

    def visitOtherParagraph(self, para):
        return para
        

    def draw(self):
        "Render the marginal text paragraph."

        SimpleParagraph.draw(self)

        if not getattr(self, "marginalText", None):
            return

        canvas = self.canv
        mtext = self.marginalText
        aW = self.marginalWidth
        w, h = mtext.wrap(aW, self.avHeight)
        canvas.rect(-aW, -self.dy, aW, self.avHeight)
        mtext.drawOn(canvas, -aW, -self.dy + self.avHeight - h) 
