#!/bin/env/python
# -*- coding: utf-8 -*-

"An example for a coloured paragraph subclass."

import random, re

from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

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


class HighlightedParagraph(MinimalParagraph):
    "A colourful tiny subclass of MinimalParagraph."

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