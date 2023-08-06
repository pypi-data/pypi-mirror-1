# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__reversion__ = "$Revision: 20 $"
__author__    = "$Author: holtwick $"
__date__      = "$Date: 2007-10-09 12:58:24 +0200 (Di, 09 Okt 2007) $"

from sx.pisa3 import pisa
from sx.pisa3 import pisa_pdf

if __name__=="__main__":

    pdf = pisa_pdf.pisaPDF()

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

    # Write the result to a file and open it
    filename = __file__ + ".pdf"
    result = pdf.getvalue()
    open(filename, "wb").write(result)
    pisa.startViewer(filename)
