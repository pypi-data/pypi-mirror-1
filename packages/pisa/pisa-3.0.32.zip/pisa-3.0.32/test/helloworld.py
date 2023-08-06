# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick            ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 194 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2008-04-18 18:59:53 +0200 (Fr, 18 Apr 2008) $"

import ho.pisa as pisa

def helloWorld():
    filename = __file__ + ".pdf"
    pdf = pisa.CreatePDF(
        u"Hello <strong>World</strong>",
        file(filename, "wb")
        )
    if not pdf.err:
        pisa.startViewer(filename)

if __name__=="__main__":
    pisa.showLogging()
    helloWorld()
