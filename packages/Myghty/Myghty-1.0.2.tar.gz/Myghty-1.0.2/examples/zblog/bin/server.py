#!/usr/local/bin/python

"""myghty HTTPServerHandler runner."""

import myghty.http.HTTPServerHandler as HTTPServerHandler
import sys, os, re
from myghty.resolver import *

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, os.path.join(root, 'lib'))

interpreter_config = {
    'root' : root
}
execfile(os.path.join(root, 'config/server_config.py'), globals(), interpreter_config)
interp = HTTPServerHandler.HSHandler(**interpreter_config)

port = 8080
httpd = HTTPServerHandler.HTTPServer(
    port = port,
    
    handlers = [
        {r'.*(?:/|\.myt)$' : interp},
    ],

    docroot = [{'.*' : os.path.join(root, 'htdocs')}],
    
)       
        
print "Listening on port %d" % port
httpd.serve_forever()

