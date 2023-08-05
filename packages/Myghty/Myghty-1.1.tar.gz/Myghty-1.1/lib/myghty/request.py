# $Id: request.py 2133 2006-09-06 18:52:56Z dairiki $
# request.py - handles component calls for Myghty templates
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
# Original Perl code and documentation copyright (c) 1998-2003 by Jonathan Swartz.
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
"""The request package and its primary class, Request, provide the "m" object in Myghty templates.
The Request is instantiated by the Interpreter and handles component execution state as well
as buffered state.
It provides the interface to all actions taken by components, such as writing output,
calling other components, calling subrequests, and controllling request state.  Also
provides the programmatic interface to key objects such as caches and sessions.
"""

from myghty.util import *
import myghty.buffer
from myghty import exception
import sys, string, re, StringIO, types, os, time, warnings
import posixpath as unixpath
from myghty.container import CreationAbortedError
import myghty.escapes as escapes
import myghty.csource as csource
from myghty.requestbuffer import UnicodeRequestBuffer, StrRequestBuffer

DEFAULT_OUTPUT_ENCODING = sys.getdefaultencoding()
DEFAULT_ENCODING_ERRORS = 'strict'

# current instance of Request for this thread. 
# this is flaky as the request module seems to get reimported when it is
# first imported within a generated component
reqinstance = ThreadLocal()

