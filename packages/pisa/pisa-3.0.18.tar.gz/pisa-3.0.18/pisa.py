#!/usr/local/bin/python
# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2007 ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 164 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2008-03-12 19:37:21 +0100 (Mi, 12 Mrz 2008) $"
__svnid__   = "$Id: pisa.py 164 2008-03-12 18:37:21Z holtwick $"

import sys
import os
import os.path

try:
    from sitecustomize import *
except:
    pass

REQUIRED_INFO = """
****************************************************
IMPORT ERROR!
%s
****************************************************

The following Python packages are required for PISA:
- ReportlabToolkit>=2.1 <http://www.reportlab.org/>
- HTML5lib <http://code.google.com/p/html5lib/>

Optional packages:
- pyPDF <http://pybrary.net/pyPdf/>
- PIL <http://www.pythonware.com/products/pil/>
""".strip()

try:
    import ho.pisa as pisa
    pisa.command()
except ImportError, e:
    print REQUIRED_INFO % e
