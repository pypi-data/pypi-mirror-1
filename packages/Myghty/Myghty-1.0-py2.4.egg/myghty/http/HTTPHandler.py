# $Id: HTTPHandler.py 2028 2006-01-16 23:39:04Z zzzeek $
# generic HTTP handler library for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#

import myghty.buffer
import types, string, re, sys
import myghty.resolver
import myghty.interp
from myghty.util import *
import myghty.session as session
import myghty.exception as exception

__all__ = ['HTTPHandler', 'HeaderTable', 'HTTPRequest', 'HTTPWriter', 'HTTPResolver', 'handle_http']

handlers = {}

def handle_http(handlerclass, interpreter_name = None, interp = None, request_impl = None, component = None, **params):
    """handles an HTTP request using the named HTTPHandler instance.  if an instance of the name does not
    exist, it is created using the given configuration parameters.  
    
    implementing modules should define their own handle() method that calls this one
    with the appropriate arguments."""
    return get_handler(handlerclass, interpreter_name, **params).handle(interp = interp, request_impl = request_impl, component = component, **params)

def get_handler(handlerclass, interpreter_name = None, **params):
    """returns an HTTPHandler instance keyed off the given name.  if the named instance does not exist,
    it is created using the given configuration parameters."""
    interpreter_name = handlerclass.__name__ + "_" + (interpreter_name or 'main')
    try:
        handler = handlers[interpreter_name]
    except KeyError:
        handler = handlerclass(**params)
        handlers[interpreter_name] = handler

    return handler

class HTTPHandler:
    """entry point for HTTP requests, configures and maintains a reference to 
    an instance of a Myghty intepreter, and
    serves as a factory for many of the
    other implementing objects in this module.   override the do_*** methods of 
    this class, and call the handle() method inside the
    the request-handling point of the implementing environment."""
    
    def __init__(self, httpreq, logbuffer, **params):
        self.params = self._init_params(httpreq, logbuffer, **params)
        self.interp = myghty.interp.Interpreter(**self.params)

    def _init_params(self, httpreq, logbuffer, **params):
        params = self.do_get_init_params(httpreq, **params)

        if not params.has_key('allow_globals'):
            params['allow_globals'] = []

        params['allow_globals'].append('r')

        if params.setdefault('use_session', False):
            params['allow_globals'].append('s')

        debug_elements = params.setdefault('debug_elements', [])

        # deprecated
        if params.setdefault('log_component_loading', False):
            debug_elements.append('classloading')

        # deprecated
        if params.setdefault('log_cache_operations', False):
            debug_elements.append('cache')

        if len(debug_elements) > 0 and not params.has_key('debug_file'):
            params['debug_file'] = logbuffer
            
        if not params.has_key('resolver'):
            d = dict(params)
            if d.has_key('debug_file'): del d['debug_file']
            params['resolver'] = self.do_get_resolver(debug_file = None, **d)

        if not params.has_key('data_dir'):
            raise exception.ConfigurationError("data_dir config is required")

        if not params.has_key('component_root') and not params.has_key('module_components') and not params.has_key('resolver_strategy') and not params.has_key('module_root'):
            raise exception.ConfigurationError("No file resolution rules detected - component_root, module_components, and/or resolver_strategy")

        return params
    
    def do_get_init_params(self, httpreq, **params):raise NotImplementedError()
    
    def do_get_resolver(self, **params):raise NotImplementedError()
    
    def do_make_request_impl(self, httpreq, **params):raise NotImplementedError()
    
    def do_get_component(self, httpreq, **params):raise NotImplementedError()
    
    def do_handle_result(self, httpreq, status_code, reason):
        """called at the end of the request.  in a normal response, headers and probably
        content have already been sent.  in the case of errors or redirects, this method
        should insure that headers have been properly sent as required by the environment.
        in all cases, appropriate return data should be returned from this method which will 
        be returned to the calling environment."""
        raise NotImplementedError()
    
    def handle(self, httpreq, interp = None, request_impl = None, component = None, **params):
        """handles an HTTP request.  implementing classes may want to override this
        to provide environment-specific request arguments that are then translated into the implementing
        module's own HTTPRequest implementation.

        httpreq - HTTPRequest request object or compatible interface
        interp - optional Interpreter object to override the default
        request_impl - optional RequestImpl object the default
        component - optional Component object or request path to serve
        **params - configuration parameters which override the default parameters
        """

        if interp is None:
            interp = self.interp
    
        implparams  = self.params.copy()
        implparams.update(params)
    
        if not request_impl:
            request_impl = self.do_make_request_impl(httpreq, **implparams)
            
        if not component:
            if implparams.has_key('component'):
                component = implparams['component']
            else:
                component = self.do_get_component(httpreq, **implparams)
                
        reason = None
        request = interp.make_request(component = component, request_impl = request_impl, **params)
    
        try:
            request.execute()
            ret = HTTP_OK
        except IOError:
            ret = HTTP_OK
        except exception.Abort, e:
            ret = e.aborted_value
            reason = e.reason
        except exception.TopLevelNotFound:
            ret = HTTP_NOT_FOUND
        except exception.ServerError:
            ret = HTTP_INTERNAL_SERVER_ERROR
    
        httpreq.status = ret
        
        return self.do_handle_result(httpreq, ret, reason)


