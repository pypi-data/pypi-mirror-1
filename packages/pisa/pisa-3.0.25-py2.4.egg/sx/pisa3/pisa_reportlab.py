# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__reversion__ = "$Revision: 20 $"
__author__    = "$Author: holtwick $"
__date__      = "$Date: 2007-10-09 12:58:24 +0200 (Di, 09 Okt 2007) $"

from pisa_util import *
from pisa_default import TAGS, STRING

from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate, FrameBreak, NextPageTemplate
from reportlab.platypus.tables import Table, TableStyle
from reportlab.platypus.flowables import Flowable, Image, CondPageBreak, KeepInFrame
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame
from reportlab.platypus.tableofcontents import TableOfContents

import copy
import cgi
 
class PmlBaseDoc(BaseDocTemplate):

    """
    We use our own document template to get access to the canvas
    and set some informations once.
    """

    def beforePage(self):

        # Tricky way to set producer, because of not real privateness in Python
        self.canv._doc.info.producer = "pisa HTML to PDF <http://www.htmltopdf.org>"

        '''
        # Convert to ASCII because there is a Bug in Reportlab not
        # supporting other than ASCII. Send to list on 23.1.2007

        author = toString(self.pml_data.get("author", "")).encode("ascii","ignore")
        subject = toString(self.pml_data.get("subject", "")).encode("ascii","ignore")
        title = toString(self.pml_data.get("title", "")).encode("ascii","ignore")
        # print repr((author,title,subject))

        self.canv.setAuthor(author)
        self.canv.setSubject(subject)
        self.canv.setTitle(title)

        if self.pml_data.get("fullscreen", 0):
            self.canv.showFullScreen0()

        if self.pml_data.get("showoutline", 0):
            self.canv.showOutline()

        if self.pml_data.get("duration", None) is not None:
            self.canv.setPageDuration(self.pml_data["duration"])
        '''

    def afterFlowable(self, flowable):
        # Does the flowable contain fragments?
        if getattr(flowable, "outline", False):
            self.notify('TOCEntry', (
                flowable.outlineLevel,
                cgi.escape(copy.deepcopy(flowable.text), 1),
                self.page))

class PmlPageTemplate(PageTemplate):

    def __init__(self, **kw):
        self.pisaStaticList = []
        self.pisaBackgroundList = []
        self.pisaBackground = None
        PageTemplate.__init__(self, **kw)

    def beforeDrawPage(self, canvas, doc):
        canvas.saveState()        
        try:
            
            try:
                # Paint static frames
                pagenumber = str(canvas.getPageNumber())
                for frame in self.pisaStaticList:

                    frame = copy.deepcopy(frame)
                    story = frame.pisaStaticStory

                    # Modify page number
                    for obj in story:                        
                        if isinstance(obj, PmlParagraph):
                            for frag in obj.frags:
                                if frag.pageNumber:
                                    frag.text = pagenumber
                        elif isinstance(obj, PmlTable):                            
                            # Accessing private member, but is there any other way?
                            for subobj in flatten(obj._cellvalues):
                                if isinstance(subobj, PmlParagraph):
                                    for frag in subobj.frags:
                                        if frag.pageNumber:
                                            frag.text = pagenumber

                    frame.addFromList(story, canvas)

            except Exception, e:                
                log.debug("PmlPageTemplate", exc_info=1)

            try:
                self.pisaBackgroundList.append(self.pisaBackground)
            except:
                self.pisaBackgroundList.append(None)

            # canvas.saveState()
            #try:
            #    self.pml_drawing.draw(canvas)
            #except Exception, e:
            #    # print "drawing exception", str(e)
            #    pass
                
        finally:
            canvas.restoreState()

class PmlImage(Image):

    def wrap(self, availWidth, availHeight):
        #print 123, self.drawWidth, self.drawHeight, self.pisaZoom
        #self.drawWidth *= self.pisaZoom
        #self.drawHeight *= self.pisaZoom
        # print 456, self.drawWidth, self.drawHeight
        width = min(self.drawWidth, availWidth)
        # print 999, width, self.drawWidth, availWidth
        factor = float(width) / self.drawWidth
        # print 123, factor
        self.drawHeight = self.drawHeight * factor
        self.drawWidth = width
        return Image.wrap(self, availWidth, availHeight)

