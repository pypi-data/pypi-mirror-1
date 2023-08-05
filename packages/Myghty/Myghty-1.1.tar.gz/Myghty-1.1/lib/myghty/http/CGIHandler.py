# $Id: CGIHandler.py 2028 2006-01-16 23:39:04Z zzzeek $
# CGIHandler.py - handles cgi requests for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#

import myghty.interp
import myghty.request
import myghty.resolver
import myghty.session as session
import myghty.exception as exception
import myghty.http.HTTPHandler as HTTPHandler
from myghty.util import *
import os, sys, cgi


def handle(*args, **params):
    return HTTPHandler.handle_http(CGIHandler, *args, **params)

def get_handler(interpreter_name = None, **params):
        return HTTPHandler.get_handler(CGIHandler, interpreter_name = interpreter_name, **params)

class CGIHandler(HTTPHandler.HTTPHandler):

    def __init__(self, **params):
        HTTPHandler.HTTPHandler.__init__(self, None, sys.stderr, **params)

    def do_get_init_params(self, httpreq, **params):
        return params
    
    def do_get_resolver(self, **params):
        return CGIResolver(**params)
    
    def do_make_request_impl(self, httpreq, **params):
        return CGIRequestImpl(httpreq, **params)
        
    def do_get_component(self, httpreq, **params):
        return httpreq.path_info
        
    def do_handle_result(self, httpreq, status_code, reason):
        httpreq.send_http_header()
        if status_code != HTTPHandler.HTTP_OK:
            sys.stdout.write("""
                <html>
                <body>
                <b>Response code %d (%s)</b><br/>
                Page: "%s"
                </body>
                </html>
                """  % (status_code, reason or "no message", httpreq.path_info))


    def handle(self, httpreq = None, interp = None, request_impl = None, component = None, **params):
        if httpreq is None:
            httpreq = CGIHTTPRequest()
            
        HTTPHandler.HTTPHandler.handle(self, httpreq, interp, request_impl, component, **params)

class CGIHTTPRequest(HTTPHandler.HTTPRequest):
    """simulates a mod_python request for use in non-mod-python applications.
    only a minimal featureset is here currently.
    """
    def __init__(self):
        HTTPHandler.HTTPRequest.__init__(self)

        self.fieldstorage = cgi.FieldStorage(keep_blank_values = True)

        env = os.environ
        for key in env.keys():
            if key[0:4] == 'HTTP':
                self.headers_in.add(key[5:], env[key])
                        
        self.content_type = 'text/html'
        self.method = env['REQUEST_METHOD']
        self.filename = env['PATH_TRANSLATED']
        self.args = env.get('QUERY_STRING', None)
        self.path_info = env.get('PATH_INFO', '/')
        self.out_buffer = sys.stdout
        
    def do_send_headers(self):
        headers = self.get_response_headers()
        headers.get_output(self.out_buffer)
        self.out_buffer.write("\n")



class CGIResolver(HTTPHandler.HTTPResolver):pass

class CGIWriter(HTTPHandler.HTTPWriter):pass
        

class CGIRequestImpl(HTTPHandler.HTTPRequestImpl):
    def __init__(self, httpreq, **params):
        HTTPHandler.HTTPRequestImpl.__init__(self, httpreq, sys.stderr, sys.stderr, **params)

    def do_get_out_buffer(self, httpreq, out_buffer = None, **params):
        if out_buffer is not None:
            return CGIWriter(httpreq, out_buffer)
        else:
            return CGIWriter(httpreq, httpreq.out_buffer)

    def do_make_request_args(self, httpreq, **params):
        return self.request_args_from_fieldstorage(httpreq.fieldstorage)


