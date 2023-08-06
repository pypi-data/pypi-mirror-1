#!/bin/env/python
# -*- coding: utf-8 -*-

"Tests for pdfnup module."


import os
import sys
import math
import unittest
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from pyPdf import PdfFileReader, PdfFileWriter
except ImportError:
    _MSG = "Please install pyPdf first, see http://pybrary.net/pyPdf"
    raise RuntimeError(_MSG)

from pdfnup import generateNup


def group(seq, groupLen=None):
    """Group a sequence ino a list of seqences of some length".
    
    e.g. group(range(10), 2) -> [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
    """
    
    if groupLen is None:
        groupLen = len(seq)
    
    res = [seq[i:i+groupLen] for i in range(0, len(seq), groupLen)]
    
    return res
    

class LayoutingTests(unittest.TestCase):
    "Test layouting with a square or half square number of pages per sheet."

    def test0(self):
        "Test generating several 'n-up' docs, n = m**2..."

        for path0 in ("samples/test-a4-l.pdf", "samples/test-a4-p.pdf"):
            for n in (4, 9, 16):
                outName = os.path.splitext(path0)[0] + "-%dup.pdf" % n
                path1 = os.path.join(".", outName)
                generateNup(path0, n, path1, verbose=True) # , dirs="UL")
    
                # assert output has correct number of pages
                input = PdfFileReader(file(path0, "rb"))
                np0 = input.getNumPages()
                input = PdfFileReader(file(path1, "rb"))
                np1 = input.getNumPages()
                self.assertEqual(np1, math.ceil(np0 / float(n)))
    
                # assert output page(s) has/have correct text content
                for pn in range(np1):
                    page = input.getPage(pn)
                    text = page.extractText().split()
                    exp = group([str(num) for num in range(np0)], n)[pn]
                    self.assertEqual(text, exp)


    def test1(self):
        "Test generating several 'n-up' docs, n = (m**2) / 2..."

        for path0 in ("samples/test-a4-l.pdf", "samples/test-a4-p.pdf"):
            for n in (2, 8, 18):
                outName = os.path.splitext(path0)[0] + "-%dup.pdf" % n
                path1 = os.path.join(".", outName)
                generateNup(path0, n, path1, verbose=True) # , dirs="UL")
    
                # assert output has correct number of pages
                input = PdfFileReader(file(path0, "rb"))
                np0 = input.getNumPages()
                input = PdfFileReader(file(path1, "rb"))
                np1 = input.getNumPages()
                self.assertEqual(np1, math.ceil(np0 / float(n)))
    
                # assert output page(s) has/have correct text content
                for pn in range(np1):
                    page = input.getPage(pn)
                    text = page.extractText().split()
                    exp = group([str(num) for num in range(np0)], n)[pn]
                    self.assertEqual(text, exp)


    def test2(self):
        "Test generating several 'n-up' docs in 'legal' format."
        # minipages are squeezed, i.e. they lose their original page ratio...
        # needs to be addressed later...

        for path0 in ("samples/test-legal-p.pdf",):
            for n in (2, 4, 8, 9):
                outName = os.path.splitext(path0)[0] + "-%dup.pdf" % n
                path1 = os.path.join(".", outName)
                generateNup(path0, n, path1, verbose=True) # , dirs="UL")
    
                # assert output has correct number of pages
                input = PdfFileReader(file(path0, "rb"))
                np0 = input.getNumPages()
                input = PdfFileReader(file(path1, "rb"))
                np1 = input.getNumPages()
                self.assertEqual(np1, math.ceil(np0 / float(n)))
    
                # assert output page(s) has/have correct text content
                for pn in range(np1):
                    page = input.getPage(pn)
                    text = page.extractText().split()
                    exp = group([str(num) for num in range(np0)], n)[pn]
                    self.assertEqual(text, exp)


class RotationTests(unittest.TestCase):
    "Test input documents with rotated pages."

    def test0(self):
        "Test on rotated pages in portrait format."

        output = PdfFileWriter()
        input1 = PdfFileReader(file("samples/test-a4-p.pdf", "rb"))
        numPages = input1.getNumPages()
        for i in range(numPages):
            p = input1.getPage(i)
            p.rotateClockwise((i % 4) * 90)
            output.addPage(p)
        outPath = "samples/test-a4-pr.pdf"
        outputStream = file(outPath, "wb")
        output.write(outputStream)
        outputStream.close()
        for j in (2, 4, 8, 9): 
            generateNup(outPath, j, verbose=True)


    def test1(self):
        "Test on rotated pages in landscape format."

        output = PdfFileWriter()
        input1 = PdfFileReader(file("samples/test-a4-l.pdf", "rb"))
        numPages = input1.getNumPages()
        for i in range(numPages):
            p = input1.getPage(i)
            p.rotateClockwise((i % 4) * 90)
            output.addPage(p)
        outPath = "samples/test-a4-lr.pdf"
        outputStream = file(outPath, "wb")
        output.write(outputStream)
        outputStream.close()
        for j in (2, 4, 8, 9): 
            generateNup(outPath, j, verbose=True)


class InMemoryTests(unittest.TestCase):
    "Test with an input document in memory."

    def test0(self):
        "Test using file object as input document."

        n = 4
        path0  = "samples/test-a4-l.pdf"
        f = open(path0, "rb")
        outName = os.path.splitext(path0)[0] + "-%dup-fromFile.pdf" % n
        path1 = os.path.join(".", outName)
        generateNup(f, n, path1, verbose=True)


    def test1(self):
        "Test using StringIO object input document."

        n = 4
        path0  = "samples/test-a4-l.pdf"
        pdfCode = open(path0, "rb").read()
        f = StringIO(pdfCode)
        outName = os.path.splitext(path0)[0] + "-%dup-fromStringIO.pdf" % n
        path1 = os.path.join(".", outName)
        generateNup(f, n, path1, verbose=True)


if __name__ == "__main__":
    unittest.main()
