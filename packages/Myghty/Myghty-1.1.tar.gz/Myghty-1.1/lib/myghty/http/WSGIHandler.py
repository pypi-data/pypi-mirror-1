# $Id: WSGIHandler.py 2133 2006-09-06 18:52:56Z dairiki $
# WSGIHandler.py - handles WSGI requests for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#


import myghty.interp
import myghty.request
import myghty.resolver
import myghty.buffer
import myghty.escapes as escapes
import myghty.session as session
import myghty.exception as exception
import myghty.http.HTTPHandler as HTTPHandler
import myghty.http.HTTPHandler as http
from myghty.util import *
import os, sys, cgi


def handle(environ, start_response, **params):
    return HTTPHandler.handle_http(WSGIHandler, environ = environ, start_response = start_response, **params)

def get_handler(interpreter_name = None, **params):
    return HTTPHandler.get_handler(WSGIHandler, interpreter_name = interpreter_name, **params)

def application(environ, start_response):
    return get_handler(**environ.get('myghty.application', {})).handle(environ, start_response, **environ.get('myghty.request', {}))

class WSGIHandler(HTTPHandler.HTTPHandler):
    def __init__(self, **params):
        HTTPHandler.HTTPHandler.__init__(self, None, myghty.buffer.LinePrinter(sys.stderr), **params)

    def do_get_init_params(self, httpreq, **params):
        return params
    
    def do_get_resolver(self, **params):
        return WSGIResolver(**params)
    
    def do_make_request_impl(self, httpreq, **params):
        return WSGIRequestImpl(httpreq, **params)
        
    def do_get_component(self, httpreq, **params):
        return httpreq.path_info
        
    def do_handle_result(self, httpreq, status_code, reason):
        httpreq.status = status_code
        httpreq.status_message = reason
        httpreq.send_http_header()
        return [httpreq.out_buffer.getvalue()]


    def handle(self, environ, start_response, httpreq = None, interp = None, request_impl = None, component = None, **params):
        if httpreq is None:
            httpreq = WSGIRequest(environ, start_response)

        return HTTPHandler.HTTPHandler.handle(self, httpreq, interp, request_impl, component, **params)


class WSGIRequest(HTTPHandler.HTTPRequest):
    def __init__(self, environ, start_response):
        HTTPHandler.HTTPRequest.__init__(self)
        
        self.start_response = start_response
        self.environ = environ

        for key in environ.keys():
            if key[0:4] == 'HTTP':
                self.headers_in.add(key[5:], environ[key])
                        
        self.content_type = 'text/html'
        self.method = environ['REQUEST_METHOD']
        self.path_info = environ.get('PATH_INFO', '/')
        self.args = environ.get('QUERY_STRING', None)
        self.status_message = None
        self.filename = environ.get('PATH_TRANSLATED', None)

        self.out_buffer = StringIO()
        
        self.fieldstorage = cgi.FieldStorage(
            fp = environ['wsgi.input'],
            environ = environ,
            keep_blank_values = True
        )

    def do_send_headers(self):
        headers = [(key, value) for key, value in self.get_response_headers().iteritems()]
        if self.status_message is None:
            reason = "HTTP return code"
        else:
            reason = self.status_message
        self.start_response(str(self.status) + " " + reason, headers)
        
        
class WSGIResolver(HTTPHandler.HTTPResolver): pass


class WSGIWriter(HTTPHandler.HTTPWriter):pass
        

class WSGIRequestImpl(HTTPHandler.HTTPRequestImpl):
    def __init__(self, httpreq, **params):
        logger = myghty.buffer.LinePrinter(httpreq.environ['wsgi.errors'])
        HTTPHandler.HTTPRequestImpl.__init__(self, httpreq, logger, logger, **params)
        
    def do_make_request_args(self, httpreq, **params):
        return self.request_args_from_fieldstorage(httpreq.fieldstorage)

    def do_get_out_buffer(self, httpreq, out_buffer = None, **params):
        if out_buffer is None:
            return WSGIWriter(httpreq, httpreq.out_buffer)
        else:
            return WSGIWriter(httpreq, out_buffer)


 