class PmlParagraph(Paragraph):

    def wrap(self, availWidth, availHeight):
        # reduce the available width & height by the padding so the wrapping
        # will use the correct size
        style = self.style
        availWidth -= style.paddingLeft + style.paddingRight
        availHeight -= style.paddingTop + style.paddingBottom

        # call the base class to do wrapping and calculate the size
        Paragraph.wrap(self, availWidth, availHeight)

        # increase the calculated size by the padding
        self.width += style.paddingLeft + style.paddingRight
        self.height += style.paddingTop + style.paddingBottom
        
        return (self.width, self.height)

    def draw(self):

        # Insert page number
        '''
        if 0: #for line in self.blPara.lines:
            try:
                for frag in line.words:
                    #print 111,frag.pageNumber, frag.text
                    if frag.pageNumber:
                        frag.text = str(self.canv.getPageNumber())
            except Exception, e:
                log.debug("PmlParagraph", exc_info=1)
        '''

        # Create outline
        if getattr(self, "outline", False):

            # Check level and add all levels
            last = getattr(self.canv, "outlineLast", -1) + 1
            while last < self.outlineLevel:
                # print "(OUTLINE",  last, self.text
                key = getUID()
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(
                    self.text,
                    key,
                    last,
                    not self.outlineOpen)
                last += 1
            self.canv.outlineLast = self.outlineLevel

            key = getUID()
            # print " OUTLINE", self.outlineLevel, self.text
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(
                self.text,
                key,
                self.outlineLevel,
                not self.outlineOpen)
            last += 1

        #else:
        #    print repr(self.text)[:80]
        
        # Draw the background and borders here before passing control on to
        # ReportLab. This is because ReportLab can't handle the individual
        # components of the border independently. This will also let us
        # support more border styles eventually.
        canvas = self.canv
        style = self.style
        bg = style.backColor
        leftIndent = style.leftIndent
        bp = style.borderPadding

        x = leftIndent - bp
        y = -bp
        w = self.width - (leftIndent + style.rightIndent) + 2 * bp
        h = self.height + 2 * bp
        
        canvas.saveState()
        if bg:
            # draw a filled rectangle (with no stroke) using bg color
            canvas.setFillColor(bg)
            canvas.rect(x, y, w, h, fill=1, stroke=0)
            
        def _drawBorderLine(bstyle, width, color, x1, y1, x2, y2):            
            # We need width and border style to be able to draw a border
            if width and getBorderStyle(bstyle):
                # If no color for border is given, the text color is used (like defined by W3C)
                if color is None:
                    color = style.textColor
                canvas.setStrokeColor(color)
                canvas.setLineWidth(width)
                canvas.line(x1, y1, x2, y2)
        
        _drawBorderLine(style.borderTopStyle,
                        style.borderTopWidth,
                        style.borderTopColor,                        
                        x, y+h, x+w, y+h)
        _drawBorderLine(style.borderBottomStyle,
                        style.borderBottomWidth,
                        style.borderBottomColor,
                        x, y, x+w, y)
        _drawBorderLine(style.borderLeftStyle,
                        style.borderLeftWidth,
                        style.borderLeftColor,
                        x, y, x, y+h)
        _drawBorderLine(style.borderRightStyle,
                        style.borderRightWidth,
                        style.borderRightColor,
                        x+w, y, x+w, y+h)
        
        canvas.restoreState()
                    
        # we need to hide the bg color (if any) so Paragraph won't try to draw it again
        style.backColor = None
        
        # offset the origin to compensate for the padding
        canvas.saveState()
        canvas.translate(style.paddingLeft, -style.paddingTop)
        
        # Call the base class draw method to finish up
        Paragraph.draw(self)
        canvas.restoreState()
        
        # Reset color because we need it again if we run 2-PASS like we 
        # do when using TOC
        style.backColor = bg

