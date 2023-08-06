#!/bin/env/python
# -*- coding: utf-8 -*-

"""Layout multiple pages per sheet of a PDF document.

Pdfnup is a Python module and command-line tool for layouting multiple 
pages per sheet of a PDF document. Using it you can take a PDF document 
and create a new PDF document from it where each page contains a number
of minimized pages from the original PDF file. 

This can be considered a sample tool for the excellent package pyPdf by 
Mathieu Fenniak, see http://pybrary.net/pyPdf.

For further information please look into the file README.txt!
"""


import os
import sys
import math
from cStringIO import StringIO


try:
    from reportlab.pdfgen.canvas import Canvas
except ImportError:
    _MSG = "Please install reportlab first, see http://www.reportlab.org"
    raise RuntimeError(_MSG)

try:
    from pyPdf import PdfFileWriter, PdfFileReader
    from pyPdf.pdf import PageObject, ImmutableSet, ContentStream
    from pyPdf.generic import \
        NameObject, DictionaryObject, ArrayObject, FloatObject
except ImportError:
    _MSG = "Please install pyPdf first, see http://pybrary.net/pyPdf"
    raise RuntimeError(_MSG)


__version__ = "0.3.0"
__license__ = "GPL 3"
__author__ = "Dinu Gherman"
__date__ = "2008-09-24"


def isSquare(n):
    "Is this a square number?"
    
    s = math.sqrt(n)
    lower, upper = math.floor(s), math.ceil(s)
    
    return lower == upper


def isHalfSquare(n):
    "Is this a square number, divided by 2?"
    
    return isSquare(n * 2)


def calcScalingFactors(w, h, wp, hp):
    wp, hp = map(float, (wp, hp))
    
    if w == None:
        xscale = h/hp
        yscale = h/hp
    elif h == None:
        xscale = w/wp
        yscale = w/wp
    else:
        xscale = w/wp
        yscale = h/hp
        
    return xscale, yscale

    
def calcRects(pageSize, numTiles, dirs="RD"):
    "Return list of sub rects for some rect."
    
    allowdDirs = [x+y for x in "RL" for y in "UD"]
    allowdDirs += [y+x for x in "RL" for y in "UD"]
    assert dirs in allowdDirs

    width, height = pageSize
    n = numTiles
    xDir, yDir = dirs

    if isSquare(n):
        s = math.sqrt(n)
        w, h = float(width)/float(s), float(height)/float(s)
        if "R" in dirs:
            xr = range(0, int(s))
        elif "L" in dirs:
            xr = range(int(s)-1, -1, -1)
        if "D" in dirs:
            yr = range(int(s)-1, -1, -1)
        elif "U" in dirs:
            yr = range(0, int(s))
        xs = [i*w for i in xr]
        ys = [j*h for j in yr]
    elif isHalfSquare(n):
        # should issue a warning for page ratios different from 1:sqr(2) 
        s = math.sqrt(2*n)
        if width > height:
            w, h = float(width)/float(s), float(height)/float(s)*2
            if "R" in dirs:
                xr = range(0, int(s))
            elif "L" in dirs:
                xr = range(int(s)-1, -1, -1)
            if "D" in dirs:
                yr = range(int(s/2)-1, -1, -1)
            elif "U" in dirs:
                yr = range(0, int(s/2))
            xs = [i*w for i in xr]
            ys = [j*h for j in yr]
        else:
            w, h = float(width)/float(s)*2, float(height)/float(s)
            if "R" in dirs:
                xr = range(0, int(s/2))
            elif "L" in dirs:
                xr = range(int(s/2)-1, -1, -1)
            if "D" in dirs:
                yr = range(int(s)-1, -1, -1)
            elif "U" in dirs:
                yr = range(0, int(s))
            xs = [i*w for i in xr]
            ys = [j*h for j in yr]

    # decide order (first x, then y or first y then x)
    if dirs in "RD LD RU LU".split():
        rects = [(x, y, w, h) for y in ys for x in xs]
    elif dirs in "DR DL UR UL".split():
        rects = [(x, y, w, h) for x in xs for y in ys]

    return rects


