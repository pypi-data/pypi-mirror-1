# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__reversion__ = "$Revision: 20 $"
__author__    = "$Author: holtwick $"
__date__      = "$Date: 2007-10-09 12:58:24 +0200 (Di, 09 Okt 2007) $"

from reportlab.lib.units import inch, cm
from reportlab.lib.styles import *
from reportlab.lib.enums import *
from reportlab.lib.colors import *
from reportlab.lib.pagesizes import *
from reportlab.pdfbase import pdfmetrics

# from reportlab.platypus import *
# from reportlab.platypus.flowables import Flowable
# from reportlab.platypus.tableofcontents import TableOfContents
# from reportlab.platypus.para import Para, PageNumberObject, UNDERLINE, HotLink

import reportlab
import copy
import types
import os
import os.path
import pprint
import sys
import string
import re

rgb_re = re.compile("^.*?rgb[(]([0-9]+).*?([0-9]+).*?([0-9]+)[)].*?[ ]*$")

if not(reportlab.Version[0] == "2" and reportlab.Version[2]>="1"):
    raise ImportError("Reportlab Version 2.1+ is needed!")

REPORTLAB22 = (reportlab.Version[0] == "2" and reportlab.Version[2] >= "2")
# print "***", reportlab.Version, REPORTLAB22, reportlab.__file__

import logging
log = logging.getLogger("ho.pisa")


#try:
#    import cStringIO as StringIO
#except:
import StringIO

try:
    import pyPdf
except:
    pyPdf = None

try:
    from reportlab.graphics import renderPM
except:
    renderPM = None

try:
    from reportlab.graphics import renderSVG
except:
    renderSVG = None

def ErrorMsg():
    """
    Helper to get a nice traceback as string
    """
    import traceback, sys, cgi
    type = value = tb = limit = None
    type, value, tb = sys.exc_info()
    list = traceback.format_tb(tb, limit) + traceback.format_exception_only(type, value)
    return "Traceback (innermost last):\n" + "%-20s %s" % (
        string.join(list[:-1], ""),
        list[-1])

def toList(value):
    if type(value) not in (types.ListType, types.TupleType):
        return [value]
    return list(value)

def flatten(x):
    """flatten(sequence) -> list

    copied from http://kogs-www.informatik.uni-hamburg.de/~meine/python_tricks

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def _toColor(arg, default=None):
    '''try to map an arbitrary arg to a color instance'''
    if isinstance(arg, Color): return arg
    tArg = type(arg)
    if tArg in (types.ListType, types.TupleType):
        assert 3<=len(arg)<=4, 'Can only convert 3 and 4 sequences to color'
        assert 0<=min(arg) and max(arg)<=1
        return len(arg)==3 and Color(arg[0], arg[1], arg[2]) or CMYKColor(arg[0], arg[1], arg[2], arg[3])
    elif tArg == types.StringType:
        C = getAllNamedColors()
        s = arg.lower()
        if C.has_key(s): return C[s]
        try:
            return toColor(eval(arg))
        except:
            pass
    try:
        return HexColor(arg)
    except:
        if default is None:
            raise ValueError('Invalid color value %r' % arg)
        return default

# http://www.w3.org/TR/CSS2/ui.html
# http://meyerweb.com/eric/css/tests/css2/sec18-02.htm
_XXX = """
ActiveBorder
    Active window border. 
ActiveCaption
    Active window caption. 
AppWorkspace
    Background color of multiple document interface. 
Background
    Desktop background. 
ButtonFace
    Face color for three-dimensional display elements. 
ButtonHighlight
    Dark shadow for three-dimensional display elements (for edges facing away from the light source). 
ButtonShadow
    Shadow color for three-dimensional display elements. 
ButtonText
    Text on push buttons. 
CaptionText
    Text in caption, size box, and scrollbar arrow box. 
GrayText
    Grayed (disabled) text. This color is set to #000 if the current display driver does not support a solid gray color. 
Highlight
    Item(s) selected in a control. 
HighlightText
    Text of item(s) selected in a control. 
InactiveBorder
    Inactive window border. 
InactiveCaption
    Inactive window caption. 
InactiveCaptionText
    Color of text in an inactive caption. 
InfoBackground
    Background color for tooltip controls. 
InfoText
    Text color for tooltip controls. 
Menu
    Menu background. 
MenuText
    Text in menus. 
Scrollbar
    Scroll bar gray area. 
ThreeDDarkShadow
    Dark shadow for three-dimensional display elements. 
ThreeDFace
    Face color for three-dimensional display elements. 
ThreeDHighlight
    Highlight color for three-dimensional display elements. 
ThreeDLightShadow
    Light color for three-dimensional display elements (for edges facing the light source). 
ThreeDShadow
    Dark shadow for three-dimensional display elements. 
