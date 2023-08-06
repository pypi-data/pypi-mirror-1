#!/bin/env/python
# -*- coding: utf-8 -*-

"An example for a paragraph generated externally by TeX."

import re

from reportlab.pdfbase.pdfmetrics import stringWidth

from minimalparagraph import MinimalParagraph


class TexParagraph(MinimalParagraph):
    "A TeX paragraph."

    pass