__all__ = ['Request', 'instance', 'threadlocal']
class Request(object):

    """request object, calls components and directs output.  also is the 
    primary programmatic interface presented to a template's environment."""

    def __init__(self,
        interpreter,
        component = None,
        request_impl = None,
        max_recursion = 32,
        auto_flush = False,
        use_dhandlers = True,
        dont_auto_flush_filters = False,
        resolver_context = 'request',
        parent_request = None,
        request_depth = 0,
        request_path = None,
        raise_error = False,
        disable_wrapping = False,
        output_encoding = DEFAULT_OUTPUT_ENCODING,
        encoding_errors = DEFAULT_ENCODING_ERRORS,
        disable_unicode = False,
        **params
        ):
        """init is called internally by the Interpreter."""
        
        self.component = component
        self.auto_flush = auto_flush
        self.executed = False
        self.interpreter = interpreter
        self.execution_stack = []
        self.max_recursion = max_recursion
        self.dont_auto_flush_filters = dont_auto_flush_filters
        self.use_dhandlers = use_dhandlers
        self.disable_wrapping = disable_wrapping
        self.raise_error = raise_error
        self.parent_request = parent_request

        self._attributes = {}

        self.request_depth = request_depth
        
        self.current_csource = None

        self.starttime = time.time()

        self.comphash = {}
        self.compcaches = {}

        self.request_path = request_path

        self.resolver_context = resolver_context
        
        if parent_request is not None:
            self.root_request = parent_request.root_request
            self.declined_components = parent_request.declined_components
            self.dhandler_path = parent_request.dhandler_path
        else:
            self.declined_components = {}
            self.root_request = self
            self.dhandler_path = None

        if request_impl:
            self.request_impl = request_impl
        else:
            self.request_impl = DefaultRequestImpl(**params)

        self.buffer = None
        self.__output_encoding = output_encoding, encoding_errors
        self.disable_unicode = bool(disable_unicode)
        
    notes = property(lambda self: self.attributes, doc="""A synonym for m.attributes""")

    root_request_path = property(lambda self:self.root_request.request_path, doc="""\
    The URI sent to the ultimate root request of this Request.
    """)
    root_request_args = property(lambda self:self.root_request.request_args, doc="""\
    The request argument dictionary sent to the ultimate root request of this Request.
    """)

    def _parentattr(self):
        if self.parent_request is not None:
            return self.parent_request.attributes
        else:
            return None

    attributes = property(lambda self:InheritedDict(self._attributes, lambda: self._parentattr()), doc="""\
    A dictionary where arbitrary attributes can be stored and retrieved.  Inherits data from its 
    parent request, if any.
    """)
            
    def is_subrequest(self):
        """returns True if this request is a subrequest."""
        return self.parent_request is not None
        
    def clone(self, **params):
        """creates a copy of this Request.  Normally used to create subrequests."""
        if not params.has_key('request_impl'):
            params['request_impl'] = self.request_impl.clone(**params)
        clone = ConstructorClone(self, **params)
        return clone.clone()
        
    
    class StackFrame:
        """data object representing the currently executing component context.
        
        gets pushed and popped to/from the execution_stack instance variable.
        """
        
        def __init__(self, request, component, args, base_component, content, is_call_self):
            self.component = component
            self.args = args
            self.base_component = base_component
            self.content = content
            self.is_call_self = is_call_self
            self.content_args = None
        
            # set up an indirect filter function that is passed to output
            # buffers, etc.  allows the filtering function can be dynamically 
            # reset to a no-op, in the case that the component calls call_self
            # or cache_self, which should disable the final output filtering
            if isinstance(component, myghty.component.Component) and component.has_filter():
                def filt(f):
                    return component.filter(f, m = request, ARGS = args, **request.global_args)
                self._filter = filt
                self.filter = lambda f: self._filter(f)
        
            
        def reset_filter(self):
            self._filter = lambda f: f

    def out(self, string):
        """a synonym for write"""
        self.write(string)
    
    def write(self, string):
        """writes textual content to the current output buffer."""
        self.buffer.write(string)
        
    def flush_buffer(self):
        """flushes the current output buffer to its destination."""
        self.buffer.flush()

    def clear_buffer(self):
        """clears all content from the current output buffer."""
        self.buffer.clear()

    def execute(self):
        """executes this request after constructed.  This is the first method called,
        and can only be called once per request."""
        if self.executed:
            self._raise_error("Can only call execute() once per request")
        self.executed = True
        if reqinstance.exists():
            existing_request = reqinstance.get()
        else:
            existing_request = None
        reqinstance.put(self)

        # Divert python warnings to log file
        saved_showwarning = warnings.showwarning
        warnings.showwarning = self.__showwarning
        
        if self.parent_request is None \
               or isinstance(self.request_impl, CapturingRequestImpl):
            # top-level request (or subrequest with output captured to
            # out_buffer): set up buffer
            if self.disable_unicode:
                self.buffer = StrRequestBuffer(self.request_impl.buffer)
            else:
                self.buffer = UnicodeRequestBuffer(self.request_impl.buffer,
                                                   self.output_encoding,
                                                   self.encoding_errors)
        else:
            # use parent's request buffer
            self.buffer = self.parent_request.buffer

        self.out = self.write = self.buffer.write # optimization
        
        self.request_args = self.request_impl.request_args
        self.global_args = self.request_impl.global_args
        [self.global_args.setdefault(k, v) for k,v in self.interpreter.global_args.iteritems()]
        [self.global_args.setdefault(k, None) for k in self.interpreter.compiler().allow_globals]
        component = self.component

        # current request-clearing try/finally
        try:
            # exception handling try/except
            try:
                if type(component) == types.StringType:
                    component = self.fetch_lead_component(component)
                elif component.is_file_component():
                    self.request_path = component.path

                self.request_component = component

                depth = 0
                self.wrapper_chain = []
                while (component):
                    self.wrapper_chain.append(component)
                    if not component.is_file:
                        break
                    component = component.parent_component
                    depth += 1
                    if depth >= self.max_recursion:
                        self._raise_error("Max %d levels deep in determining inheritance chain (recursive inheritance pattern?)" % depth);

                if self.disable_wrapping:
                    first_component = self.wrapper_chain[0]
                else:
                    first_component = self.wrapper_chain[-1]

                result = None
                try:
                    result = self.execute_component(first_component, base_component = self.request_component, args = self.request_args)
                except exception.Abort: raise
                except exception.Decline, d: result = d.declined_value
                except exception.AbortRequest: pass

                return result

            except exception.Redirected, e:
                self.request_impl.send_redirect(e.path)
            except exception.Abort, e:
                self.request_impl.send_abort(e.aborted_value, e.reason)
            except exception.Error, e:
                error = e
            except Exception, e:
                error = exception.Error(wrapped = e)
            except:
                e = sys.exc_info()[0]
                error = exception.Error(wrapped = e)

            if error:
                error.initTraceback(self.interpreter)
                if self.parent_request is not None:
                    raise error
                else:
                    if self.raise_error:
                        raise error
                    else:
                        self.request_impl.handle_error(error, self)

        finally:
            # before we leave the execute method, remove all 
            # buffers and restore the request threadlocal
            del self.write, self.out
            self.buffer = None
            warnings.showwarning = saved_showwarning
            
            if existing_request:
                reqinstance.put(existing_request)
            else:
                reqinstance.remove()


    def comp(self, component, **params):
        """component calling method which takes a simple parameter 
        list.
        
        this method is meant to be the default method to call when
        calling components programmatically.
        compare to scomp()."""
        
        return self.execute_component(component = component, args = params)

    def scomp(self, component, **params):
        """component calling method which returns output as a string"""
        self.buffer.push_capture_buffer()
        self.execute_component(component = component, args = params, store = None)
        return self.buffer.pop_capture_buffer().getvalue()
    
    def subexec(self, component, **params):
        """creates a subrequest with the given component and request parameters and executes it.
        
        see create_subrequest()."""
        self.make_subrequest(component, **params).execute()
    
                        
    def execute_component(self, component, args = {}, base_component = None, content = None, store = None, is_call_self = False):
        """component calling method which takes parameter list as a
        dictionary, and allows special execution options.
        
        This method is used by component call tags and internally within
        the Request object."""
        path = None
        if type(component) == types.StringType:
            path = component
            component = self.fetch_component(path)
        
        if self.depth >= self.max_recursion:
            self._raise_error("%d levels deep in component stack (infinite recursive call?)" % self.depth)
        
        
        # if base component was set, use that
        # otherwise, figure it out
        if not base_component:
        
        
            # however, for method and file components, we might have to figure
            # the appropriate base class if there is a colon in the path
            if (
                (component.is_method_component() or not component.is_sub_component()) and
                path and 
                not component.is_module_component() and 
                not re.match(r"(?:SELF|PARENT|REQUEST)(?:\:..*)?$", path)):
                
                match = re.match(r"(.*):", path)
                if match:
                    base_component = self.fetch_component(match.group(1))
                else:
                    base_component = component
                    
                if base_component.is_sub_component():
                    base_component = base_component.owner
            
            elif len(self.execution_stack):
                # base_component defaults to that of the top of the execution stack
                base_component = self.execution_stack[-1].base_component

        frame = Request.StackFrame(self, component, args, base_component, content, is_call_self)
        self.execution_stack.append(frame)

        initial_buffer_state = self.buffer.get_state()

        # if they requested to store the output, push that buffer onto the stack
        if store:
            self.buffer.push_capture_buffer(store)

        if component.has_filter():
            self.buffer.push_filter(frame.filter)

        # Figure out if buffering is needed.
        do_auto_flush = component.use_auto_flush()
        if component.has_filter():
            # If filtering, auto_flush defaults to False
            if do_auto_flush is None or self.dont_auto_flush_filters:
                do_auto_flush = False
        # If this is the top-level component, auto_flush defaults to config val
        if do_auto_flush is None and len(self.execution_stack) == 1:
            do_auto_flush = self.auto_flush

        if not do_auto_flush:
            self.buffer.push_buffer()

        discard_buffered_output = True
        try:
            if component.flags.setdefault('use_cache', False):
                retval = value()
                if self.cache_self(retval = retval, **component.flags):
                    discard_buffered_output = False
                    return retval()

            result = component.run(self, **args)
            discard_buffered_output = False
        finally:
            self.execution_stack.pop()
            # Warning: pop_to_state can raise UnicodeError
            self.buffer.pop_to_state(initial_buffer_state,
                                     discard=discard_buffered_output)

        return result

    def fetch_lead_component(self, path):
        """fetches the top level (initial) component to be executed by this request.  Differs from
        fetch_component in that the resolver context is "request" or "subrequest" and the dhandler
        flag is enabled when resolving.   Also does not support method calls. """
        path = re.sub(r"/+", "/", path)

        request_path = path
        
        try:
            resolution = self.interpreter.resolve_component(path, resolver_context = self.resolver_context, enable_dhandler = self.use_dhandlers, declined_components = self.declined_components)
        except exception.ComponentNotFound, cfound:
            raise cfound.create_toplevel()
        
        # set up a pointer to the current component source, in case
        # the initialization of this component wants to do a fetch_component
        csource = resolution.csource
        
        self.current_csource = csource
        self.resolution = resolution
        
        component = self.interpreter.load_component(csource)

        if hasattr(resolution, 'dhandler_path'):
            self.dhandler_path = resolution.dhandler_path
        
        if self.request_path is None:
            self.request_path = request_path
                    
        return component


    def fetch_component(self, path, resolver_context = 'component', **params):
        """
        Given a component path (absolute or relative), returns a component.
        Handles SELF, PARENT, REQUEST, comp:method, relative->absolute
        conversion, MODULE, and local subcomponents.
        """
        
        hascolon = (string.find(path, ':') != -1)
        
        if not hascolon:
            if path == 'SELF':
                return self.base_component
            elif path == 'PARENT':
                comp = self.current_component.parent_component
                if not comp:
                    self._raise_error("PARENT designator used from component with no parent")
                else:
                    return comp
            elif path == 'REQUEST':
                return self.request_component
            elif path == 'MODULE':
                self._raise_error("MODULE designator requires module name")
        
        if self.has_current_component():
            if hascolon:
                (owner_path, argument) = re.split(':', path, 1)
                if owner_path == 'MODULE':
                    return self.fetch_module_component(argument, **params)
                elif owner_path[0]=='@':
                    return self.fetch_module_component(path[1:], **params)
                
                owner_component = self.fetch_component(owner_path, resolver_context = resolver_context, **params)
                method_component = owner_component.locate_inherited_method(argument)
                return method_component         

            if not hascolon:
                subcomp = self.current_component.get_sub_component(path)
                if subcomp: 
                    return subcomp
                    
            # adjust requested path to the path of the current component            
            path = unixpath.join(self.current_component.dir_name, path)
        else:           
            # no current component.  current csource ?
            if self.current_csource is not None:
                path = unixpath.join(self.current_csource.dir_name, path)
        
        return self.load_component(path, resolver_context = resolver_context, **params) 

    def fetch_module_component(self, moduleorpath, classname = None, raise_error = True):
        """fetches a module-based component.  Usually called by fetch_component when the 
        'MODULE' keyword is given as a prefix. """
        module = None
        modulename = None
        
        if type(moduleorpath) == types.StringType:
            if classname is None:
                (modulename, classname) = moduleorpath.split(':')               
            else:
                modulename = moduleorpath
        else:
            module = moduleorpath
            modulename = moduleorpath.__name__
            if classname is None:
                self._raise_error("classname is required with component module")

        key = "module:" + modulename + ":" + classname
        
        if self.comphash.has_key(key):
            return self.comphash[key]
        
        component = self.interpreter.load_module_component(arg = modulename + ":" + classname)
        self.comphash[key] = component
        
        if raise_error and component is None:
            raise exception.ComponentNotFound("Cant locate component %s" % key)

        return component
        
        
    def load_component(self, path, raise_error = True, resolver_context = None, **params):
        """a mirror of interpreter.load() which caches its results in a request-local
        dictionary, thereby bypassing all the filesystem checks that interp does for
        a repeated file-based request."""

        # since different contexts can come in here, cache based on that key as well
        # technically, all the other context-specific stuff, like dhandler, search upwards
        # etc., should be built into the key as well
        key = "%s_%s" % (str(resolver_context), path)
        
        if self.comphash.has_key(key):
            # get the component from the hash...might be None
            component = self.comphash[key]
        else:
            component = self.interpreter.load(path, raise_error = raise_error, resolver_context = resolver_context, **params)
            self.comphash[key] = component

        if raise_error and component is None:
            raise exception.ComponentNotFound("Cant locate component %s" % path)
    
        return component

    def make_subrequest(self, component, **params):
        """creates a subrequest with the given component and request parameters.
        
        see create_subrequest()."""
        return self.create_subrequest(component, request_args = params)
    
    def create_subrequest(self, component, resolver_context = 'subrequest', **params):
        """base subrequest-creation method.  A subrequest is a request that is a child to 
        this one, enabling execution of a component and its full inheritance chain within 
        this request."""

        if type(component) == types.StringType and self.has_current_component():
            component = unixpath.join(self.current_component.dir_name, component)

        params['component'] = component
        params['parent_request'] = self
        if params.get('out_buffer'):
            params['request_impl'] = CapturingRequestImpl(self.request_impl,
                                                          **params)
            params.setdefault('output_encoding', DEFAULT_OUTPUT_ENCODING)
            params.setdefault('encoding_errors', DEFAULT_ENCODING_ERRORS)
        
        request = self.clone(resolver_context = resolver_context, **params)
        request.request_depth = self.request_depth + 1
        if request.request_depth > self.max_recursion:
            raise exception.Error("recursion limit exceeded")
        return request

    def cache(self, **params):
        """a synonym for get_cache()."""
        return self.get_cache(**params)
        
    def get_cache(self, component = None, **params):
        """returns the given component's cache.  **params is a dictionary of options
        used as the default options for individually cached elements."""
        if component is None:
            component = self.current_comp()
        elif type(component) == types.StringType:
            component = self.fetch_component(component)

        if not self.compcaches.has_key(component.id):
            self.compcaches[component.id] = self.interpreter.cache_args.get_cache(component = component, starttime = component.creationtime, **params)
            
        return self.compcaches[component.id]

    
    def cache_self(self, key = '_self', component = None, retval = None, **params):
        """caches this component's output.  this is called in a "reentrant" fashion; if 
        it returns False, component execution should continue.  If it returns True,
        component execution should cease."""
        cache = self.get_cache(component = component, **params)
        
        def getself():
            rv = value()
            buf = StringIO.StringIO()
            ret = self.call_self(buf, rv)
            if not ret: raise CreationAbortedError()
            else: return (buf, rv())
            
        try:    
            (buf, ret) = cache.get_value(key, cache_createfunc = getself)
            if retval is not None:
                retval.assign(ret)

            # turn off output filtering for the currently
            # executing stack frame
            self.execution_stack[-1].reset_filter()

            self.buffer.write(buf.getvalue())
            return True
        except CreationAbortedError:
            return False

    def call_self(self, output_buffer, return_buffer):
        """calls this component and places its output and return value in the given buffers.
        This component is called in a "reentrant" fashion, where a return value of False
        means to continue component execution and a return value of True means to halt execution
        and return. """
        if self.execution_stack[-1].is_call_self: return False
        
        # turn off output filtering for the currently
        # executing stack frame
        self.execution_stack[-1].reset_filter()
        
        result = self.execute_component(self.current_component, args = self.component_args, store = output_buffer, is_call_self = True)
        return_buffer.assign(result)
        
        return True


    def get_session(self, *args, **params):
        """returns the Session object used by this request.  If the session has not been created
        it will be created when this method is called.  Once the session is created, this method
        will return the same session object repeatedly.  **params is a dictionary of options used
        when the session is first constructed; if it already exists, the parameters are ignored."""
        return self.request_impl.get_session(*args, **params)
        
    
    def has_current_component(self):
        """returns if this request has a currently executing component.
        
        This could return false if the request's top-level-component is in the loading
        stage."""
        return len(self.execution_stack) > 0
        
    def component_exists(self, path, **params):
        """returns True if the given component path exists."""
        return self.interpreter.component_exists(path, **params)

    def apply_escapes(self, text, escapes):
        """applies the given escape flags to the given text.  escapes is a list of
        escape flags, such as 'h', 'u', and 'x'."""
        # XXX: If you change this string coercion code, you should also
        #      make matching changes to {Unicode,Str}RequestBuffer.write()
        if text is None:
            text = ''
        elif self.disable_unicode:
            text = str(text)
        else:
            text = unicode(text)
        
        esctable = self.interpreter.escapes
        try:
            escfuncs = [ esctable[esc] for esc in escapes ]
        except KeyError, k:
            self._raise_error("no such escape '%s'" % k)

        for f in escfuncs:
            text = f(text)
        return text
    

    def _get_status(self):
        """debugging method that returns the current execution stack entry"""
        return ("Base Comp: %s\n_request Comp: %s\n_current Comp: %s\n" %
            (self.base_component.id, 
                self.request_component.id, 
                self.current_component.id()))
            
    
    def abort(self, status_code=None, reason=None):
        """raises an abort exception.  """
        if status_code is None:
            raise exception.AbortRequest()
        else:
            raise exception.Abort(aborted_value=status_code, reason=reason)

    def decline(self, returnval = None):
        """used by dhandlers to decline handling the current request.  Control will
        be passed to the next enclosing dhandler, or if none is found a ComponentNotFound
        (and possibly 404 error) is raised."""
        self.buffer.clear()
        subreq = self.make_subrequest(component=self.request_path,
            request_args = self.request_args)
        subreq.declined_components[self.request_component.id] = self.request_component
        ret = subreq.execute()
        raise exception.Decline(declined_value = ret)
    
    def callers(self, index = None):
        """returns the list of components in the current call stack.  if an integer 
        index is given, returns the component at that position in the current call stack."""
        if index is None:
            return map(lambda f: f.component, self.execution_stack)         
        else:
            return self.execution_stack[index].component
            
    def caller_args(self, index = None):
        """returns the list of component arguments in the current call stack.  if an 
        integer index is given, returns the component arguments at that position in the
        current call stack."""
        if index is None:
            return map(lambda f: f.args, self.execution_stack)          
        else:   
            return self.execution_stack[index].args
    
    def call_stack(self, index = None):
        """returns the current execution stack, which consists of StackFrame objects.
        if an integer index is given, returns the StackFrame object at that position
        in the current call stack."""
        if index is None:
            return self.execution_stack
        else:
            return self.execution_stack[index]
    
    def call_next(self, **params):
        """used within an inheritance chain to call the next component in the chain.  If 
        **params are given, each parameter will override the arguments sent to this component
        when calling the next component."""
        comp = self.fetch_next()
        args = {}
        args.update(self.request_args)
        args.update(params)
        
        return self.comp(comp, **args)

    def fetch_next(self):
        """in an inheritance chain (i.e. of autohandlers), returns the next component in 
        the chain"""
        try:
            self.wrapper_chain.pop()
            return self.wrapper_chain[-1]
        except IndexError:
            self._raise_error("No component available for fetch_next()")

    def fetch_all(self):
        """pops off the entire remaining list of components in the inheritance chain."""
        ret = []
        while len(self.wrapper_chain):
            ret.append(self.wrapper_chain.pop())
        return ret
        
    def send_redirect(self, path, hard=True):
        """sends a redirect to the given path.  If hard is True, sends an HTTP 302 redirect
        via the underlying RequestImpl being used.  If False, clears out the current output 
        buffer and executes a subrequest with the given path.  The path can also contain 
        url encoded query string arguments with a question mark which will be converted
        to key/value arguments for the next request, even if hard=False."""
        if hard:
            raise exception.Redirected(path)
        else:
            if re.search(r'\?', path):
                (path, query) = path.split('?')
                args = dict([(escapes.url_unescape(m.group(1)), escapes.url_unescape(m.group(2))) for m in re.finditer(r'([^=&]*)=([^=&]*)', query)])
            else:
                args = {}

            self.buffer.clear()
            req = self.create_subrequest(path, resolver_context = self.resolver_context, request_args = args)
            req.execute()
            self.buffer.flush()
            raise exception.AbortRequest()
        
    def has_content(self):
        """returns whether or not the current component call was called
        with captured content specified"""
        return self.execution_stack[-1].content != None

    def call_content(self, **kwargs):
        """calls the "captured content" function within a component call with content"""
        if not self.execution_stack[-1].content:
            return

        frame = self.execution_stack.pop()
        try:
            self.execution_stack[-1].content_args = kwargs
            frame.content()
        finally:
            self.execution_stack[-1].content_args = None
            self.execution_stack.append(frame)
        
    def content(self, **kwargs):
        """when inside a component call with content, this method calls the
        "captured content" function and buffers the content, returning the string
        value."""

        self.buffer.push_capture_buffer()
        try:
            self.call_content(**kwargs)
        finally:
            buffer = self.buffer.pop_capture_buffer()
        return buffer.getvalue()
        
    def closure_with_content(self, func, content=None, args=None):
        """given a function, will execute it with the given arguments, after pushing
        the given content function onto the call stack via a new StackFrame, enabling
        the function to call it via the content() method."""
        frame = Request.StackFrame(self, func, args, self.base_component, content, False)
        if args is None:
            args = {}
        self.execution_stack.append(frame)
        try:
            func(**args)
        finally:
            self.execution_stack.pop()
        
    def _raise_error(self, error):
        self.interpreter.raise_error(error)

    def log(self, message):
        """writes a message to the request log.  The log is RequestImpl-specific and can be 
        standard error, a webserver error log, or a user-defined file object."""
        self.request_impl.log(message)

    def __showwarning(self, message, category, filename, lineno):
        """A custom warnings handler.
        """
        interpreter = self.interpreter
        try:
            # Try to map (filename, lineno) back to original
            try:
                comprec = interpreter.reverse_lookup[filename]
            except KeyError:
                comprec = interpreter.reverse_lookup['memory:' + filename]
            reversefile = exception.Error.ReverseFile(interpreter, comprec)
            csource = comprec.csource
            filename, lineno = \
                      csource.file_path, reversefile.get_line_number(lineno)
        except:
            pass
        mesg = warnings.formatwarning(message, category, filename, lineno)
        if mesg.endswith('\n'):
            mesg = mesg[:-1]
        self.log(mesg)

    # property accessors
    
    logger = property(lambda self: _Logger(self), doc="""\
    returns the logger for this Request, which is a file-like object.
    """)
    
    depth = property(lambda self: len(self.execution_stack), doc="""\
    Returns the current depth of the execution stack.
    """)

    base_component = property(lambda self: self.execution_stack[-1].base_component, doc="""\
    Returns the "base component" for the current stack frame, which is either the top level component
    or the owning component of a method component.
    
    """)

    component_args = property(lambda self: self.execution_stack[-1].args, doc="""\
    returns the argument dictionary from the current stack frame, corresponding to the arguments
    sent to the currently executing component.
    """)
    
    content_args = property(lambda self:self.execution_stack[-1].content_args, doc="""\
    returns the component-call-with-content argument dictionary from the current stack frame, 
    corresponding to the arguments sent in an m.content() call.
    """)
    
    caller = property(lambda self: self.execution_stack[-2].component, doc="""\
    returns the calling component for the currently executing component.
    """)
    
    dhandler_argument = property(lambda self: self.dhandler_path, doc="""\
    returns the current dhandler_argument, which corresopnds to the remaining path tokens
    in the request URI when executing a dhandler.
    """)
    
    current_component = property(lambda self: self.execution_stack[-1].component, doc="""\
    returns the component currently executing from the current stack frame.
    """)


    def get_output_encoding(self):
        if self.buffer:
            return self.buffer.encoding
        else:
            return self.__output_encoding[0]
    output_encoding = property(
        get_output_encoding,
        doc="""The ouput encoding for the request

        This is the encoding of the output written to the output buffer
        of the top-level request.  (I.e. the encoding delivered to the
        user.)

        This is a read-only attribute, though you can change its value
        using the `set_output_encoding`_ method.
        """)

    def get_encoding_errors(self):
        if self.buffer:
            return self.buffer.errors
        else:
            return self.__output_encoding[1]
    encoding_errors = property(
        get_encoding_errors,
        doc="""The encoding error handling strategy for the request

        This is the error handling strategy used when encoding text
        writtent to the output buffer of the top-level request.

        This is a read-only attribute, though you can change its value
        using the `set_output_encoding`_ method.
        """)

    def set_output_encoding(self, encoding, errors='strict'):
        """Change the output_encoding.
        
        Note that in most cases you do not want to change it after you
        have written any output (as then your output will be in two
        different encodings --- probably not what you wanted unless,
        perhaps, you are generating Mime multipart output.)
        """
        if self.buffer:
            self.buffer.set_encoding(encoding, errors)
            self.__output_encoding = self.buffer.encoding, self.buffer.errors
        else:
            self.__output_encoding = encoding, errors
    
    # deprecated getter methods !   

    def get_attribute(self, key): 
        """deprecated. use the attributes property."""
        return self.notes(key)
    def set_attribute(self, key, value): 
        """deprecated. use the attributes property."""
        self.notes(key, value)
    def get_attributes(self): 
        """deprecated. use the attributes property."""
        return self.notes
    def get_depth(self): 
        """deprecated.  use the depth property."""
        return self.depth
    def get_log(self): 
        """deprecated.  use the logger property."""
        return self.logger
    def get_start_time(self): 
        """deprecated. use the starttime property."""
        return self.starttime
    def get_request_args(self):
        """deprecated.  use the request_args property."""
        return self.request_args 
    def get_base_component(self): 
        """deprecated.  use the base_component property."""
        return self.base_component
    def base_comp(self): 
        """deprecated.  use the base_component property."""
        return self.base_component
    def get_request_component(self): 
        """deprecated.  use the request_component property."""
        return self.request_component
    def request_comp(self): 
        """deprecated.  use the request_component property."""
        return self.request_component
    def get_component_args(self):
        """deprecated.  use the component_args property."""
        return self.component_args
    def get_dhandler_argument(self): 
        """deprecated.  use the request_path or dhandler_argument property."""
        return self.request_path
    def dhandler_arg(self): 
        """deprecated.  use the request_path or dhandler_argument property."""
        return self.request_path
    def get_request_path(self): 
        """deprecated.  use the request_path property."""
        return self.request_path
    def get_interpreter(self): 
        """deprecated.  use the interpreter property."""
        return self.interpreter
    def get_current_component(self): 
        """deprecated.  use the current_component property."""
        return self.current_component
    def current_comp(self): 
        """deprecated.  use the current_component property."""
        return self.current_component
    

