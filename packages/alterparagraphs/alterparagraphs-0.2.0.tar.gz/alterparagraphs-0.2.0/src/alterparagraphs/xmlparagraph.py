#!/bin/env/python
# -*- coding: utf-8 -*-

"An XML paragraph class to be used with ReportLab Platypus."

#### development barely started

import xml.sax
from xml.sax.handler import ContentHandler, ErrorHandler

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.flowables import Flowable

from minimalparagraph import MinimalParagraph


class MyHandler(ContentHandler):
    "A SAX content handler."
    
    def __init__(self, style):
        self.style = style
        self.words = []    

    def startElement(self, name, attrs):
        return

    def endElement(self, name):
        return

    def characters(self, content):
        # print repr(content.strip())
        fn, fs = self.style.fontName, self.style.fontSize
        cont = content.strip()
        if " " not in cont:
            self.words.append({
                "text": content, 
                "width": stringWidth(content.strip(), fn, fs)}
            )
        else:
            self.words += [{"text": w, "width": stringWidth(w, fn, fs)} 
                for w in cont.split()]


class ErrorHandler(ErrorHandler):
    "A SAX error handler."
    
    def setContent(self, content):
        self.content = content
        
    def error(self, exception):
        print "error:", exception
        
    def fatalError(self, exception): 
        print "fatalError:", exception
        
    def warning(self, exception): 
        print "warning:", exception
        

class XMLParagraph(MinimalParagraph):
    """A minimal XML Paragraph class.
    
    text = "foo <font color='red'> and </font> bar"
    
    after parsed():
    words = [
        {"text":"foo", "width":...),
        {"opentag":"font", "color":"red"),
        {"text":"and", "width":...),
        {"endtag":"foo"),
        {"text":"bar", "width":...),
    ]

    after wrap():
    words = [
        {"text":"foo", "width":..., "pos":(x, y)),
        {"text":"and", "width":..., "pos":(x, y)),
        {"text":"bar", "width":..., "pos":(x, y)),
    ]
    """

    def __init__(self, text, style, **kwDict):
        MinimalParagraph.__init__(self, text, style)
        
        self.text = text
        self.style = style

        # handle named arguments        
        self.words = kwDict.get("words", None) # previously parsed text
        self.containsFirstLine = kwDict.get("containsFirstLine", False)
        self.debug = kwDict.get("debug", False)
        
        # set later...
        self.dy = None
        self.words = None
        self.splitted = None
        self.splitIndex = None


    def parse(self, text):
        "Parse text and build a word list with string widths out of it."

        text = text.replace(chr(10), " ")
        text = text.replace(chr(13), " ")
        text = '<?xml version="1.0" encoding="UTF-8"?><para>%s</para>' % text

        if self.debug:
            print "*** parse", text

        handler = MyHandler(self.style)
        errhandler = ErrorHandler()
        xml.sax.parseString(text, handler, errhandler)

        self.words = handler.words
