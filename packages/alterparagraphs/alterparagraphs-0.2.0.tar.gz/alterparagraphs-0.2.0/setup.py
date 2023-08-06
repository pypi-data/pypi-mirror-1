#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
from distutils.core import setup

from alterparagraphs import __version__, __date__, __license__, __author__


setupCommand = sys.argv[1]


# first try converting README from ReST to HTML, if Docutils is installed
# (else issue a warning)

if setupCommand in ("sdist", "build"):
    toolName = "rst2html.py"
    res = os.popen("which %s" % toolName).read().strip()
    if res.endswith(toolName):
        cmd = "%s '%s' '%s'" % (res, "README.txt", "README.html")
        print "running command %s" % cmd
        cmd = os.system(cmd)
    else:
        print "Warning: No '%s' found. 'README.{txt|html}'" % toolName,
        print "might be out of synch."


# description for Distutils to do its business

package_data = {
    "alterparagraphs": ["dict/*"],
}

baseURL = "http://www.dinu-gherman.net/"

setup(
    name = "alterparagraphs",
    version = __version__,
    description = "Alternative paragraphs for ReportLab.",
    long_description = """\
`Alterparagraphs` is an ongoing effort for providing a family of
paragraph implementations, each to be used as a replacement for the 
regular and only paragraph flowable inside the ReportLab package.

The idea behind this collection of paragraphs is to provide simple 
implementations that can be more easily understood and extended than 
the monolithic paragraph implementation as implemented by ReportLab. 

Note that many of the paragraph classes in `alterparagraphs` are not 
finished in the sense that they are directly ready for production 
(this is especially true for the XMLParagraph, the development of 
which has barely started). You must test yourself if they are suitable 
for your purpose. In any case it should be much easier to tweak them 
to make them do what you need compared to the standard ReportLab 
implementation.""",
    date = __date__,
    author = __author__,
    author_email = "gherman@darwin.in-berlin.de",
    maintainer = __author__,
    maintainer_email = "gherman@darwin.in-berlin.de",
    license = __license__,
    platforms = ["Posix", "Windows"],
    keywords = ["ReportLab", "alternative paragraphs"],
    url = baseURL,
    download_url = baseURL + "tmp/alterparagraphs-%s.tar.gz" % __version__,
    package_dir = {"alterparagraphs": "src/alterparagraphs"},
    packages = ["alterparagraphs"],
    package_data = package_data,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
    ]
)


# simulate setup option "package_data" for Python < 2.4

if sys.version_info[:2] < (2, 4) and setupCommand in ("build", "install"):
    # Distutils copies the addidional data files itself during "install"
    import sys, glob, shutil
    from os.path import join
    for (k, v) in package_data.items():
        for f in v:
            files = glob.glob(join(k, f))
            for src in files:
                dst = join("build/lib", src)
                print "copying %s -> %s" % (src, dst)
                shutil.copy2(src, dst)