def generateNup(inPath, n, outputPat=None, dirs="RD"):
    "Generate a N-up document version."    

    assert isSquare(n) or isHalfSquare(n)

    # derive the ouput path from the output pattern, if given
    if not outputPat:
        outputPat = "%(dirname)s/%(base)s-%(n)dup%(ext)s"
    dirname = os.path.dirname(inPath)
    basename = os.path.basename(inPath)
    base = os.path.basename(os.path.splitext(inPath)[0])
    ext = os.path.splitext(inPath)[1]    
    aDict = {
        "dirname":dirname, "basename":basename, 
        "base":base, "n":n, "ext":ext
    }
    outPath = outputPat % aDict

    # get info about source document
    docReader = PdfFileReader(open(inPath, "rb"))
    numPages = docReader.getNumPages()
    oldPageSize = docReader.getPage(0).mediaBox.upperRight

    # create empty output document
    if isSquare(n):
        newPageSize = oldPageSize
    elif isHalfSquare(n):
        newPageSize = oldPageSize[1], oldPageSize[0]
    np = numPages / n + numPages % n
    buf = StringIO()
    c = Canvas(None)
    c.setPageSize(newPageSize)
    c.showOutline()
    for page in range(np):
        c.showPage()
    buf.write(c.getpdfdata())
    buf.seek(0)
    open(outPath, "wb").write(buf.read())
    
    # calculate mini page areas
    rects = calcRects(newPageSize, n, dirs)
        
    # combine
    ops = []
    newPageNum = -1
    for i in range(numPages):
        if i % n == 0:
            newPageNum += 1
        op = (inPath, i, (0, 0, None, None), i/n, rects[i % n])
        ops.append(op)

    srcr = srcReader = PdfFileReader(open(inPath, "rb"))
    srcPages = [srcr.getPage(i) for i in range(srcr.getNumPages())]

    outr = outReader = PdfFileReader(open(outPath, "rb"))
    outPages = [outr.getPage(i) for i in range(outr.getNumPages())]
    output = PdfFileWriter()

    mapping = {}
    for op in ops:
        dummy, dummy, dummy, destPageNum, dummy = op
        if destPageNum not in mapping:
            mapping[destPageNum] = []
        mapping[destPageNum].append(op) 
        
    IS = ImmutableSet
    PO, AO, DO, NO = PageObject, ArrayObject, DictionaryObject, NameObject

    for destPageNum, ops in mapping.items():
        for op in ops:
            inPath, srcPageNum, srcRect, destPageNum, destRect = op
            page2 = srcPages[srcPageNum]
            page1 = outPages[destPageNum]
            pageWidth, pageHeight = page2.mediaBox.upperRight
            destX, destY, destWidth, destHeight = destRect
            xScale, yScale = calcScalingFactors(
                destWidth, destHeight, pageWidth, pageHeight)
            
            newResources = DO()
            rename = {}
            orgResources = page1["/Resources"].getObject()
            page2Resources = page2["/Resources"].getObject()
        
            for res in "ExtGState Font XObject ColorSpace Pattern Shading".split():
                res = "/" + res
                new, newrename = PO._mergeResources(orgResources, page2Resources, res)
                if new:
                    newResources[NO(res)] = new
                    rename.update(newrename)
        
            newResources[NO("/ProcSet")] = AO(
                IS(orgResources.get("/ProcSet", AO()).getObject()).union(
                    IS(page2Resources.get("/ProcSet", AO()).getObject())
                )
            )
        
            newContentArray = AO()
            orgContent = page1["/Contents"].getObject()
            newContentArray.append(PO._pushPopGS(orgContent, page1.pdf))
            page2Content = page2['/Contents'].getObject()
            page2Content = PO._contentStreamRename(page2Content, rename, page1.pdf)
            page2Content = ContentStream(page2Content, page1.pdf)
            page2Content.operations.insert(0, [[], "q"])
            arr = [xScale, 0, 0, yScale, destX, destY]
            arr = [FloatObject(str(x)) for x in arr]
            page2Content.operations.insert(1, [arr, "cm"])
            page2Content.operations.append([[], "Q"])
            newContentArray.append(page2Content)
            page1[NO('/Contents')] = ContentStream(newContentArray, page1.pdf)
            page1[NO('/Resources')] = newResources

        output.addPage(page1)

    outputStream = open(outPath, "wb")
    output.write(outputStream)
    outputStream.close()    
    
    print "written: %s" % outPath
