# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick            ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 194 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2008-04-18 18:59:53 +0200 (Fr, 18 Apr 2008) $"

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.platypus import Frame

import ho.pisa as pisa

def test(filename):

    # Convert HTML to "Reportlab Story" structure
    story = pisa.pisaStory("""
    <h1>Sample</h1>
    <p>Hello <b>World</b>!</p>
    """ * 20).story

    # Draw to Canvas
    c = Canvas(filename)
    f = Frame(inch, inch, 6*inch, 9*inch, showBoundary=1)
    f.addFromList(story,c)
    c.save()

    # Show PDF
    pisa.startViewer(filename)

if __name__=="__main__":
    test('story2canvas.pdf')