class PmlTable(Table):

    def _normWidth(self, w, maxw):
        " Helper for calculating percentages "
        if type(w)==type(""):
            w = ((maxw/100.0) * float(w[:-1]))
        elif (w is None) or (w=="*"):
            w = maxw
        return min(w, maxw)

    def wrap(self, availWidth, availHeight):

        # Strange bug, sometime the totalWidth is not set !?
        try:
            self.totalWidth
        except:
            self.totalWidth = availWidth

        # Prepare values
        totalWidth = self._normWidth(self.totalWidth, availWidth)
        remainingWidth = totalWidth
        remainingCols = 0
        newColWidths = self._colWidths

        # Calculate widths that are fix
        # IMPORTANT!!! We can not substitute the private value
        # self._colWidths therefore we have to modify list in place
        for i in range(len(newColWidths)):
            colWidth = newColWidths[i]
            if (colWidth is not None) or (colWidth=='*'):
                colWidth = self._normWidth(colWidth, totalWidth)
                remainingWidth -= colWidth
            else:
                remainingCols += 1
                colWidth = None
            newColWidths[i] = (colWidth)

        # Distribute remaining space
        if remainingCols:
            for i in range(len(newColWidths)):
                if newColWidths[i] is None:
                    newColWidths[i] = (remainingWidth / remainingCols) - 0.1

        # print "New values:", totalWidth, newColWidths, sum(newColWidths)

        # Call original method "wrap()"
        # self._colWidths = newColWidths
        return Table.wrap(self, availWidth, availHeight)
    
class PmlTableOfContents(TableOfContents):

    def wrap(self, availWidth, availHeight):
        "All table properties should be known by now."

        widths = (availWidth - self.rightColumnWidth,
                  self.rightColumnWidth)

        # makes an internal table which does all the work.
        # we draw the LAST RUN's entries!  If there are
        # none, we make some dummy data to keep the table
        # from complaining
        if len(self._lastEntries) == 0:
            _tempEntries = [(0,'Placeholder for table of contents',0)]
        else:
            _tempEntries = self._lastEntries

        i = 0
        lastMargin = 0
        tableData = []
        tableStyle = [
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]
        for (level, text, pageNum) in _tempEntries:
            leftColStyle = self.levelStyles[level]
            if i: # Not for first element
                tableStyle.append((
                    'TOPPADDING',
                    (0,i), (-1, i),
                    max(lastMargin, leftColStyle.spaceBefore)))
            # print leftColStyle.leftIndent
            lastMargin = leftColStyle.spaceAfter
            #right col style is right aligned
            rightColStyle = ParagraphStyle(name='leftColLevel%d' % level,
                                           parent=leftColStyle,
                                           leftIndent=0,
                                           alignment=TA_RIGHT)
            leftPara = Paragraph(text, leftColStyle)
            rightPara = Paragraph(str(pageNum), rightColStyle)
            tableData.append([leftPara, rightPara])
            i += 1

        self._table = Table(
            tableData,
            colWidths=widths,
            style=TableStyle(tableStyle))

        self.width, self.height = self._table.wrapOn(self.canv,availWidth, availHeight)
        return (self.width, self.height)

class PmlRightPageBreak(CondPageBreak):

    def __init__(self):
        pass

    def wrap(self, availWidth, availHeight):
        if (0==(self.canv.getPageNumber()%2)):
            self.width = availWidth
            self.height = availHeight
            return (availWidth,availHeight)
        self.width = 0
        self.height = 0
        return (0,0)

class PmlLeftPageBreak(CondPageBreak):

    def __init__(self):
        pass

    def wrap(self, availWidth, availHeight):
        if (1==(self.canv.getPageNumber()%2)):
            self.width = availWidth
            self.height = availHeight
            return (availWidth,availHeight)
        self.width = 0
        self.height = 0
        return (0,0)

# --- Pdf Form

import reportlab.pdfbase.pdfform as pdfform

