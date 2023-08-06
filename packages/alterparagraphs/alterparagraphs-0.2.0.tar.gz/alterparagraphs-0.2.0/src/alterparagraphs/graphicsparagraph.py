#!/bin/env/python
# -*- coding: utf-8 -*-

"An minimalist paragraph class to be used with ReportLab Platypus."

import re

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.widgets import signsandsymbols

from minimalparagraph import MinimalParagraph


U = " widget:///reportlab.graphics.widgets.signsandsymbols "

def addSmilie(matchObj):
    "Add a smilie URL after a regex match object."
    
    res = "%s %s" % (matchObj.group(0), U)
    
    return res
    
    
def addSmil(text):
    if text.startswith("widget://"):
        return ""
    else: 
        vowels = len(set(re.findall("a|e|i|o|u", text.lower())))
        if vowels == 4:
            return "%s %s" % (text, U)
    
    return text
    
    
class GraphicsParagraph(MinimalParagraph):
    "A minimal Paragraph class with inline images."

    def parse(self, text):
        "Parse text and build a word list with string widths out of it."

        # (?<!file://)
        # text = re.sub("(?!\s%s\s)(\w*o\w*)" % U, addSmilie, text)
        text = " ".join([addSmil(t) for t in text.split()])
        # print "***", text

        MinimalParagraph.parse(self, text)

        imgIndices = [i for (i, path) in enumerate(self.doSplitIntoWords(text))
            if path.startswith("widget://")]
        for i in imgIndices:
            w = self.words[i]
            w["type"] = "graphics"
            w["height"] = self.style.fontSize
            w["width"] = self.style.fontSize


    # overwritten methods from Flowable class

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
            if "meta" in word:
                continue
            # print word
            try:
                text, (x, y) = word["text"], word["pos"]
            except KeyError:
                raise
            if "type" in word and word["type"] == "graphics":
                # print "*** graphics", word["text"][len("widget:///"):]
                symbol = __import__(word["text"][len("widget:///"):])
                from reportlab.graphics.widgets.signsandsymbols import SmileyFace
                d = Drawing(10, 10)
                symbol = SmileyFace()
                symbol.x = 0
                symbol.y = 0
                symbol.size = style.fontSize
                d.add(symbol)
                d.drawOn(canvas, x, y - self.dy)
            else:
                canvas.drawString(x, y - self.dy, text)

        canvas.restoreState()
        
    