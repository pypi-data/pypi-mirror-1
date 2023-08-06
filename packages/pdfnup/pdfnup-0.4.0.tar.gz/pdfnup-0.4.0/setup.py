#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup


__version__ = "0.4.0"
__license__ = "GPL 3"
__author__ = "Dinu Gherman"
__date__ = "2009-06-15"


long_description = """\
`Pdfnup` is a Python module and command-line tool for layouting multiple 
pages per sheet of a PDF document. Using it you can take a PDF document 
and create a new PDF document from it where each page contains a number
of minimized pages from the original PDF file. 

Right now `pdfnup` should be used on documents with all pages the same 
size, and half square page numbers per sheet work best on paper sizes
of the ISO A series.

Basically, `pdfnup` wrapps `pyPdf <http://pypi.python.org/pypi/pyPdf>`_, 
a package written by Mathieu Fenniak, which does not provide tools like 
this for using the core functionality easily from the command-line or 
from a Python module. `Pdfnup` itself was much inspired from some code 
written by Henning von Bargen - thanks, Henning!

This release provides full support for file objects and StringIO objects
for input as well as output documents.


Features
++++++++

- save minimized pages of a given PDF document in a new PDF document
- place n pages per sheet, with n being square or half square
- customize layout order, both horizontally and vertically
- turn rotated pages to make them all have the same format 
- allow patterns for output files
- supports file-like objects for input and output documents
- install a Python module named ``pdfnup.py``
- install a Python command-line script named ``pdfnup``
- provide a Unittest test suite


Examples
++++++++

You can use `pdfnup` as a Python module e.g. like in the following
interactive Python session::

    >>> from pdfnup import generateNup
    >>>
    >>> generateNup("file.pdf", 8, verbose=True)
    written: file-8up.pdf
    >>>
    >>> generateNup("file.pdf", 8, dirs="LD", verbose=True)
    written: file-8up.pdf
    >>>
    >>> f = open("file.pdf")
    >>> generateNup(f, 8, outputPat="out-%(n)dup.pdf", verbose=True)
    written: out-8up.pdf

In addition there is a script named ``pdfnup``, which can be used 
more easily from the system command-line like this (you can see many 
more examples when typing ``pdfnup -h`` on the command-line)::

    $ pdfnup -V file.pdf
    written: file-4up.pdf
    $ pdfnup -V -n 8 file.pdf
    written: file-8up.pdf
    $ pdfnup -V -n 8 -l LD file.pdf
    written: file-8up.pdf
    $ pdfnup -V -n 9 /path/file[12].pdf  
    written: /path/file1-9up.pdf
    written: /path/file2-9up.pdf
    $ pdfnup -V -n 8 -o "%(dirname)s/foo.pdf" /path/file.pdf
    written: /path/foo.pdf
"""

classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python",
    "Topic :: Utilities",
    "Topic :: Printing",
]

baseURL = "http://www.dinu-gherman.net/"

setup(
    name = 'pdfnup',
    version = __version__,
    description = 'Layout multiple pages per sheet of a PDF document.',
    long_description = long_description,
    date = __date__,
    author = __author__,
    author_email = "@".join(["gherman", "darwin.in-berlin.de"]),
    maintainer = __author__,
    maintainer_email = "@".join(["gherman", "darwin.in-berlin.de"]),
    license = __license__,
    platforms = ['Posix', 'Windows'],
    keywords = ['PDF', 'minimizig pages'],
    url = baseURL,
    download_url = baseURL + "tmp/pdfnup-%s.tar.gz" % __version__,
    py_modules = ["pdfnup"],
    scripts = ['pdfnup'],
    classifiers = classifiers,

    # for setuptools, only
    zip_safe = False,
    install_requires = ["pyPdf>1.10"],
)