class PmlInput(Flowable):
            
    def __init__(self, name, type="text", width=10, height=10, default="", options=[]):
        self.width = width
        self.height = height
        self.type = type
        self.name = name
        self.default = default
        self.options = options
        
    def wrap(self, *args):
        return (self.width, self.height)
    
    def draw(self):        
        c = self.canv
            
        c.saveState()
        c.setFont("Helvetica", 10)    
        if self.type == "text":
            pdfform.textFieldRelative(c, self.name, 0, 0, self.width, self.height)
            c.rect(0, 0, self.width, self.height)   
        elif self.type == "radio":
            #pdfform.buttonFieldRelative(c, "field2", "Yes", 0, 0)
            c.rect(0, 0, self.width, self.height)   
        elif self.type == "checkbox":
             pdfform.buttonFieldRelative(c, self.name, "Yes" if self.default else "Off", 0, 0)
             c.rect(0, 0, self.width, self.height)   
        elif self.type == "select":
            pdfform.selectFieldRelative(c, self.name, self.default, self.options, 0, 0, self.width, self.height)      
            c.rect(0, 0, self.width, self.height)   

        c.restoreState()
        
        '''
        canvas.setLineWidth(6)
        canvas.setFillColor(self.fillcolor)
        canvas.setStrokeColor(self.strokecolor)
        canvas.translate(self.xoffset+self.size,0)
        canvas.rotate(90)
        canvas.scale(self.scale, self.scale)
        hand(canvas, debug=0, fill=1)    
        '''
        
# --- Flowable example

def hand(canvas, debug=1, fill=0):
    (startx, starty) = (0,0)
    curves = [
        ( 0, 2), ( 0, 4), ( 0, 8), # back of hand
        ( 5, 8), ( 7,10), ( 7,14),
        (10,14), (10,13), ( 7.5, 8), # thumb
        (13, 8), (14, 8), (17, 8),
        (19, 8), (19, 6), (17, 6),
        (15, 6), (13, 6), (11, 6), # index, pointing
        (12, 6), (13, 6), (14, 6),
        (16, 6), (16, 4), (14, 4),
        (13, 4), (12, 4), (11, 4), # middle
        (11.5, 4), (12, 4), (13, 4),
        (15, 4), (15, 2), (13, 2),
        (12.5, 2), (11.5, 2), (11, 2), # ring
        (11.5, 2), (12, 2), (12.5, 2),
        (14, 2), (14, 0), (12.5, 0),
        (10, 0), (8, 0), (6, 0), # pinky, then close
        ]
    from reportlab.lib.units import inch
    if debug: canvas.setLineWidth(6)
    u = inch*0.2
    p = canvas.beginPath()
    p.moveTo(startx, starty)
    ccopy = list(curves)
    while ccopy:
        [(x1,y1), (x2,y2), (x3,y3)] = ccopy[:3]
        del ccopy[:3]
        p.curveTo(x1*u,y1*u,x2*u,y2*u,x3*u,y3*u)
    p.close()
    canvas.drawPath(p, fill=fill)
    if debug:
        from reportlab.lib.colors import red, green
        (lastx, lasty) = (startx, starty)
        ccopy = list(curves)
        while ccopy:
            [(x1,y1), (x2,y2), (x3,y3)] = ccopy[:3]
            del ccopy[:3]
            canvas.setStrokeColor(red)
            canvas.line(lastx*u,lasty*u, x1*u,y1*u)
            canvas.setStrokeColor(green)
            canvas.line(x2*u,y2*u, x3*u,y3*u)
            (lastx,lasty) = (x3,y3)    
    
from reportlab.lib.colors import tan, green

class HandAnnotation(Flowable):
    
    '''A hand flowable.'''
    
    def __init__(self, xoffset=0, size=None, fillcolor=tan, strokecolor=green):
        from reportlab.lib.units import inch
        if size is None: size=4*inch
        self.fillcolor, self.strokecolor = fillcolor, strokecolor
        self.xoffset = xoffset
        self.size = size
        # normal size is 4 inches
        self.scale = size/(4.0*inch)
    
    def wrap(self, *args):
        return (self.xoffset, self.size)
    
    def draw(self):
        canvas = self.canv
        canvas.setLineWidth(6)
        canvas.setFillColor(self.fillcolor)
        canvas.setStrokeColor(self.strokecolor)
        canvas.translate(self.xoffset+self.size,0)
        canvas.rotate(90)
        canvas.scale(self.scale, self.scale)
        hand(canvas, debug=0, fill=1)        
    