#!/bin/env/python
# -*- coding: utf-8 -*-

"""Test RL paragraph and alterparagraphs side by side.
"""

import sys
import unittest
from os.path import splitext, join, basename, dirname

from reportlab.lib import colors 
from reportlab.lib.units import cm 
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet 
from reportlab.lib.styles import ParagraphStyle, StyleSheet1 
from reportlab.pdfgen.canvas import Canvas 
from reportlab.platypus import Paragraph

sys.path.insert(0, "../src/alterparagraphs")

from minimalparagraph import MinimalParagraph
from simpleparagraph import SimpleParagraph
from bulletparagraph import BulletParagraph
from marginalparagraph import MarginalParagraph
from countingparagraph import CountingParagraph
from versalparagraph import VersalParagraph


SAMPLE_TEXT_1 = "If you need something that isn't on the feature list, please check the mailing-list archives. Lots of features are yet to be documented, but most of the functionality has been commented in the mailing-list. If you have a problem that has not been dealt with yet."


def addParagraph(title, canv, text, style, Para, frame1, frame2, **kwDict):    
    canv.saveState()

    x0, y0, aW, aH = frame1
    xli = style.__dict__.get("leftIndent", 0)
    xri = style.__dict__.get("rightIndent", 0)

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
        canv.rect(x0+xli, y0+aH-h, w-xli-xri, h, stroke=True, fill=False)
        p1.drawOn(canv, x0, y0+aH-h) 

        x0, y0, aW, aH = frame2
        canv.saveState()
        canv.setLineWidth(2)
        canv.setStrokeColor(colors.blue)
        canv.rect(x0, y0, aW, aH)
        canv.restoreState()
        
        w, h = p2.wrap(aW, aH)    # find needed space 
        canv.rect(x0, y0+aH-h, w, h, stroke=True, fill=True)
        canv.rect(x0+xli, y0+aH-h, w-xli-xri, h, stroke=True, fill=False)
        p2.drawOn(canv, x0, y0+aH-h) 

    canv.restoreState()


