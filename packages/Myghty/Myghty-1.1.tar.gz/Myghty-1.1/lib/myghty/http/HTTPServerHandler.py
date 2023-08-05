# $Id: HTTPServerHandler.py 2133 2006-09-06 18:52:56Z dairiki $
# HTTPServerHandler.py - standalone HTTP server for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#

import myghty.interp
import myghty.request
import myghty.resolver
import myghty.exception as exception
from myghty.buffer import LinePrinter
import myghty.http.HTTPHandler as HTTPHandler
import BaseHTTPServer, SocketServer
from myghty.util import *
import os, sys, cgi, re, types, traceback
import mimetypes,posixpath,shutil,urllib


class HTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """main server class.  just overrides the basic webserver."""
    def __init__(self, port = 8000, docroot = None, handlers = None, text_only = True, **params):
        self.params = params
        self.port = port
        self.text_only = text_only
        self.daemon_threads = False
        server_address = ('', port)

        
        if handlers is None:
            handlers = [{r'(.*)':HSHandler(**params)}]

        if docroot is not None:
            if not (isinstance(docroot, types.ListType)):
                handlers.append(docroot)
            else:
                handlers += docroot
            
        self.handlers = OrderedDict(handlers)
            
        BaseHTTPServer.HTTPServer.__init__(self, server_address, HTTPRequestHandler)
        

class HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """request handling for the webserver.  this is the engine of the standalone server."""
    def do_POST(self):
        self.handle_request()
    
    def do_GET(self):
        self.handle_request()

    def handle_request(self):
        httpreq = HSHTTPRequest(self)
    
        try:    
            if (
                self.server.text_only and httpreq.content_type[0:4] != "text"
            ):
                self.serve_file(httpreq)
            else:
                for key in self.server.handlers.keys():
                    match = re.match(key, httpreq.path_info)
                    if match:
                        handler = self.server.handlers[key]
                        if match.lastindex >= 1:
                            httpreq.converted_path_info = match.group(1)
                        else:
                            httpreq.converted_path_info = httpreq.path_info
                            
                        if type(handler) == str:
                            self.serve_file(httpreq)
                        else:
                            handler.handle(httpreq)
                        return
        except:
            traceback.print_exc(file=sys.stdout)
            self.send_error(500, "Server Error")
                

    # methods ripped from SimpleHTTPServer to handle sending binary
    # files, non-myghty files
    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        
        for key in self.server.handlers.keys():
            match = re.match(key, path)
            if match:
                root = self.server.handlers[key]
                if type(root) != str:
                    continue
                if match.lastindex >=1:
                    path = match.group(1)
                break
        else:
            return None

        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = root
        
        for word in words:
            drive, word = posixpath.splitdrive(word)
            head, word = posixpath.split(word)
            if word in (os.curdir, os.pardir): continue
            path = posixpath.join(path, word)
        return path

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using text/plain
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
    '': 'text/html', # Default
    '.myt':'text/html',
    '.myc':'text/html',
    '.py': 'text/plain',
    '.c': 'text/plain',
    '.h': 'text/plain',
    })

    
    def serve_file(self, httpreq):
        ctype = httpreq.content_type
        if ctype.startswith('text/'):
            mode = 'r'
        else:
            mode = 'rb'
        
        path = httpreq.filename
        if path is None:
            self.send_error(404, "File not found")
            return
        try:
            f = open(path, mode)
        except IOError:
            self.send_error(404, "File not found")
            return
        self.send_response(200)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", str(os.fstat(f.fileno())[6]))
        self.end_headers()
        shutil.copyfileobj(f, self.wfile)
        f.close()
        
# now, the myghty stuff.        

def handle(httpreq, interpreter_name = None, **params):
    return HTTPHandler.handle_http(HSHandler, interpreter_name = interpreter_name, httpreq = httpreq, **params)


class HSHandler(HTTPHandler.HTTPHandler):
    def __init__(self, **params):
        HTTPHandler.HTTPHandler.__init__(self, None, LinePrinter(sys.stderr), **params)

    def do_get_init_params(self, httpreq, **params):
        return params
    
    def do_get_resolver(self, **params):
        return HSResolver(**params)
    
    def do_make_request_impl(self, httpreq, **params):
        return HSRequestImpl(httpreq, **params)
        
    def do_get_component(self, httpreq, **params):
        return httpreq.converted_path_info
        
    def do_handle_result(self, httpreq, status, message):
        # in the case that we had an error, do a send_error, which shows the 
        # BaseHTTPServer's error page
        # for codes below 300, do nothing;  this will send no content, unless
        # the application has (as it does for a redirect)
        if status >= 400:
            if message is not None:
                httpreq.handler.send_error(status, message)
            else:
                httpreq.handler.send_error(status)

    def handle(self, httpreq):
        HTTPHandler.HTTPHandler.handle(self, httpreq)


class HSHTTPRequest(HTTPHandler.HTTPRequest):
    def __init__(self, httpreqhandler):
        HTTPHandler.HTTPRequest.__init__(self)

        self.handler = httpreqhandler
        headers = httpreqhandler.headers
        
        for key in headers.keys():
            self.headers_in.add(key, headers[key])
                        
        self.method = httpreqhandler.command
        
        match = re.match(r"([^\?]*)(?:\?(.*))?", httpreqhandler.path)
        if match:
            self.path_info = match.group(1)
            if match.lastindex >=2:
                self.args = match.group(2)
            else:
                self.args = None
        else:
            self.path_info = None
            self.args = None

        self.content_type = self.handler.guess_type(self.path_info)
        self.filename = self.handler.translate_path(self.path_info)
        
        # cobble together a cgi.FieldStorage object from what we have
        
        cgienviron = {
                'QUERY_STRING': self.args,
                'REQUEST_METHOD': self.method,
        }
        
        if self.headers_in.has_key('content-type'):
            cgienviron['CONTENT_TYPE'] = self.headers_in['content-type']
        if self.headers_in.has_key('content-length'):
            cgienviron['CONTENT_LENGTH'] = self.headers_in['content-length']
            
        self.fieldstorage = cgi.FieldStorage(
            fp = self.handler.rfile,
            environ = cgienviron,
            keep_blank_values = True
        )

    def do_send_headers(self):
        self.handler.send_response(self.status)
        headers = self.get_response_headers()
        for key, value in headers.iteritems():
            self.handler.send_header(key, value)

        self.handler.end_headers()

class HSResolver(HTTPHandler.HTTPResolver): pass


class HSWriter(HTTPHandler.HTTPWriter):pass
        

class HSRequestImpl(HTTPHandler.HTTPRequestImpl):
    def __init__(self, httpreq, **params):
        HTTPHandler.HTTPRequestImpl.__init__(self, httpreq, LinePrinter(sys.stderr), LinePrinter(sys.stderr), **params)
        
    def do_make_request_args(self, httpreq, **params):
        return self.request_args_from_fieldstorage(httpreq.fieldstorage)

    def do_get_out_buffer(self, httpreq, out_buffer = None, **params):
        if out_buffer is None:
            return HSWriter(httpreq, httpreq.handler.wfile, **params)
        else:
            return out_buffer



if __name__ == '__main__':
    params = {}
    for item in sys.argv[1:]:
        (key, value) = item.split('=', 1)
        params[key] = eval(value)

    httpd = HTTPServer(**params)
    print "HTTPServer listening on port %d" % httpd.port
    httpd.serve_forever()
 
