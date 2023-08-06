# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick            ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 194 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2008-04-18 18:59:53 +0200 (Fr, 18 Apr 2008) $"

import ho.pisa as pisa
import os, os.path
import logging
log = logging.getLogger(__file__)

def helloWorld():
    filename = __file__ + ".pdf"
    datauri = pisa.makeDataURIFromFile('img/denker.png')
    bguri = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir, "pdf/background-sample.pdf"))
    bguri = pisa.makeDataURIFromFile(bguri)
    html = u"""
            <style>
            @page {
                background: url("%s");
                @frame text {
                    top: 6cm;
                    left: 4cm;
                    right: 4cm;
                    bottom: 4cm;
                    -pdf-frame-border: 1;
                }
            }
            </style>

            <p>
            Hello <strong>World</strong>
            <p>
            <img src="%s">
        """ % (bguri, datauri)
    pdf = pisa.pisaDocument(
        html,
        file(filename, "wb"),
        path = __file__
        )
    if not pdf.err:
        pisa.startViewer(filename)

if __name__=="__main__":
    pisa.showLogging()
    helloWorld()