def instance():
    """returns the Request instance corresponding to the current thread"""
    return reqinstance.get()

def threadlocal(value = None):
    """returns a thread local container, with initial value that of the given variable"""
    return ThreadLocal(value)

def value(value = None):
    """returns a value container object.  useful for mutating data that was instantiated
    in a requestonce or shared block"""
    return Value(value)
    
class AbstractRequestImpl(object):
    def clone(self):raise NotImplementedError()
    def handle_error(self, e, m, **params):raise NotImplementedError()
    def get_session(self, **params):raise NotImplementedError()

    def send_redirect(self, path):raise NotImplementedError()
    def send_abort(self, ret, reason):raise NotImplementedError()
    def log(self, message):raise NotImplementedError()

    def _run_error_handler(self, handler, logger, error, m, **params):
        err = None
        try:
            if handler:
                return handler(error, m, **params)
        except exception.Error, e:
            err = e
        except Exception, e:
            err = exception.Error(wrapped = e)
        except:
            e = sys.exc_info()[0]
            err = exception.Error(wrapped = e)

        if err:
            err.initTraceback(m.interpreter)
            logger.write("Custom error handler had an error:")
            logger.writelines(string.split(err.format(), "\n"))

        return False

    def __init__(self):
        self.global_args = None
        self.request_args = None
        self.logger = None
        self.buffer = None
        self.request = None

