#!/bin/env/python
# -*- coding: utf-8 -*-

"An simple paragraph class with bullets to be used with ReportLab Platypus."


from reportlab.pdfbase.pdfmetrics import stringWidth

from simpleparagraph import SimpleParagraph


class BulletParagraph(SimpleParagraph):
    """A Paragraph class with bullets.

    Does text without tags (including <bullet>).
    
    Uses the following additional global style attributes: 
    bulletFontName, bulletFontSize, bulletIndent, bulletColor, bulletOffsetY.
    An additional attribute is passed in the constructor with
    the name bulletText.
    """

    # overwritten methods from SimpleParagraph class
    
    def visitFirstParagraph(self, para):
        para.bulletText = self.bulletText
        return para
        

    def draw(self):
        "Render the bullet of the paragraph."

        SimpleParagraph.draw(self)

        if not hasattr(self, "bulletText") or not self.bulletText:
            return

        text = self.bulletText
        style = self.style
        fn, fs = style.bulletFontName, style.bulletFontSize
        sw = stringWidth(text, fn, fs)
        offsetY = getattr(style, "bulletOffsetY", 0)
        bulletColor = getattr(style, "bulletColor", style.textColor)
        try:
            x, y = style.bulletIndent, self.words[0]["pos"][1]
        except:
            # find first real word
            for word in self.words:
                if "meta" in word or not "pos" in word:
                    continue
                else:
                    x, y = style.bulletIndent, word["pos"][1]
                    break
        
        canvas = self.canv
        canvas.saveState()
        canvas.setFont(fn, fs)
        canvas.setFillColor(bulletColor)
        canvas.drawString(x, y - self.dy + offsetY, text)
        canvas.restoreState()
