#!/usr/local/bin/python
# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 103 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-31 17:08:54 +0100 (Mi, 31 Okt 2007) $"
__svnid__   = "$Id: pisa.py 103 2007-10-31 16:08:54Z holtwick $"

import sys
import os
import os.path

REQUIRED_INFO = """
EXCEPTION!
%s

The following Python packages are required for PISA:
- ReportlabToolkit 2.1 <http://www.reportlab.org/>
- HTML5lib <http://code.google.com/p/html5lib/>
- TG W3C CSS (included in PISA)

Optional packages:
- pyPDF <http://pybrary.net/pyPdf/>
- PIL <http://www.pythonware.com/products/pil/>
""".strip()    

try:  
    import reportlab
    import html5lib    
    # import pyPdf
    import sx.pisa3 as pisa    
    pisa.command()
except ImportError, e:
    print REQUIRED_INFO % e
    