Window
    Window background. 
WindowFrame
    Window frame. 
WindowText
    Text in windows. 
"""
    
def getColor(value, default=None):
    " Convert to color value "
    try:
        original = value
        if isinstance(value, Color):
            return value
        value = str(value).lower()
        if value=="transparent" or value=="none":
            return default
        if value.startswith("#") and len(value)==4:
            value = "#" + value[1] + value[1] + value[2] + value[2] + value[3] + value[3]
        elif rgb_re.search(value):
            # e.g., value = "<css function: rgb(153, 51, 153)>", go figure:
            r, g, b = [int(x) for x in rgb_re.search(value).groups()]
            value = "#%02x%02x%02x" % (r, g, b)
        else:
            # Shrug
            pass

        # XXX Throws illegal in 2.1 e.g. toColor('none'),
        # therefore we have a workaround here
        return _toColor(value)
    except ValueError, e:
        log.warn("Unknown color %r", original)
    return default

def getBorderStyle(value, default=None):
    # log.debug(value)
    if value and (str(value).lower() not in ("none", "hidden")):
        return value
    return default

mm = cm / 10.0
dpi96 = (1.0 / 96.0 * inch)

_absoluteSizeTable = {
    "1": 50.0/100.0,  
    "xx-small": 50.0/100.0,
    "x-small": 50.0/100.0,  
    "2": 75.0/100.0,
    "small": 75.0/100.0, 
    "3": 100.0/100.0,
    "medium": 100.0/100.0,
    "4": 125.0/100.0,
    "large": 125.0/100.0,
    "5": 150.0/100.0,
    "x-large": 150.0/100.0,
    "6": 175.0/100.0,
    "xx-large": 175.0/100.0,
    "7": 200.0/100.0,        
    "xxx-large": 200.0/100.0,    
    #"xx-small" : 3./5.,
    #"x-small": 3./4.,
    #"small": 8./9.,
    #"medium": 1./1.,
    #"large": 6./5.,
    #"x-large": 3./2.,
    #"xx-large": 2./1.,
    #"xxx-large": 3./1.,
}

_relativeSizeTable = {    
    "larger": 1.25,
    "smaller": 0.75,
    "+4": 200.0/100.0,
    "+3": 175.0/100.0,
    "+2": 150.0/100.0,
    "+1": 125.0/100.0,
    "-1": 75.0/100.0,
    "-2": 50.0/100.0,
    "-3": 25.0/100.0,
    }      
     
MIN_FONT_SIZE = 1.0
 
def getSize(value, relative=0, base=None, default=0.0):
    """
    Converts strings to standard sizes
    """
    try:
        original = value
        if value is None:
            return relative
        elif type(value) is types.FloatType:
            return value
        elif type(value) is types.IntType:
            return float(value)
        elif type(value) in (types.TupleType, types.ListType):
            value = "".join(value)
        value = str(value).strip().lower().replace(",", ".")
        if value[-2:]=='cm':
            return float(value[:-2].strip()) * cm
        elif value[-2:]=='mm':
            return (float(value[:-2].strip()) * mm) # 1mm = 0.1cm
        elif value[-2:]=='in':
            return float(value[:-2].strip()) * inch # 1pt == 1/72inch
        elif value[-2:]=='inch':
            return float(value[:-4].strip()) * inch # 1pt == 1/72inch
        elif value[-2:]=='pt':
            return float(value[:-2].strip())
        elif value[-2:]=='pc':
            return float(value[:-2].strip()) * 12.0 # 1pc == 12pt
        elif value[-2:]=='px':
            return float(value[:-2].strip()) * dpi96 # XXX W3C says, use 96pdi http://www.w3.org/TR/CSS21/syndata.html#length-units
        elif value[-1:]=='i':  # 1pt == 1/72inch
            return float(value[:-1].strip()) * inch
        elif value in ("none", "0", "auto"):
            return 0.0       
        elif relative:
            if value[-2:]=='em': # XXX
                return (float(value[:-2].strip()) * relative) # 1em = 1 * fontSize
            elif value[-2:]=='ex': # XXX
                return (float(value[:-2].strip()) * (relative/2.0)) # 1ex = 1/2 fontSize
            elif value[-1:]=='%':
                # print "%", value, relative, (relative * float(value[:-1].strip())) / 100.0
                return (relative * float(value[:-1].strip())) / 100.0 # 1% = (fontSize * 1) / 100
            elif value in ("normal", "inherit"):
                return relative            
            elif _relativeSizeTable.has_key(value):     
                if base:
                    return max(MIN_FONT_SIZE, base * _relativeSizeTable[value])       
                return max(MIN_FONT_SIZE, relative * _relativeSizeTable[value]) 
            elif _absoluteSizeTable.has_key(value):
                if base:
                    return max(MIN_FONT_SIZE, base * _absoluteSizeTable[value])
                return max(MIN_FONT_SIZE, relative * _absoluteSizeTable[value])
        try:
            value = float(value)
        except:
            log.warn("getSize: Not a float %r", value)
            return default #value = 0
        return max(0, value)
    except Exception:
        log.warn("getSize %r %r", original, relative, exc_info=1)
        # print "ERROR getSize", repr(value), repr(value), e
        return default

def getCoords(x, y, w, h, pagesize):
    """
    As a stupid programmer I like to use the upper left
    corner of the document as the 0,0 coords therefore
    we need to do some fancy calculations
    """
    #~ print pagesize
    ax, ay = pagesize
    if x < 0:
        x = ax + x
    if y < 0:
        y = ay + y
    if w != None and h != None:
        if w <= 0:
            w = (ax - x + w)
        if h <= 0:
            h = (ay - y + h)
        return x, (ay - y - h), w, h
    return x, (ay - y)

def getBox(box, pagesize):
    """
    Parse sizes by corners in the form:
    <X-Left> <Y-Upper> <Width> <Height>
    The last to values with negative values are interpreted as offsets form
    the right and lower border.
    """
    box = str(box).split()
    if len(box)!=4:
        raise Exception, "box not defined right way"
    x, y, w, h = map(getSize, box)
    return getCoords(x, y, w, h, pagesize)

def getPos(position, pagesize):
    """
    Pair of coordinates
    """
    position = str(position).split()
    if len(position)!=2:
        raise Exception, "position not defined right way"
    x, y = map(getSize, position)
    return getCoords(x, y, None, None, pagesize)

def getBool(s):
    " Is it a boolean? "
    return str(s).lower() in ("y", "yes", "1", "true")

_uid = 0
def getUID():
    " Unique ID "
    global _uid
    _uid += 1
    return str(_uid)

_alignments = {
    "left": TA_LEFT,
    "center": TA_CENTER,
    "middle": TA_CENTER,
    "right": TA_RIGHT,
    "justify": TA_JUSTIFY,
    }

def getAlign(value, default=TA_LEFT):
    return _alignments.get(str(value).lower(), default)

#def getVAlign(value):
#    # Unused
#    return str(value).upper()

import base64
import re
import urlparse
import mimetypes    
import urllib2

_rx_datauri = re.compile("^data:(?P<mime>[a-z]+/[a-z]+);base64,(?P<data>.*)$", re.M|re.DOTALL)

class pisaFileObject:
    
    """
    XXX
    """
    
    def __init__(self, uri, basepath=None):
               
        self.basepath = basepath
        self.mimetype = None
        self.file = None        
        self.data = None
        self.uri = None
        self.local = None
        uri = str(uri)
    
        # Data URI
        if uri.startswith("data:"):
            m = _rx_datauri.match(uri)
            self.mimetype = m.group("mime")        
            self.data = base64.decodestring(m.group("data"))    

        else:
                       
            # Check if we have an external scheme
            if basepath:
                urlParts = urlparse.urlparse(basepath)
            else:
                urlParts = urlparse.urlparse(uri)
            
            # Drive letters have len==1 but we are looking for things like http:
            if len(urlParts[0])>1:
                
                # External data
                if basepath:
                    uri = urlparse.urljoin(basepath, uri)    
                                                
                #path = urlparse.urlsplit(url)[2]
                #mimetype = getMimeType(path)
                urlResponse = urllib2.urlopen(uri)     
                self.mimetype = urlResponse.info().get("Content-Type", None).split(";")[0] 
                self.uri = urlResponse.geturl()
                self.file = urlResponse
                
            else:
                
                # Local data
                if basepath:
                    uri = os.path.normpath(os.path.join(basepath, uri)) 
                
                if os.path.isfile(uri):
                    self.uri = uri
                    self.local = uri
                    self.setMimeTypeByName(uri)                    
                    self.file = open(uri, "rb")
                    
    def getFile(self):
        if self.file is not None:
            return self.file
        if self.data is not None:
            return StringIO.StringIO(self.data)
        return None
    
    def getData(self):
        if self.data is not None:
            return self.data
        if self.file is not None:
            self.data = self.file.read()
            return self.data
        return None
    
    def notFound(self):
        return (self.file is None) and (self.data is None)
                        
    def setMimeTypeByName(self, name):        
        " Guess the mime type "
        mimetype = mimetypes.guess_type(name)[0]
        if mimetype is not None:
            self.mimetype = mimetypes.guess_type(name)[0].split(";")[0]
        
def getFile(*a , **kw):
    file = pisaFileObject(*a, **kw)
    if file.notFound():
        return None
    return file