class HTTPRequestImpl(myghty.request.AbstractRequestImpl):
    """subclasses the myghty AbstractRequestImpl class, to provide the connector between 
    the "real" http request (HTTPRequest) and the Myghty request (Request).
    
    this class is responsible for setting up the resources needed by Request, including 
    the output buffer, session, request arguments (usually via a FieldStorage type API),
    sending redirects and handling errors and other exceptions.
    """
    
    def __init__(self, httpreq, logger, errorlogger, 
        request_args = None,
        use_session = False, 
        global_args = None, 
        log_errors = False, output_errors = True, error_handler=None, **params):

        self.httpreq = httpreq
        
        if request_args is None:
            request_args = self.do_make_request_args(httpreq, **params)

        self.request_args = request_args
        
        if not global_args is None:
            # copy the global_args in case they are synonymous with those 
            # given to the interpreter
            self.global_args = global_args.copy()
        else:
            self.global_args = {}

        self.global_args['r'] = self.httpreq

        self.session_args = session.MyghtySessionArgs(**params)

        self.error_handler = error_handler

        self.use_session = use_session
        if self.use_session:
            self.global_args['s'] = self.get_session()

        self.log_errors = log_errors
        self.output_errors = output_errors
        self.logger = logger
        self.errorlogger = errorlogger

        self.out_buffer = self.do_get_out_buffer(httpreq, **params)

    buffer = property(lambda self:self.out_buffer)
    
    def do_make_request_args(self, httpreq, **params):raise NotImplementedError()

    def do_get_out_buffer(self, httpreq, out_buffer = None, **params):raise NotImplementedError()

    def log(self, message):
        self.logger.write(message)
        
    def request_args_from_fieldstorage(self, fields):
        """based on FieldStorage request information, returns a dict of key values, where the values are
        one of:  a string, a list of strings, a Field object with an upload value, a list of
        Field objects with upload values."""

        def formatfield(field):
            if type(field) == types.ListType:
                return map(formatfield, field)
            elif not field.file:
                return field.value
            else:
                return field

        request_args = {}
        
        if fields.file:
            request_args['_file'] = fields.file
        elif fields.list:
            for key in fields.keys():
                request_args[key] = formatfield(fields[key])
        return request_args
        
    def get_session(self, **params):
        if not hasattr(self, 'session'):
            self.session = self.session_args.get_session(self.httpreq, **params)
            
        return self.session
        
    def handle_error(self, error, m, **params):
        if self._run_error_handler(self.error_handler, self.errorlogger, error, m, r = self.httpreq, **params): return

        if isinstance(error, exception.TopLevelNotFound):
            if not error.silent:
                self.errorlogger.write(error.singlelineformat())
            raise error
        else:
            if self.log_errors:
                self.errorlogger.writelines(string.split(error.format(), "\n"))
            else:
                self.errorlogger.write(error.singlelineformat())

            if self.output_errors:
                self.httpreq.content_type = "text/html"
                self.out_buffer.write(error.htmlformat())
                #self.out_buffer.write(error.textformat())
            else:
                raise exception.ServerError(wrapped = error)

        
    def send_redirect(self, path):
        self.httpreq.err_headers_out["Location"] = path
        self.httpreq.content_type = "text/html"
        self.httpreq.status = 302
        self.out_buffer.write('<p>The document has moved'
                  ' <a href="%s">here</a></p>\n'
                  % path)
        raise exception.Redirected(path, 302)

    def send_abort(self, ret, reason):
        raise exception.Abort(ret, reason)
        

    def clone(self, **params):
        # quick shallow copy cloner.  constructor clone doesnt
        # really work in a superclass.  
        # override this if a more complex clone is needed
        cloner = ConstructorClone(self, **params)
        impl = cloner.copyclone()
        return impl
    

class HeaderTable(OrderedDict):
    """a dictionary for storing HTTP headers, works similarly to the table object
    in mod_python."""
    
    def add(self, key, value):
        if self.has_key(key):
            list = self[key]
            if type(list) != types.ListType:
                list = [list]
                self[key] = list
            list.append(value)
        else:
            self[key] = value
    
    def __getitem__(self, key):
        return OrderedDict.__getitem__(self, string.lower(key))

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, string.lower(key), value)


    def has_headers(self):
        return len(self) > 0
        
    def get_output(self, buffer):
        for key, value in self.iteritems():
            key = re.sub('_', '-', key)
            if type(value) == types.StringType:
                buffer.write("%s: %s\n" % (key, value))
            else:
                for v in value:
                    buffer.write("%s: %s\n" % (key, v))