class CompareParaTestCase(unittest.TestCase):
    "Test paragraph comparison (eyeball-test)."

    def setUp(self):
        styleSheet = getSampleStyleSheet() 
        style = styleSheet['BodyText']
        style.fontName = "Times-Bold" 
        style.fontSize = 18 
        style.leading = 25
        style.alignment = TA_CENTER
        # style.textColor = colors.red
        self.style = style
        
        self.output = "output"
        

    def test0(self):
        "Test MinimalParagraph."

        text = SAMPLE_TEXT_1
        path = join(self.output, "test_para_sidebyside_test0.pdf")
        canv = Canvas(path)
    
        fw, fh = (250, 205)
        f1 = (30, 500, fw, fh)
        f2 = (30, 200, fw, fh)
        title = "ReportLab Paragraph"
        addParagraph(title, canv, text, self.style, Paragraph, f1, f2)   
        
        f1 = (320, 500, fw, fh)
        f2 = (320, 200, fw, fh)
        title = "MinimalParagraph"
        addParagraph(title, canv, text, self.style, MinimalParagraph, f1, f2)   
    
        canv.save() 
    
    
    def test1(self):
        "Test SimpleParagraph."

        text = SAMPLE_TEXT_1
        path = join(self.output, "test_para_sidebyside_test1.pdf")
        canv = Canvas(path)
    
        fw, fh = (250, 205)
        f1 = (30, 500, fw, fh)
        f2 = (30, 200, fw, fh)
        title = "ReportLab Paragraph"
        addParagraph(title, canv, text, self.style, Paragraph, f1, f2)   
        
        f1 = (320, 500, fw, fh)
        f2 = (320, 200, fw, fh)
        title = "SimpleParagraph"
        addParagraph(title, canv, text, self.style, SimpleParagraph, f1, f2)   
    
        canv.save() 
    
    
    def test2(self):
        "Test BulletParagraph."

        text = SAMPLE_TEXT_1
        path = join(self.output, "test_para_sidebyside_test2.pdf")
        canv = Canvas(path)
    
        style = self.style
        style.alignment = TA_LEFT        
        style.leftIndent = 1*cm
        style.rightIndent = 1*cm
        style.firstLineIndent = 1*cm
        style.bulletFontName = "Helvetica-Bold"
        style.bulletFontSize = 18
        style.bulletIndent = 0.5*cm
        style.bulletOffsetY = -0.5*cm
        style.bulletColor = colors.red
    
        bullet = unichr(50).encode('utf8')
        
        fw, fh = (250, 205)
        f1 = (30, 500, fw, fh)
        f2 = (30, 200, fw, fh)
        title = "ReportLab Paragraph"
        addParagraph(title, canv, text, style, Paragraph, 
            f1, f2, bulletText=bullet)
        
        f1 = (320, 500, fw, fh)
        f2 = (320, 200, fw, fh)
        title = "BulletParagraph"
        addParagraph(title, canv, text, style, BulletParagraph, 
            f1, f2, bulletText=bullet)   
    
        canv.save() 
    

    def test3(self):
        "Test MarginalParagraph."

        text = SAMPLE_TEXT_1
        path = join(self.output, "test_para_sidebyside_test3.pdf")
        canv = Canvas(path)
    
        style = self.style
        style.leftIndent = 0.5*cm
        style.rightIndent = 0.5*cm
        style.alignment = TA_LEFT        
    
        styleSheet2 = StyleSheet1()
        add = lambda **kwdict:styleSheet2.add(ParagraphStyle(**kwdict))
        add(name = "Marginal",
            fontName = "Times-Roman",
            fontSize = 12,
            leading = 15,
            alignment = TA_LEFT,
        )
        mstyle = styleSheet2["Marginal"]
        mtext = "Some maybe not so short marginal text... "*2
        mp = Paragraph(mtext, mstyle)
        
        fw, fh = (250, 205)
        f1 = (320, 500, fw, fh)
        f2 = (320, 200, fw, fh)
        title = "MarginalParagraph"
        addParagraph(title, canv, text, style, MarginalParagraph, 
            f1, f2, marginalText=mp, marginalWidth=3*cm)   
    
        canv.save() 


    def test4(self):
        "Test widows/orphans wih MinimalParagraph."

        text = "Orphans have a future and no past while widows have a past and no future. " * 3
        path = join(self.output, "test_para_sidebyside_test4.pdf")
        canv = Canvas(path)

        style = self.style
        style.leftIndent = 0.5*cm
        style.rightIndent = 0.5*cm
        style.alignment = TA_LEFT        

        fw, fh = (250, 205)
        f1 = (30, 500, fw, fh)
        f2 = (30, 200, fw, fh)
        title = "ReportLab Paragraph"
        addParagraph(title, canv, text, style, Paragraph, f1, f2)   
        
        f1 = (320, 500, fw, fh)
        f2 = (320, 200, fw, fh)
        title = "MinimalParagraph"
        addParagraph(title, canv, text, style, MinimalParagraph, f1, f2)   
    
        canv.save() 
    

    def test5(self):
        "Test wih CountingParagraph."

        text = SAMPLE_TEXT_1
        path = join(self.output, "test_para_sidebyside_test5.pdf")
        canv = Canvas(path)

        style = self.style
        style.leftIndent = 0.5*cm
        style.rightIndent = 0.5*cm
        style.alignment = TA_LEFT        

        fw, fh = (250, 205)
        f1 = (30, 500, fw, fh)
        f2 = (30, 200, fw, fh)
        title = "ReportLab Paragraph"
        addParagraph(title, canv, text, style, Paragraph, f1, f2)   
        
        f1 = (320, 500, fw, fh)
        f2 = (320, 200, fw, fh)
        title = "CountingParagraph"
        addParagraph(title, canv, text, style, CountingParagraph, f1, f2, debug=False)   
    
        canv.save() 
    

    def test6(self):
        "Test wih VersalParagraph."

        text = "A para shows the first letter of the first word in a bigger size capital then the rest of the paragraph. "
        path = join(self.output, "test_para_sidebyside_test6.pdf")
        canv = Canvas(path)

        style = self.style
        # style.leftIndent = 0.5*cm
        # style.rightIndent = 0.5*cm
        style.fontSize = 40
        style.leading = 48
        style.alignment = TA_LEFT        

        fw, fh = (250, 205)
        f1 = (30, 500, fw, fh)
        f2 = (30, 200, fw, fh)
        title = "ReportLab Paragraph"
        addParagraph(title, canv, text, style, Paragraph, f1, f2)   
        
        f1 = (320, 500, fw, fh)
        f2 = (320, 200, fw, fh)
        title = "VersalParagraph"
        addParagraph(title, canv, text, style, VersalParagraph, f1, f2, debug=False)   
    
        canv.save() 
    

if __name__ == "__main__":
    unittest.main()
