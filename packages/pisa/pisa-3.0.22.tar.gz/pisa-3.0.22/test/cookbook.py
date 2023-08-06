# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick            ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 176 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2008-03-15 00:11:47 +0100 (Sa, 15 Mrz 2008) $"

"""
HTML/CSS to PDF converter

Most people know how to write a page with HTML and CSS. Why not using these skills to dynamically generate PDF documents using it? The "pisa" project http://www.htmltopdf.org enables you to to this quite simple.
"""

import cStringIO
import ho.pisa as pisa
import os

# Shortcut for dumping all logs to the screen
pisa.showLogging()

def HTML2PDF(data, filename, open=False):

    """
    Simple test showing how to create a PDF file from
    PML Source String. Also shows errors and tries to start
    the resulting PDF
    """

    pdf = pisa.CreatePDF(
        cStringIO.StringIO(data),
        file(filename, "wb"))

    if open and (not pdf.err):
        os.startfile(str(filename))

    return not pdf.err

if __name__=="__main__":
    HTMLTEST = """
    <html><body>
    <p>Hello <strong style="color: #f00;">World</strong>
    <hr>
    <table border="1" style="background: #eee; padding: 0.5em;">
        <tr>
            <td>Amount</td>
            <td>Description</td>
            <td>Total</td>
        </tr>
        <tr>
            <td>1</td>
            <td>Good weather</td>
            <td>0 EUR</td>
        </tr>
        <tr style="font-weight: bold">
            <td colspan="2" align="right">Sum</td>
            <td>0 EUR</td>
        </tr>
    </table>
    </body></html>
    """

    HTML2PDF(HTMLTEST, "test.pdf", open=True)
