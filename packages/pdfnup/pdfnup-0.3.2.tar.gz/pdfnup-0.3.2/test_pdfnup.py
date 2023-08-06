#!/bin/env/python
# -*- coding: utf-8 -*-

"Tests for pdfnup module."


import os
import sys
import math
import unittest

try:
    from pyPdf import PdfFileReader
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
                generateNup(path0, n, path1) # , dirs="UL")
    
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
                generateNup(path0, n, path1) # , dirs="UL")
    
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
                generateNup(path0, n, path1) # , dirs="UL")
    
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


if __name__ == "__main__":
    unittest.main()
