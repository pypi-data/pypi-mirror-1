#!/bin/python2.5
# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 103 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-31 17:08:54 +0100 (Mi, 31 Okt 2007) $"
__svnid__   = "$Id: pisa.py 103 2007-10-31 16:08:54Z holtwick $"

from wsgiref.simple_server import make_server
import logging

import sx.pisa3.pisa_wsgi as pisa_wsgi

def SimpleApp(environ, start_response):
    
    # That's the magic!
    #
    # Set the environment variable "pisa.topdf" to the filename
    # you would like to have for the resulting PDF 
    environ["pisa.topdf"] = "index.pdf"
    
    # Simple Hello World example
    start_response(
        '200 OK', [
        ('content-type', "text/html"),
        ])
    return ["Hello <strong>World</strong>"]

if __name__ == '__main__':

    HOST = ''
    PORT = 8080
    logging.basicConfig(level=logging.DEBUG)
    
    app = SimpleApp
    
    # Add PISA WSGI Middleware  
    app = pisa_wsgi.PisaMiddleware(app)
    
    httpd = make_server(HOST, PORT, app)
    print "Serving HTTP on port %d..." % PORT
    httpd.serve_forever()
