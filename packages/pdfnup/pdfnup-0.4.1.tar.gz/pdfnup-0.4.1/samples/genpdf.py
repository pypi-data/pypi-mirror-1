#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"Generate test PDF documents for pdfnup."

from reportlab.lib.colors import black, white, pink, lightblue
from reportlab.lib.pagesizes import A4, legal, landscape
from reportlab.pdfgen.canvas import Canvas


# not used anymore
def genTestFile(path, numPages):
    "Generate a PDF doc with *very* big page numbers on all pages."
    
    size = landscape(A4)
    canv = Canvas(path, pagesize=size)
    for i in range(numPages):
        canv.setFont("Helvetica", size[1]*1.2)
        x, y = size[0]/2.0, size[1]*0.1
        text = u"%s" % i
        if i % 2 == 1:
            canv.setStrokeColor(black)
            canv.setFillColor(black)
            canv.rect(0, 0, size[0], size[1], fill=True)
        if i % 2 == 1:
            canv.setFillColor(white)
        else:
            canv.setFillColor(black)
        canv.drawCentredString(x, y, text) 
        canv.showPage()
    canv.save() 


def generateNumberedPages(numPages, pageSize, orientation, bgColor, outPath):
    "Generate a 10 page document with one big number per page."
    
    if orientation == "landscape":
        pageSize = landscape(pageSize)
    canv = Canvas(outPath, pagesize=pageSize)

    for i in range(numPages):
        canv.setFont("Helvetica", 500)
        text = u"%s" % i
        if i % 2 == 0:
            canv.setStrokeColor(bgColor)
            canv.setFillColor(bgColor)
            canv.rect(0, 0, pageSize[0], pageSize[1], stroke=True, fill=True)
            canv.setFillColor(black)
        elif i % 2 == 1:
            canv.setStrokeColor(black)
            canv.setFillColor(black)
            canv.rect(0, 0, pageSize[0], pageSize[1], stroke=True, fill=True)
            canv.setFillColor(bgColor)
        if orientation == "portrait":
            canv.drawCentredString(pageSize[0]/2.0, pageSize[1]*0.3, u"%s" % i) 
        elif orientation == "landscape":
            canv.drawCentredString(pageSize[0]/2.0, pageSize[1]*0.21, u"%s" % i) 
        canv.showPage()
        
    canv.save() 


if __name__ == '__main__':
    gnp = generateNumberedPages
    gnp(50, A4, "landscape", pink, "test-a4-l.pdf")
    gnp(50, A4, "portrait", lightblue, "test-a4-p.pdf")
    gnp(50, legal, "portrait", lightblue, "test-legal-p.pdf")
