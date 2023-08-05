<%flags>
    # myghtyjax.myt needs to inherit from either None, or an autohandler
    # that doesnt have any textual output.
    inherit=None
    trim="both"
</%flags>

<%doc>
    MyghtyJax - a Myghty AJAX Adapter
    
    The "init" method is called to register the names of javascript functions that will
    map to Myghty components and/or python function definitions.  supply
    key=value arguments, where keys are the names of javascript functions 
    to be generated and the value is one of: a function object, the string
    address of a Myghty component (path or method name), or a Myghty component object.
    This method should be called in the %init section of the calling component, usually before
    anything else has executed.  If it returns true it means the XMLHttpRequest action
    is taking effect, and the calling component should return immediately.  
    If false is returned, the component should continue on normally. 

    Note that the "js" method below must be called within the HTML body of a page to
    actually write out the javascript functions defined by the init method.

    components that are called can specify options for how they should be handled via their
    <%attr> sections.  the available options are:

    type='source'
                    take the HTML source of the component and send it to a supplied javascript
                    callback function.

    type='writedom' 
                    take the HTML source of the component and send it to the DOM element
                    with the id given by either the <%attr> 'dom_id', or the first argument
                    to the javascript function.

    type='exec' 
                    take the output of the component and evaluate it directly as javascript.

    Example:

        if m.comp('myghtyjax.myt:init',
              mypage = 'SELF:mymethod'
        ): return

    The above example will create a javascript function 'mypage()', which results in an Ajax
    call back to the myghtyjax.myt page which will route the request to the <%method mymethod>
    inside the current page.  The results of the method will be processed per the "type"
    attribute on the method.

    A second form of init argument allows the values normally inside <%attr> to be 
    specified directly to init:

        if m.comp('myghtyjax.myt:init',
              mypage = {
                   'component' : 'SELF:mymethod',
                   'exectype' : 'writedom',
                   'dom_id' : 'leftnav'
              }
        ): return

    The above example will create a javascript function 'mypage()', which results in an Ajax
    call back to the myghtyjax.myt page which will route the request to the <%method mymethod>
    inside the current page.  The resulting output from the method will be written to the
    'leftnav' DOM element on the page.

    There is also a way to circumvent the usual URL of the myghtyjax controller 
    directly to any URL:

        if m.comp('myghtyjax.myt:init',
             mypage = {
                   'handler_uri' : '/my_ajax_page/',
                   'exectype' : 'writedom',
                   'dom_id' : 'leftnav'
             }
         ): return

    The above example will create a javascript function 'mypage()', which results in an Ajax
    call directly to the uri '/my_ajax_page/', and the resulting HTML will be written into the
    DOM element 'leftnav'.
</%doc>
<%method init>
    <%init>
        frame = m.execution_stack.pop()
        try:
            ret = init(m, **ARGS)
        finally:
            m.execution_stack.append(frame)
        return ret
    </%init>
</%method>

<%doc>
    js is called after init has been called, and delivers the javascript "stub" functions
    that connect page javascript to server side calls via XMLHttpRequest.
    
    the scripturi and handleruri arguments are optional arguments that 
    reference the web-accessible URIs of the myghtyjax.js and myghtyjax.myt 
    files respectively.  

    If these parameters are not supplied, they will be searched for in the interpreter 
    attributes "myghtyjax.handleruri" and "myghtyjax.scripturi".  
    if not there either, they will be determined based on the path of the original 
    calling component.
</%doc>
<%method js>
    <%args>
        scripturi = None
        handleruri = None
    </%args>
    <%init>
        js(m, handleruri = handleruri, scripturi = scripturi)
    </%init>
</%method>

<%args>
    _mjax_def
    _mjax_component
</%args>

<%init>
    m.comp(_mjax_component, **ARGS)
</%init>


<%once>

import inspect, string, types, posixpath
import myghty.request as request

# initialization method, receives javascript function names mapped
# to python function pointers, component names, or component objects.
# referenced by the "init" myghty method.
def init(m, **params):
    run_func = m.request_args.get('_mjax_def', None)
    
    if (run_func is not None):
        object = params[run_func]
        callable = _get_callable(m, run_func, object)
        callable.run(m)
        return True
    else:
        defs = m.attributes.setdefault('__mjax_defs', {})
        for (jsname, object) in params.iteritems():
                    defs[jsname] = _get_callable(m, jsname, object)
        return False
    
def _get_callable(m, name, object):
    if isinstance(object, types.FunctionType):    
        return DefCallable(name, object)
    elif isinstance(object, dict):
        return ComponentCallable(m, name, **object)
    else:
        return ComponentCallable(m, name, object)
        
