# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__reversion__ = "$Revision: 20 $"
__author__    = "$Author: holtwick $"
__date__      = "$Date: 2007-10-09 12:58:24 +0200 (Di, 09 Okt 2007) $"

from sx.pisa3.pisa_pdf import *
import sx.pisa3.pisa as pisa

if __name__=="__main__":

    pdf = pisaPDF()

    subPdf = pisa.pisaDocument(
        u"""
            Hello <strong>World</strong>
        """)
    pdf.addDocument(subPdf)

    raw = open("test-loremipsum.pdf", "rb").read()
    pdf.addFromString(raw)

    pdf.addFromURI("test-loremipsum.pdf")

    pdf.addFromFile(open("test-loremipsum.pdf", "rb"))

    datauri = pisa.makeDataURIFromFile("test-loremipsum.pdf")
    pdf.addFromURI(datauri)

    filename = __file__ + ".pdf"
    open(filename, "wb").write(pdf.getvalue())
    pisa.startViewer(filename)
