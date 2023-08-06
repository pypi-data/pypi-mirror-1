#!/bin/env/python
# -*- coding: utf-8 -*-

"""Test bullets implemented in ReportLab paragraphs as tags and attributes.

If this fails you might have the wrong RL implementation, 2.1 won't do it.
"""

import sys
import unittest
from os.path import splitext, join, basename, dirname

import reportlab
from reportlab.lib import colors 
from reportlab.lib.units import cm 
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet 
from reportlab.lib.styles import ParagraphStyle, StyleSheet1 
from reportlab.pdfgen.canvas import Canvas 
from reportlab.platypus import Paragraph


def addParagraph(title, canv, text, style, Para, frame1, frame2, **kwDict):    
    canv.saveState()

    x0, y0, aW, aH = frame1

    canv.setFont("Helvetica", 18)
    canv.drawString(x0, y0+aH+30, title)
    
    p = Para(text, style, **kwDict)
    w, h = p.wrap(aW, aH)    # find needed space 
        
    canv.saveState()
    canv.setLineWidth(2)
    canv.setStrokeColor(colors.blue)
    canv.rect(x0, y0, aW, aH)
    canv.restoreState()
    
    canv.setLineWidth(1)
    canv.setStrokeColor(colors.red)
    canv.setFillColor(colors.yellow)
    if w <= aW and h <= aH: 
        canv.rect(x0, y0+aH-h, w, h, stroke=True, fill=True)
        p.drawOn(canv, x0, y0+aH-h) 
    else:
        p1, p2 = p.split(aW, aH)
        w, h = p1.wrap(aW, aH)    # find needed space 
        canv.rect(x0, y0+aH-h, w, h, stroke=True, fill=True)
        p1.drawOn(canv, x0, y0+aH-h) 

        x0, y0, aW, aH = frame2
        canv.saveState()
        canv.setLineWidth(2)
        canv.setStrokeColor(colors.blue)
        canv.rect(x0, y0, aW, aH)
        canv.restoreState()
        w, h = p2.wrap(aW, aH)    # find needed space 
        canv.rect(x0, y0+aH-h, w, h, stroke=True, fill=True)
        p2.drawOn(canv, x0, y0+aH-h) 

    canv.restoreState()


class CompareParaTestCase(unittest.TestCase):
    "Test paragraph comparison (eyeball-test)."

    def test0(self):
        "Test styled vs. tagged RL bullet Paragraphs."

        text = "If you need something that isn't on the feature list, please check the mailing-list archives. Lots of features are yet to be documented, but most of the functionality has been commented in the mailing-list. If you have a problem that has not been dealt with yet."
        path = splitext(sys.argv[0])[0] + "_test0.pdf"
        canv = Canvas(path)
    
        styleSheet = getSampleStyleSheet() 
        style = styleSheet['BodyText']
        style.fontName = "Times-Bold" 
        style.fontSize = 18 
        style.leading = 25
        style.alignment = TA_LEFT
        
        style.bulletFontName = "Helvetica-Bold"
        style.bulletFontSize = 18
        style.leftIndent = 2*cm
        style.rightIndent = 1*cm
        style.firstLineIndent = 1*cm
        style.bulletIndent = 0.5*cm
        style.bulletOffsetY = -10
        style.bulletColor = colors.red

        fw, fh = (250, 205)
        f1 = (30, 500, fw, fh)
        f2 = (30, 200, fw, fh)
        title = "Styled ReportLab Paragraph"
        addParagraph(title, canv, text, style, Paragraph, f1, f2, bulletText="2")
        
        
        styleSheet2 = StyleSheet1()
        add = lambda **kwdict:styleSheet2.add(ParagraphStyle(**kwdict))
        add(name = 'Normal',
            fontName = 'Times-Bold',
            fontSize = 18,
            leading = 25,
            alignment = TA_LEFT,
        )
        style2 = styleSheet2["Normal"]
    
        f1 = (320, 500, fw, fh)
        f2 = (320, 200, fw, fh)
        title = "Tagged ReportLab Paragraph"
        text = "<para firstLineIndent='1cm' leftIndent='2cm' rightIndent='1cm' bulletIndent='0.5cm' bulletFontName='Helvetica-Bold' bulletFontSize='18' bulletColor='red' bulletoffsety='-10'><bullet>2</bullet>%s</para>" % text
        addParagraph(title, canv, text, style2, Paragraph, f1, f2)   
    
        canv.save() 
    

if __name__ == "__main__":
    unittest.main()
