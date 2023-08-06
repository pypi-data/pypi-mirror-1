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
import base64
from cStringIO import StringIO


try:
    from pyPdf import PdfFileWriter, PdfFileReader
    from pyPdf.pdf import PageObject, ImmutableSet, ContentStream
    from pyPdf.generic import \
        NameObject, DictionaryObject, ArrayObject, FloatObject
except ImportError:
    _MSG = "Please install pyPdf first, see http://pybrary.net/pyPdf"
    raise RuntimeError(_MSG)


__version__ = "0.3.1"
__license__ = "GPL 3"
__author__ = "Dinu Gherman"
__date__ = "2008-09-28"


# one empty A4 page as PDF file encoded in base64
_mtA4Pdf64 = """\
JVBERi0xLjMNCiWTjIueIFJlcG9ydExhYiBHZW5lcmF0ZWQgUERGIGRvY3VtZW50IGh0dHA6Ly93
d3cucmVwb3J0bGFiLmNvbQ0KJSAnQmFzaWNGb250cyc6IGNsYXNzIFBERkRpY3Rpb25hcnkgDQox
IDAgb2JqDQolIFRoZSBzdGFuZGFyZCBmb250cyBkaWN0aW9uYXJ5DQo8PCAvRjEgMiAwIFIgPj4N
CmVuZG9iag0KJSAnRjEnOiBjbGFzcyBQREZUeXBlMUZvbnQgDQoyIDAgb2JqDQolIEZvbnQgSGVs
dmV0aWNhDQo8PCAvQmFzZUZvbnQgL0hlbHZldGljYQ0KIC9FbmNvZGluZyAvV2luQW5zaUVuY29k
aW5nDQogL05hbWUgL0YxDQogL1N1YnR5cGUgL1R5cGUxDQogL1R5cGUgL0ZvbnQgPj4NCmVuZG9i
ag0KJSAnUGFnZTEnOiBjbGFzcyBQREZQYWdlIA0KMyAwIG9iag0KJSBQYWdlIGRpY3Rpb25hcnkN
Cjw8IC9Db250ZW50cyA3IDAgUg0KIC9NZWRpYUJveCBbIDANCiAwDQogNTk1LjI3NTYNCiA4NDEu
ODg5OCBdDQogL1BhcmVudCA2IDAgUg0KIC9SZXNvdXJjZXMgPDwgL0ZvbnQgMSAwIFINCiAvUHJv
Y1NldCBbIC9QREYNCiAvVGV4dA0KIC9JbWFnZUINCiAvSW1hZ2VDDQogL0ltYWdlSSBdID4+DQog
L1JvdGF0ZSAwDQogL1RyYW5zIDw8ICA+Pg0KIC9UeXBlIC9QYWdlID4+DQplbmRvYmoNCiUgJ1I0
JzogY2xhc3MgUERGQ2F0YWxvZyANCjQgMCBvYmoNCiUgRG9jdW1lbnQgUm9vdA0KPDwgL091dGxp
bmVzIDggMCBSDQogL1BhZ2VNb2RlIC9Vc2VOb25lDQogL1BhZ2VzIDYgMCBSDQogL1R5cGUgL0Nh
dGFsb2cgPj4NCmVuZG9iag0KJSAnUjUnOiBjbGFzcyBQREZJbmZvIA0KNSAwIG9iag0KPDwgL0F1
dGhvciAoYW5vbnltb3VzKQ0KIC9DcmVhdGlvbkRhdGUgKDIwMDgwOTI4MTQ0MjM3KQ0KIC9LZXl3
b3JkcyAoKQ0KIC9Qcm9kdWNlciAoUmVwb3J0TGFiIGh0dHA6Ly93d3cucmVwb3J0bGFiLmNvbSkN
CiAvU3ViamVjdCAodW5zcGVjaWZpZWQpDQogL1RpdGxlICh1bnRpdGxlZCkgPj4NCmVuZG9iag0K
JSAnUjYnOiBjbGFzcyBQREZQYWdlcyANCjYgMCBvYmoNCiUgcGFnZSB0cmVlDQo8PCAvQ291bnQg
MQ0KIC9LaWRzIFsgMyAwIFIgXQ0KIC9UeXBlIC9QYWdlcyA+Pg0KZW5kb2JqDQolICdSNyc6IGNs
YXNzIFBERlN0cmVhbSANCjcgMCBvYmoNCiUgcGFnZSBzdHJlYW0NCjw8IC9GaWx0ZXIgWyAvQVND
SUk4NURlY29kZQ0KIC9GbGF0ZURlY29kZSBdDQogL0xlbmd0aCA2MCA+Pg0Kc3RyZWFtDQpHYXBR
aDBFPUYsMFVcSDNpIlZvWW1xL00rQlZaMyZWSTQpM0I7LHNzVVltJy1iR0UidCJUWil0I1dffj5l
bmRzdHJlYW0NCg0KZW5kb2JqDQolICdSOCc6IGNsYXNzIFBERk91dGxpbmVzIA0KOCAwIG9iag0K
PDwgL0NvdW50IDANCiAvVHlwZSAvT3V0bGluZXMgPj4NCmVuZG9iag0KeHJlZg0KMCA5DQowMDAw
MDAwMDAwIDY1NTM1IGYNCjAwMDAwMDAxMTMgMDAwMDAgbg0KMDAwMDAwMDIwOSAwMDAwMCBuDQow
MDAwMDAwMzcyIDAwMDAwIG4NCjAwMDAwMDA2NDkgMDAwMDAgbg0KMDAwMDAwMDc4MyAwMDAwMCBu
DQowMDAwMDAwOTk0IDAwMDAwIG4NCjAwMDAwMDEwOTkgMDAwMDAgbg0KMDAwMDAwMTMwMiAwMDAw
MCBuDQp0cmFpbGVyDQo8PCAvSUQgDQogJSBSZXBvcnRMYWIgZ2VuZXJhdGVkIFBERiBkb2N1bWVu
dCAtLSBkaWdlc3QgKGh0dHA6Ly93d3cucmVwb3J0bGFiLmNvbSkgDQogWyhcMDEzXDI1NlwzNjBc
MDIyalwwMjFrbFwzMTBcMzcxXDIxNWlcMzEwW1wyNTVJKSAoXDAxM1wyNTZcMzYwXDAyMmpcMDIx
a2xcMzEwXDM3MVwyMTVpXDMxMFtcMjU1SSldIA0KDQogL0luZm8gNSAwIFINCiAvUm9vdCA0IDAg
Ug0KIC9TaXplIDkgPj4NCnN0YXJ0eHJlZg0KMTM1Mw0KJSVFT0YNCg==
"""
_mtA4Pdf = base64.decodestring(_mtA4Pdf64)


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


def exP1multiN(pdf, newPageSize, n):
    "Extract page 1 of a PDF file, copy it n times resized."
    
    # create a file-like buffer object containing PDF code
    buf = StringIO()
    buf.write(pdf)

    # extract first page and resize it as desired
    srcReader = PdfFileReader(buf)
    page1 = srcReader.getPage(0)
    page1.mediaBox.upperRight = newPageSize

    # create output and copy the first page n times
    output = PdfFileWriter()
    for i in range(n):
        output.addPage(page1)
    
    # create a file-like buffer object to hold the new PDF code
    buf2 = StringIO()
    output.write(buf2)
    buf2.seek(0)
    
    return buf2


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
    
    # buf = StringIO()
    # c = Canvas(None)
    # c.setPageSize(newPageSize)
    # c.showOutline()
    # for page in range(np):
    #     c.showPage()
    # buf.write(c.getpdfdata())
    # buf.seek(0)
    # open(outPath, "wb").write(buf.read())

    buf = exP1multiN(_mtA4Pdf, newPageSize, np)
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
