#!/bin/env/python
# -*- coding: utf-8 -*-

"An minimalist paragraph class to be used with ReportLab Platypus."

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from minimalparagraph import MinimalParagraph


TTFSources = [
    ("Myriad", "/Data/Fonts/truetype/myriad.ttf"),
    # ("MyriadBold", "/Data/Fonts/truetype/myriadb.ttf"),
    # ("MyriadItalic", "/Data/Fonts/truetype/myriadi.ttf"),
]

for name, path in TTFSources:
    font = TTFont(name, path)
    if not name in pdfmetrics._fonts:
        pdfmetrics.registerFont(font)


class TTFParagraph(MinimalParagraph):
    """A minimal Paragraph class using a fixed TrueType font.
    """

    def __init__(self, text, style, **kwDict):
        MinimalParagraph.__init__(self, text, style, **kwDict)
        
        self.style.fontName = "Myriad"
