#!/bin/env/python
# -*- coding: utf-8 -*-

"An paragraph class to be used with ReportLab Platypus."

import re, os

import Image as PILImage
from reportlab.platypus import Image as RLImage
from reportlab.pdfbase.pdfmetrics import stringWidth

from minimalparagraph import MinimalParagraph


# U = " file:///Users/dinu/Developer/Python/myparagraph/experimenting/icons/kiss.jpg "
U = " file://icons/kiss.jpg "

def addSmilie(matchObj):
    "Add a smilie URL after a regex match object."
    
    res = "%s %s" % (matchObj.group(0), U)
    
    return res
    
    
def addSmil(text):
    if text.startswith("file://"):
        return ""
    else: 
        vowels = len(set(re.findall("a|e|i|o|u", text.lower())))
        if vowels == 4:
            return "%s %s" % (text, U)
    
    return text
    
    
class IconizedParagraph(MinimalParagraph):
    "A minimal Paragraph class with inline images."
    # rescales images vertically to fit into current line.

    def parse(self, text):
        "Parse text and build a word list with string widths out of it."

        # (?<!file://)
        # text = re.sub("(?!\s%s\s)(\w*o\w*)" % U, addSmilie, text)
        text = " ".join([addSmil(t) for t in text.split()])
        # print "***", text

        MinimalParagraph.parse(self, text)

        imgIndices = [i for (i, path) in enumerate(self.doSplitIntoWords(text))
            if path.startswith("file://")]
        for i in imgIndices:
            w = self.words[i]
            path = w["text"][7:]
            if not os.path.isabs(path):
                path = os.path.join(os.getcwd(), path)
            img = PILImage.open(path)
            w["type"] = "image"
            w["height"] = img.size[1]
            w["width"] = img.size[0]
            w["height"] = self.style.fontSize
            w["width"] = w["width"]/w["height"]*self.style.fontSize


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
            try:
                text, (x, y) = word["text"], word["pos"]
            except KeyError:
                raise
            if "type" in word and word["type"] == "image":
                # print "*** image", word["text"][7:]
                height = word["height"]
                width = word["width"]                
                # img = RLImage(word["text"][7:])
                img = PILImage.open(word["text"][7:])
                img = img.resize((width, height), PILImage.BILINEAR)
                try:
                    canvas.drawImage(img, x, y - self.dy, 
                        width=width, height=height)
                except AttributeError:
                    canvas.drawInlineImage(img, x, y - self.dy, 
                        width=width, height=height)
            else:
                canvas.drawString(x, y - self.dy, text)

        canvas.restoreState()
        
    