class DefaultRequestImpl(AbstractRequestImpl):

    def __init__(self, out_buffer = None, global_args = None, request_args = None, error_handler = None, **params):
        if out_buffer:
            self.out_buffer = out_buffer
        else:
            self.out_buffer = sys.__stdout__

        self.error_handler = error_handler
        
        if request_args is None:
            request_args = {}
        self.request_args = request_args
        if global_args is None:
            self.global_args = {}
        else:
            # copy the global_args in case they are synonymous with those given to the
            # interpreter
            self.global_args = global_args.copy()
        self.logger = sys.stderr
        
        self.buffer = self.out_buffer
            
    def handle_error(self, error, m, **params):
        if self._run_error_handler(self.error_handler, self.logger, error, m, **params): return
        
        sys.stderr.write(error.format())

    def log(self, message):self.logger.write(message + "\n")

    def clone(self, **params):
        cloner = ConstructorClone(self, **params)
        return cloner.clone()

class _Logger:
    '''A file-like object which "writes" to an object ``log()`` method.
    '''
    def __init__(self, impl): self.impl = impl
    def write(self, text): self.impl.log(text)
    def writelines(self, lines):
        for text in lines: self.write(text)

class CapturingRequestImpl(AbstractRequestImpl):
            
    def __init__(self, parent_request_impl, out_buffer,
                 request_args=None,
                 global_args=None,
                 error_handler=None,
                 **params):
        self.buffer = self.out_buffer = out_buffer
        self.parent_request_impl = parent_request_impl

        if request_args is None:
            request_args = parent_request_impl.request_args.copy()
        self.request_args = request_args

        # XXX: No .copy() here, subrequest can change parent requests
        # global_args.  Is that correct?
        if global_args is None:
            global_args = parent_request_impl.global_args
        self.global_args = global_args

        self.error_handler = error_handler

    logger = property(lambda self: _Logger(self))
    
    def handle_error(self, error, m, **params):
        if self.error_handler:
            self._run_error_handler(self.error_handler,
                                    self.logger, error, m, **params)
        else:
            self.parent_request_impl.handle_error(error, m, **params)
        
    def log(self, message):
        self.parent_request_impl.log(message)
    
