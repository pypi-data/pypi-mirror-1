# $Id: ApacheHandler.py 2028 2006-01-16 23:39:04Z zzzeek $
# ApacheHandler.py - handles apache requests for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#

from mod_python import apache
from mod_python import util as mputil
import myghty.exception as exception
import myghty.buffer
import re,string, types, time
from myghty.util import *
from myghty.resolver import *
import myghty.http.HTTPHandler as HTTPHandler

def handle(httpreq, interpreter_name = None, **params):
    return get_handler(httpreq, interpreter_name, **params).handle(httpreq = httpreq, **params)

def get_handler(httpreq, interpreter_name = None, **params):
    if interpreter_name is None:
        try:
            interpreter_name = httpreq.get_options()['MyghtyInterpreterName']
        except KeyError:
            pass
    return HTTPHandler.get_handler(ApacheHandler, httpreq = httpreq, interpreter_name = interpreter_name, **params)

class ApacheHandler(HTTPHandler.HTTPHandler):
    def __init__(self, httpreq, **params):
        HTTPHandler.HTTPHandler.__init__(self, httpreq, LogBuffer(httpreq.server), **params)

    def do_handle_result(self, httpreq, status_code, reason):
        httpreq.status = HTTPHandler.HTTP_OK
        if status_code == HTTPHandler.HTTP_OK:
            return apache.OK
        else:
            return status_code

    def do_get_init_params(self, httpreq, **params):
        table = httpreq.get_options()
        
        options = params.copy()
        for key in table.keys():
            match = re.match("^Myghty(.*)$", key)
            if not match: continue
            param = match.group(1)
            param = string.lower(re.sub(r"(\w)([A-Z])", r"\1_\2", param))
            if not options.has_key(param):
                options[param] = eval(table[key])
            
        return options
    
    def do_make_request_impl(self, httpreq, **params):
        httpreq.add_common_vars()
        return ApacheRequestImpl(httpreq, **params)

    def do_get_resolver(self, **params):
        return ApacheResolver(**params)
    
    def do_get_component(self, httpreq, **params):
        return httpreq.uri
        
            


class LogBuffer(object):
    def __init__(self, server, retcode = apache.APLOG_NOTICE):
        self.server = server
        self.retcode = retcode

    def write(self, s):
        apache.log_error(string.rstrip(s), self.retcode, self.server)

    def writelines(self, list):
        for line in list:
            apache.log_error(string.rstrip(line), self.retcode, self.server)

    def flush(self):
        pass

class ApacheBuffer(HTTPHandler.HTTPWriter):

    def send_headers(self):
        if self.headers_sent:
            return

        self.headers_sent = True

        if not self.httpreq._content_type_set:
            self.httpreq.content_type = 'text/html'

        # this method is only documented in mod py 2.7
        # (where its needed) but seems harmless though useless
        # to use in mod py 3.0 as well
        self.httpreq.send_http_header()


    def writelines(self, list):
        for line in list:
            self.write(line + "\n")

        def flush(self):pass

class ApacheResolver(HTTPHandler.HTTPResolver):pass

class ApacheRequestImpl(HTTPHandler.HTTPRequestImpl):
    def __init__(self, httpreq, use_modpython_session = False, **params):

        self.use_modpython_session = use_modpython_session

        HTTPHandler.HTTPRequestImpl.__init__(self, httpreq, LogBuffer(httpreq.server),
            LogBuffer(httpreq.server, apache.APLOG_ERR), **params)
        
        
    def get_session(self, **params):
        if not hasattr(self, 'session'):
            if self.use_modpython_session:
                import mod_python.Session
                self.session = mod_python.Session.Session(timeout = self.session_args.timeout)
            else:
                self.session = self.session_args.get_session(self.httpreq, **params)
            
        return self.session

    def do_get_out_buffer(self, httpreq, out_buffer = None, **params):
        if out_buffer is None:
            out_buffer = httpreq
            
        return ApacheBuffer(httpreq, out_buffer = out_buffer, **params)

    def do_make_request_args(self, httpreq, **params):
        """given a mod_python request, returns a real dict of key values, where the values are
        one of:  a string, a list of strings, a Field object with an upload value, a list of
        Field objects with upload values."""

        def formatfield(field):
            if type(field) == types.ListType:
                return map(formatfield, field)
            elif isinstance(field, mputil.Field):
                return field
            else:
                return str(field)

        request_args = {}
        fields = mputil.FieldStorage(httpreq, keep_blank_values = True)
        for key in fields.keys():
            request_args[key] = formatfield(fields[key])
        return request_args
        



