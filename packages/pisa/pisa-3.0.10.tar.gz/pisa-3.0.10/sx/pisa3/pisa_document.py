# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 20 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-09 12:58:24 +0200 (Di, 09 Okt 2007) $"
__svnid__   = "$Id: pml.py 20 2007-10-09 10:58:24Z holtwick $"

from pisa_context import pisaContext
from pisa_parser import pisaParser
from pisa_util import *
from pisa_reportlab import *

import cStringIO
import os
import types

def pisaDocument(
    src, 
    dest, 
    path = None, 
    link_callback = None,
    debug = 0,
    **kw):

    c = pisaContext(
        path, 
        debug = debug)
    c.pathCallback = link_callback
    
    # XXX Handle strings and files    
    if type(src) in types.StringTypes:
        src = cStringIO.StringIO(src)
    
    pisaParser(src, c)

    # Avoid empty pages
    if not c.story:
        c.addPara(force=True)

    # Remove anchors if they do not exist (because of a bug in Reportlab)
    for frag, anchor in c.anchorFrag:       
        if anchor not in c.anchorName:                        
            frag.link = None
            
    out = cStringIO.StringIO()
    
    doc = PmlBaseDoc(
        out,
        pagesize = c.pageSize,
        author = c.meta["author"].strip(),
        title = c.meta["title"].strip(),
        showBoundary = 0,
        allowSplitting = 1)

    if c.templateList.has_key("body"):
        body = c.templateList["body"]
        del c.templateList["body"]
    else:
        x, y, w, h = getBox("1cm 1cm -1cm -1cm", c.pageSize)    
        body = PmlPageTemplate(
            id="body",
            frames=[
                Frame(x, y, w, h, 
                    id = "body",
                    leftPadding = 0,
                    rightPadding = 0,
                    bottomPadding = 0,
                    topPadding = 0)],
            pagesize = c.pageSize)

    # print body.frames

    # print [body] + c.templateList.values()
    doc.addPageTemplates([body] + c.templateList.values())             
    doc.build(c.story)    
    
    # Add watermarks
    if pyPdf:             
        # print c.pisaBackgroundList   
        for bgouter in c.pisaBackgroundList:                    
            # If we have at least one background, then lets do it
            if bgouter:
                istream = out 
                # istream.seek(2,0) #cStringIO.StringIO(data)
                try:                            
                    output = pyPdf.PdfFileWriter()
                    input1 = pyPdf.PdfFileReader(istream)
                    ctr = 0                        
                    for bg in c.pisaBackgroundList:                                
                        page = input1.getPage(ctr)
                        if bg:
                            if os.path.exists(bg):                    
                                # print "BACK", bg                
                                bginput = pyPdf.PdfFileReader(open(bg, "rb"))
                                # page.mergePage(bginput.getPage(0))
                                pagebg = bginput.getPage(0)
                                pagebg.mergePage(page)
                                page = pagebg 
                            else:
                                c.warning("Background PDF %s doesn't exist." % bg)
                        output.addPage(page)
                        ctr += 1
                    out = cStringIO.StringIO()
                    output.write(out)
                    # data = sout.getvalue()
                except Exception, e:
                    c.error("Exception: %s" % str(e))
                # istream.close()
            # Found a background? So leave loop after first occurence
            break
    else:
        c.warning("pyPDF not installed!")

    # Get result
    data = out.getvalue()
    dest.write(data)

    return c
