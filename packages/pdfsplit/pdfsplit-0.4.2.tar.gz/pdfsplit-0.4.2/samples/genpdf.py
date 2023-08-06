#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"Generate test PDF document for pdfslice"

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen.canvas import Canvas


def genTestFile(path, numPages):
    "Generate a PDF doc with *very* big page numbers on all pages."
    
    size = landscape(A4)
    canv = Canvas(path, pagesize=size)
    for i in range(numPages):
        canv.setFont("Helvetica", size[1]*1.2)
        x, y = size[0]/2.0, size[1]*0.1
        text = u"%s" % i
        canv.drawCentredString(x, y, text) 
        canv.showPage()
    canv.save() 

    
if __name__ == '__main__':    
    genTestFile("test.pdf", 50)
