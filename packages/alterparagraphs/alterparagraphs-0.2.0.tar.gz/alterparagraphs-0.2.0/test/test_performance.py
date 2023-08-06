#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

# Use Psyco, if desired and available
if True:
    try:
        import psyco
        psyco.full()
        _v = ".".join([str(o) for o in psyco.version_info])
        print "(Using Psyco version %s)" % _v
    except ImportError:
        pass

import re, os, sys, time, stat, getopt, urllib
import unittest

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import Frame, Paragraph
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate

sys.path.insert(0, "../src/alterparagraphs")

from minimalparagraph import MinimalParagraph
from simpleparagraph import SimpleParagraph
from countingparagraph import CountingParagraph
from colouredparagraph import ColouredParagraph
from iconizedparagraph import IconizedParagraph
from graphicsparagraph import GraphicsParagraph
from hyphenatedparagraph import HyphenatedParagraph
from highlightedparagraph import HighlightedParagraph
from hyphenlightedparagraph import HyphenlightedParagraph
from ttfparagraph import TTFParagraph
# from xmlparagraph import XMLParagraph


# config
INPUT_DIR = "input"
OUTPUT_DIR = "output"


class MyDocTemplate(BaseDocTemplate):
    "Simple layout with two columns on every page."

    def __init__(self, filename, **kw):
        frame1 = Frame(2*cm, 2*cm, 8.5*cm, 26*cm, id='F1', 
            leftPadding=0, bottomPadding=0, 
            rightPadding=0, topPadding=0,
            showBoundary=True)
        frame2 = Frame(11*cm, 2*cm, 8.5*cm, 26*cm, id='F2', 
            leftPadding=0, bottomPadding=0, 
            rightPadding=0, topPadding=0,
            showBoundary=True)
        self.allowSplitting = True
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        template = PageTemplate('normal', [frame1, frame2])
        self.addPageTemplates(template)
        

def loadText(path, numParagraphs=None):
    "Load text file and return list of paragraphs."
    
    nl = "\n\n+"
    text = open(path, "rU").read()
    text = text.decode("utf8")
    paragraphs = re.split(nl, text)
    paragraphs = [p for p in paragraphs if p.strip()]
    if numParagraphs != None or numParagraphs >= 0:
        paragraphs = paragraphs[:numParagraphs]
    print "#words:", len(text.split())
    print "#lines:", len(text.split("\n"))
    print "#paragraphs:", len(paragraphs)

    return paragraphs
    

def _render(path, ParagraphClass, style, paragraphs):
    "Render a text file, return time needed and resulting file size."
    
    story = []
    for i, para in enumerate(paragraphs):
        para = para.replace("\r", " ")
        if ParagraphClass == HyphenatedParagraph:
            p = ParagraphClass(para, style) # , debug=True)
        else:
            p = ParagraphClass(para, style)
        if ParagraphClass == CountingParagraph:
            p.debug = True
        story.append(p)
    args = (os.path.basename(os.path.splitext(path)[0]), ParagraphClass.__name__)
    outPath = os.path.join(OUTPUT_DIR, "%s-%s.pdf" % args)
    doc = MyDocTemplate(outPath)
    
    t0 = time.time()
    doc.build(story)
    t = time.time() - t0
    
    fs = os.stat(outPath)[stat.ST_SIZE]
    return t, fs


def render(path, ParagraphClass, style, paragraphs):
    "Render a text file, return time needed and resulting file size."
    
    story = []
    for i, para in enumerate(paragraphs):
        para = para.replace("\r", " ")
        p = ParagraphClass(para, style)
        story.append(p)
    args = (os.path.basename(os.path.splitext(path)[0]), ParagraphClass.__name__)
    outPath = os.path.join(OUTPUT_DIR, "%s-%s.pdf" % args)
    doc = MyDocTemplate(outPath)
    
    t0 = time.time()
    doc.build(story)
    t = time.time() - t0
    
    fs = os.stat(outPath)[stat.ST_SIZE]
    return t, fs


def process(path, fn="Times-Roman", fs=12, maxNumParas=None):
    stylesheet=getSampleStyleSheet()
    normal = stylesheet['BodyText']
    # supported style attributes:
    normal.fontName = fn
    normal.fontSize = fs
    normal.leading = fs*1.2
    normal.spaceBefore = 0
    normal.spaceAfter = 10
    #normal.firstLineIndent = 30
    #normal.leftIndent = 10
    #normal.rightIndent = 10
    normal.textColor = colors.darkblue
    # normal.alignment = TA_RIGHT
    # not yet supported:
    if False:
        normal.backColor = colors.lemonchiffon
        normal.bulletFontName = "Times-Roman"
        normal.bulletFontSize = 12
        normal.bulletIndent = 10
        normal.bulletColor = colors.red

    print "input file:", path

    paragraphs = loadText(path, maxNumParas)

    # create PDF using standard ReportLab paragraph class
    t1, fs1 = render(path, Paragraph, normal, paragraphs)
    print "%s, time needed: %f" % (Paragraph.__name__, t1)
    print "%s, file size: %d" % (Paragraph.__name__, fs1)

    # create PDF using alternative minimal paragraph class
    # for comparison
    for pc in (MinimalParagraph, GraphicsParagraph, TTFParagraph, SimpleParagraph, ColouredParagraph, CountingParagraph, HighlightedParagraph, IconizedParagraph, HyphenatedParagraph, HyphenlightedParagraph):
        t2, fs2 = render(path, pc, normal, paragraphs)
        print "%s, time needed: %f (%.2f x)" % (pc.__name__, t2, t2/t1)
        print "%s, file size: %d (%.2f x)" % (pc.__name__, fs2, float(fs2)/fs1)


class PerformanceComparisonTestCase(unittest.TestCase):
    "Test paragraph comparison."

    def test0(self):
        "Test paragraph comparison."

        destPath = "input/alice30.txt"
        process(destPath, fn="Helvetica", fs=12, maxNumParas=100)


if __name__ == "__main__":
    unittest.main()