class HTTPResolver(myghty.resolver.FileResolver):
    """a subclass of the FileResolver, which can have HTTP-environment-specific
    functionality attached to it if desired."""
    pass
        
class HTTPRequest(object):
    """represents the actual HTTP request.  implementations have to provide this
    object's implementation.  in the case of mod_python, the actual mod_python
    request object is used instead of this one.  the interface should have a 
    compatible subset of the mod_python apache request object's attributes as follows:

    # set up by the base class __init__ method  
    headers_in
    err_headers_out
    headers_out
    status
    headers_sent = False

    # should be added by the implementing __init__ method
    method
    content_type

    # not as required, but preferred:
    path_info
    args
    filename
    
    # required method is:
    do_send_headers()
    
    the headers attributes should use the HeaderTable class to implement.   
    """ 

    def __init__(self):
        self.headers_in = HeaderTable()
        self.headers_out = HeaderTable()
        self.err_headers_out = HeaderTable()
        self.status = HTTP_OK
        self.headers_sent = False
        

    def send_http_header(self):
        if not self.headers_sent:
            self.headers_sent = True
            self.do_send_headers()
            
    def do_send_headers(self):raise NotImplementedError()
    
    def get_response_headers(self):
        if len(self.err_headers_out):
            self.err_headers_out['content-type'] = self.content_type
            return self.err_headers_out
        else:
            self.headers_out['content-type'] = self.content_type
            return self.headers_out
    

class HTTPWriter(myghty.buffer.BufferDecorator):
    """subclasses BufferDecorator to provide the output stream for the response.  

    also calls send_http_header() off of the request at the moment content is first
    sent.
    """

    def __init__(self, httpreq, out_buffer, *args, **params):
        myghty.buffer.BufferDecorator.__init__(self, out_buffer)
        self.httpreq = httpreq
        self.headers_sent = False

    def send_headers(self):
        if not self.headers_sent:
            self.headers_sent = True
            self.httpreq.send_http_header()
            

    def write(self, text):
        if not self.headers_sent:
            self.send_headers()
        self.buffer.write(text)

    def writelines(self, lines):
        if not self.headers_sent:
            self.send_headers()
        self.buffer.writelines(lines)




# what HTTP thingamabob is complete without the HTTP status codes
# defined somewhere
HTTP_CONTINUE                     = 100
HTTP_SWITCHING_PROTOCOLS          = 101
HTTP_PROCESSING                   = 102
HTTP_OK                           = 200
HTTP_CREATED                      = 201
HTTP_ACCEPTED                     = 202
HTTP_NON_AUTHORITATIVE            = 203
HTTP_NO_CONTENT                   = 204
HTTP_RESET_CONTENT                = 205
HTTP_PARTIAL_CONTENT              = 206
HTTP_MULTI_STATUS                 = 207
HTTP_MULTIPLE_CHOICES             = 300
HTTP_MOVED_PERMANENTLY            = 301
HTTP_MOVED_TEMPORARILY            = 302
HTTP_SEE_OTHER                    = 303
HTTP_NOT_MODIFIED                 = 304
HTTP_USE_PROXY                    = 305
HTTP_TEMPORARY_REDIRECT           = 307
HTTP_BAD_REQUEST                  = 400
HTTP_UNAUTHORIZED                 = 401
HTTP_PAYMENT_REQUIRED             = 402
HTTP_FORBIDDEN                    = 403
HTTP_NOT_FOUND                    = 404
HTTP_METHOD_NOT_ALLOWED           = 405
HTTP_NOT_ACCEPTABLE               = 406
HTTP_PROXY_AUTHENTICATION_REQUIRED= 407
HTTP_REQUEST_TIME_OUT             = 408
HTTP_CONFLICT                     = 409
HTTP_GONE                         = 410
HTTP_LENGTH_REQUIRED              = 411
HTTP_PRECONDITION_FAILED          = 412
HTTP_REQUEST_ENTITY_TOO_LARGE     = 413
HTTP_REQUEST_URI_TOO_LARGE        = 414
HTTP_UNSUPPORTED_MEDIA_TYPE       = 415
HTTP_RANGE_NOT_SATISFIABLE        = 416
HTTP_EXPECTATION_FAILED           = 417
HTTP_UNPROCESSABLE_ENTITY         = 422
HTTP_LOCKED                       = 423
HTTP_FAILED_DEPENDENCY            = 424
HTTP_INTERNAL_SERVER_ERROR        = 500
HTTP_NOT_IMPLEMENTED              = 501
HTTP_BAD_GATEWAY                  = 502
HTTP_SERVICE_UNAVAILABLE          = 503
HTTP_GATEWAY_TIME_OUT             = 504
HTTP_VERSION_NOT_SUPPORTED        = 505
HTTP_VARIANT_ALSO_VARIES          = 506
HTTP_INSUFFICIENT_STORAGE         = 507
HTTP_NOT_EXTENDED                 = 510

