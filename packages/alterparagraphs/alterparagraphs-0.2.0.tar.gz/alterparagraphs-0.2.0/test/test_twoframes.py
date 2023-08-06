#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""Run performance tests on alterparagraphs.


"""

import os
import sys
from os.path import splitext, join, basename
import unittest

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Frame, Paragraph
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate

sys.path.insert(0, "../src/alterparagraphs")

from simpleparagraph import SimpleParagraph


class MyDocTemplate(BaseDocTemplate):
    "Simple two-frame document template."
    
    def __init__(self, filename, **kw):
        frame1 = Frame(100, 700, 240, 50, id='F1', 
            leftPadding=0, bottomPadding=0, 
            rightPadding=0, topPadding=0,
            showBoundary=True)
        frame2 = Frame(100, 600, 240, 50, id='F2', 
            leftPadding=0, bottomPadding=0, 
            rightPadding=0, topPadding=0,
            showBoundary=True)
        self.allowSplitting = True
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        template = PageTemplate('normal', [frame1, frame2])
        self.addPageTemplates(template)
        

class MyTestCase(unittest.TestCase):
    "Test wrapping/splitting one line paragraph."

    def setUp(self):
        self.output = "output"


    def test0(self):
        "Test wrapping/splitting one line over two frames."

        stylesheet=getSampleStyleSheet()
        normal = stylesheet['BodyText']
        normal.fontSize = 20
        normal.leading = normal.fontSize
        normal.fontName = "Times-Roman"
    
        path = "input/test_twoframes.sample.utf8.txt"
        text = open(path).read()
        story = []
        # p = Paragraph(text, normal)
        p = SimpleParagraph(text, normal)
        story.append(p)
            
        outPath = join(self.output, splitext(basename(path))[0] + ".pdf")
        doc = MyDocTemplate(outPath)
        doc.build(story)


if __name__ == '__main__':
    unittest.main()