def js(m, handleruri = None, scripturi = None):
    try:
        defs = m.attributes['__mjax_defs']
    except KeyError:
        raise "myghtyjax.js() method requires components and defs to be init()ialized first"

    path = m.current_component.path

    if handleruri is None:
        handleruri = m.interpreter.attributes.get('myghtyjax.handleruri', path)
        

    if scripturi is None:
        scripturi = m.interpreter.attributes.get('myghtyjax.scripturi', None)
        if scripturi is None:
            (dir, file) = posixpath.split(path)
            scripturi = posixpath.join(dir, "myghtyjax.js")
    
    m.write("<script src=\"%s\"></script>\n" % scripturi)
    m.write("<script>\n");
    for callable in defs.values():
        callable.init_callerpath(m)
        if callable.exectype == 'writedom':
            m.comp('SELF:write_writedom', callable = callable, handleruri = handleruri)
        elif callable.exectype == 'source':
            m.comp('SELF:write_docall', callable = callable, handleruri=handleruri)
        else:    
            m.comp('SELF:write_remotejs', callable = callable, handleruri=handleruri)

    m.write("</script>\n")

class JaxComponent:
    def init_callerpath(self, m):
        if getattr(self, 'callerpath',None) is None:
            self.callerpath = m.caller.path
        
    def get_function_args(self, leading_comma = False):
        args = string.join(self.argnames + ['_mjax_named'], ',')
        if leading_comma and args:
            return ', ' + args
        else:
            return args
        
    def get_handler_uri(self, handler_uri):
        return handler_uri
        
    def get_remote_args(self, m):
        return string.join( 
                    [
                        "'_mjax_def' : '%s'" % self.jsname,
                        "'_mjax_component' : '%s'" % self.callerpath,
                        "'_mjax_named':_mjax_named"
                    ] + 
                    ["'%s' : %s" % (name, name) for name in self.argnames],
                    ",\n",
                )

        
class ComponentCallable(JaxComponent):
    def __init__(self, m, jsname, component=None, exectype=None, argnames=None, dom_id=None, handler_uri=None):
        self.jsname = jsname
        self.component = component
        self.handler_uri=handler_uri
        if type(component) == types.StringType:
            componentobj = m.fetch_component(component)
        else:
            componentobj = component

        if exectype is None:
            if componentobj is not None:
                self.exectype = componentobj.attributes.get('type', 'exec')
            else:
                self.exectype = 'exec'
        else:
            self.exectype = exectype
            
        if dom_id is None and componentobj is not None:
            self.dom_id = componentobj.attributes.get('dom_id', None)
        else:
            self.dom_id = dom_id
    
        if argnames is None:
            if componentobj is not None:
                self.argnames = [arg.name for arg in componentobj.arguments]
            else:
                self.argnames = []
        else:
            self.argnames = argnames

    def get_handler_uri(self, handler_uri):
        if self.handler_uri is not None:
            return self.handler_uri
        else:
            return handler_uri
                
    def run(self, m):
        m.comp(self.component, **m.root_request_args)
        
    
class DefCallable(JaxComponent):
    def __init__(self, jsname, defobj):
        self.jsname = jsname

        if isinstance(defobj, types.MethodType):
            defobj = defobj.im_func
        self.defobj = defobj
        self.argnames = inspect.getargspec(defobj)[0]
        self.has_named = inspect.getargspec(defobj)[2] is not None
        self.exectype = 'exec'    
                
    def run(self, m):
        if self.has_named:
            m.write(self.defobj(**m.root_request_args))
        else:
            args = {}
            for name in self.argnames:
                args[name] = m.root_request_args[name]
            
            m.write(self.defobj(**args))

</%once>

<%method write_docall>
    <%args>
        callable
        handleruri
    </%args>
    function <% callable.jsname %>(callback<% callable.get_function_args(leading_comma = True) %>) {
        doCall('<% callable.get_handler_uri(handleruri) %>', callback, {
<% callable.get_remote_args(m) %>
        });
    }
</%method>

<%method write_remotejs>
    <%args>
        callable
        handleruri
    </%args>
    function <% callable.jsname %>(<% callable.get_function_args() %>) {
        runRemoteJS('<% callable.get_handler_uri(handleruri) %>', {
<% callable.get_remote_args(m) %>
        });
    }
</%method>

<%method write_writedom>
    <%args>
        callable
        handleruri
    </%args>
% if callable.dom_id is None:
    function <% callable.jsname %>(domid <% callable.get_function_args(leading_comma = True) %>) {
        populateDOM(domid, '<% callable.get_handler_uri(handleruri) %>', {
<% callable.get_remote_args(m) %>
        });
    }
% else:
    function <% callable.jsname %>(<% callable.get_function_args() %>) {
        populateDOM('<% callable.dom_id %>', '<% callable.get_handler_uri(handleruri) %>', {
<% callable.get_remote_args(m) %>
        });
    }
%
</%method>


