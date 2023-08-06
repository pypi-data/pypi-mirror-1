.. -*- mode: rst -*-

===============
Alterparagraphs
===============

---------------------------------------------------------------
Alternative implementations for ReportLab paragraph flowables.
---------------------------------------------------------------

:Author:  Dinu Gherman <gherman@darwin.in-berlin.de>
:Homepage: http://www.dinu-gherman.net/
:Version: Version 0.2.0
:Date: 2008-07-07
:Copyright: GNU Public Licence v3 (GPLv3)


About
-----

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
implementation. 


Installation
------------

After downloading the file ``alterparagraphs-0.2.0.tar.gz`` in your 
download directory, change into this directory and run the following 
command to unpack `alterparagraphs`::

  $ tar xfz alterparagraphs-0.2.0.tar.gz

Then change into the newly created directory ``alterparagraphs`` and 
install `alterparagraphs` by running the following command::

  $ python setup.py install

This will install a Python package named `alterparagraphs` in the 
``site-packages`` subfolder of your Python interpreter.


Testing
-------

The `alterparagraphs` package comes with a Unittest test suite which 
can be run like this before (or after) building the package::
 
  $ cd test
  $ python test_all.py

After the test run you'll find some PDF files in the directory 
``test/output``.


Bug reports
-----------

Please report bugs and patches to Dinu Gherman 
<gherman@darwin.in-berlin.de>. Don't forget to include information 
about the operating system, Python and ReportLab versions being used.
