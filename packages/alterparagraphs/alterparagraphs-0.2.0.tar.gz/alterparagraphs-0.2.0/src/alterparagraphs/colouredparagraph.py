#!/bin/env/python
# -*- coding: utf-8 -*-

"An example for a coloured paragraph subclass."

import random

from reportlab.lib import colors

from minimalparagraph import MinimalParagraph


RL_COLORS = [v for (k, v) in colors.__dict__.items() 
    if isinstance(v, colors.Color)]


class ColouredParagraph(MinimalParagraph):
    "A colourful tiny subclass of MinimalParagraph."

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
            col = random.choice(RL_COLORS)
            canvas.setStrokeColor(col)
            canvas.setFillColor(col)
            canvas.rect(x, y - self.dy, word["width"], style.fontSize,
                fill=True, stroke=True)
            canvas.setFillColor(style.textColor)
            canvas.drawString(x, y - self.dy, text)

        canvas.restoreState()