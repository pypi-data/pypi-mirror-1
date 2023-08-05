# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002      ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 104 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-31 17:39:49 +0100 (Mi, 31 Okt 2007) $"

try:
    # Small patch for Python 2.5
    import sitecustomize
except:
    pass

import os
import sys
import cgi
import cStringIO

import sx.pisa3 as pisa

def dumpErrors(pdf, showLog=True):
    if showLog and pdf.log:
        for mode, line, msg, code in pdf.log:
            print "%s in line %d: %s" % (mode, line, msg)

    if pdf.warn:
        print "*** %d WARNINGS OCCURED" % pdf.warn

    if pdf.err:
        print "*** %d ERRORS OCCURED" % pdf.err

def startViewer(filename):
    " Open PDF with a viewer like Adobe Reader "
    if filename:
        try:
            # This should start a file with it's
            # corresponding application. Works fine for Windows
            os.startfile(str(filename))
        except:
            # This works under MacOS X
            cmd = 'open "%s"' % str(filename)
            os.system(cmd)

def testSimple(
    data="Hello <b>World</b>",
    dest="test.pdf"):

    """
    Simple test showing how to create a PDF file from
    PML Source String. Also shows errors and tries to start
    the resulting PDF
    """

    pdf = pisa.CreatePDF(
        cStringIO.StringIO(data),
        file(dest, "wb")
        )

    if pdf.err:
        dumpErrors(pdf)
    else:
        startViewer(dest)

def testCGI(data="Hello <b>World</b>"):

    """
    This one shows, how to get the resulting PDF as a
    file object and then send it to STDOUT
    """

    result = cStringIO.StringIO()

    pdf = pisa.CreatePDF(
        cStringIO.StringIO(data),
        result
        )

    if pdf.err:
        print "Content-Type: text/plain"
        print
        dumpErrors(pdf)
    else:
        print "Content-Type: application/octet-stream"
        print
        sys.stdout.write(result.getvalue())

def testBackgroundAndImage(
    src="test-background.html",
    dest="test-background.pdf"):

    """
    Simple test showing how to create a PDF file from
    PML Source String. Also shows errors and tries to start
    the resulting PDF
    """

    pdf = pisa.CreatePDF(
        file(src, "r"),
        file(dest, "wb"),
        log_warn = 1,
        log_err = 1,
        path = os.path.join(os.getcwd(), src)
        )

    dumpErrors(pdf)
    if not pdf.err:
        startViewer(dest)

def testURL(
    url="http://pisa.spirito.de",
    dest="test-website.pdf"):

    """
    Loading from an URL. We open a file like object for the URL by
    using 'urllib'. If there have to be loaded more data from the web,
    the pisaLinkLoader helper is passed as 'link_callback'. The 
    pisaLinkLoader creates temporary files for everything it loads, because
    the Reportlab Toolkit needs real filenames for images and stuff. Then
    we also pass the url as 'path' for relative path calculations.
    """
    import urllib
    
    pdf = pisa.CreatePDF(
        urllib.urlopen(url),
        file(dest, "wb"),
        log_warn = 1,
        log_err = 1,
        path = url,
        link_callback = pisa.pisaLinkLoader(url).getFileName
        )

    dumpErrors(pdf)
    if not pdf.err:
        startViewer(dest)
        
if __name__=="__main__":
    testSimple()
    # testCGI()
    testBackgroundAndImage()
    testURL()
