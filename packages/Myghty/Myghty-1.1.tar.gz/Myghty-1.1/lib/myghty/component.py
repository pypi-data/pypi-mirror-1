# $Id: component.py 2133 2006-09-06 18:52:56Z dairiki $
# component.py - component base classes for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
# Original Perl code and documentation copyright (c) 1998-2003 by Jonathan Swartz. 
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#

"""the component package defines the Component class and several subclasses.  FileComponent
serves as the base class for template style-components, and ModuleComponent the base
for module-based components."""

from myghty import exception
from myghty.util import *
from myghty.args import *
import myghty.request
import myghty.csource

import weakref, string
import posixpath as unixpath
import sys, inspect, types

__all__ = ['Component', 'ModuleComponent', 'HTTPModuleComponent', 'FileComponent', 'SubComponent']

argtypes = (            
    (RequestArg, True, 'required_request_args'),
    (RequestArg, False, 'request_args'),
    (SubRequestArg, True, 'required_subrequest_args'),
    (SubRequestArg, False, 'subrequest_args'),
    (LocalArg, True, 'required_args'),
    (LocalArg, False, 'args'),
    (DynamicArg, True, 'required_dynamic_args'),
    (DynamicArg, False, 'dynamic_args'),
)
        
class Component(object):
    """Base class for all components.  the primary method is the run() method which
    executes the Component in the context of a particular request.  A Component instance
    is usually cached in memory based on its component ID and can execute many requests
    simultaneously."""
    
    def __init__(self, interpreter, component_source, **params):
        """initializes a new Component. this method is called by the Interpreter."""
        self.filter = None
        self.owner = self.parent_component = None
        
        self.flags = {}
        self.attr = {}
        self.arguments = []

        self.component_source = component_source
        
        self.is_method = self.is_file = self.is_subcomponent = self.is_module = False
        
        self.size = 0
        
        self.use_count = 0
        self.interpreter = interpreter
        self.threads_init = ThreadLocal()

    id = property(lambda self: self.component_source.id, 
        doc="unique identifier for this component")
        
    source_id = property(lambda self: self.component_source.id, 
        doc="unique identifier for the ComponentSource of this component")
        
    name = property(lambda self: self.component_source.name,
        doc="name of this component")
    
    dir_name = property(lambda self: self.component_source.dir_name,
        doc="relative directory name of the component")

    path = property(lambda self: self.component_source.path,
        doc="relative full path of the component")

    file = property(lambda self: self.component_source.file_path,
        doc="the actual filename of the component, if one exists")
        
    def _parentattr(self):
        if self.parent_component is not None:
                return self.parent_component.attributes
        else:
            return None
        
    attributes = property(lambda self: InheritedDict(self.attr, lambda: self._parentattr()))

    def component_init(self):
        """initializes the component after construction.  Calls the do_component_init() method
        before setting up the component's arguments."""
        self.do_component_init()
        self._convert_component_args()
        
    def _convert_component_args(self):
        # the args system has been overhauled to be just a list of 
        # ComponentArgs objects, which come straight from the compiled
        # component file.
        # but try to do some compatibility, for older compiled components
        # and module components that have all the separate ***_args arrays 
        # attached to them.  we generate the _args if it doesnt exist,
        # and then recreate the ***_args arrays in all cases.
        for argtype in argtypes:
            self.arguments += [argtype[0](arg, argtype[1]) for arg in getattr(self, argtype[2], [])]
            # TODO: try to use property() for this
            setattr(self, argtype[2], [arg.name for arg in self.arguments if arg.__class__ == argtype[0] and arg.required == argtype[1]])

    def do_component_init(self):
        """overridden by subclasses to perform per-instance initialization steps."""
        raise NotImplementedError()
        
    def run(self, request, **params):
        """runs this component in the context of the given request.  **params are the arguments
        sent to the component, which become ARGS in the context of the component's
        runtime environment."""
        self.use_count += 1
        compparams = {}

        for arg in self.arguments:
            arg.get_arg(request, compparams, **params)

        compparams.update(request.global_args)
    
        if not self.threads_init.exists():
            self.do_thread_init()
            self.threads_init.assign(True)

        return self.do_run_component(m = request, ARGS = params, **compparams)
        
    def has_filter(self):
        """returns True if this component defines a <%filter> section."""
        return self.filter != None
    
    def _init_filter_func(self, d = None):
        if self.flags.has_key('trim'):
            # the 'trim' flag implies that the component is
            # buffered as well
            self.flags['autoflush'] = False

            try:
                func = {'left':string.lstrip, 'right':string.rstrip, 'both':string.strip}[self.flags['trim']]
                if d is not None:
                    return lambda f, **kwargs: d(func(f), **kwargs)
                else:
                    return lambda f, **kwargs: func(f)
            except KeyError, e:
                raise exception.Interpreter("invalid 'trim' argument '%s'" % e)

        elif d is not None:
            return d

    def get_flag(self, key, inherit = False):
        """returns a flag defines in this component's <%flags> section."""
        if self.flags.has_key(key):
            return self.flags[key]
        elif inherit:
            parent = self.parent_component
            if parent is not None:
                return parent.get_flag(key, True)
        
        return None

    def get_sub_component(self, name):
        """returns a SubComponent of the given name, represented within the source
        of this Component."""
        return None
    
    def do_run_component(self, m, ARGS, **params):
        """overridden by subclasses to provide the main execution body of the component."""
        raise NotImplementedError()

    def do_thread_init(self):
        """overridden by subclasses to provide a per-thread initialization routine."""
        pass
    
    def locate_inherited_method(self, method_name):
        """returns a method SubComponent of the given name, represented either within the
        source of this Component or within the source of an inherited Component, 
        i.e. the inheritance hierarchy will be searched for the approrpriate method call."""
        raise NotImplementedError()

    def call_method(self, method_name, **params):
        """calls a method SubComponent of the given name on this component.  
        This amounts to locating it via locate_inherited_method, retrieving the
        current request via request.instance(), and then calling execute_component
        on that request.

        See also m.comp("component:methodname")
        """
        
        method_component = self.locate_inherited_method(method_name)            
        return myghty.request.instance().execute_component(method_component, args = params, base_component = self)

    def scall_method(self, method_name, **params):
        """same as call_method, but returns the component output as a string
        See also m.scomp("component:methodname")
        """
        
        method_component = self.locate_inherited_method(method_name)            
        buffer = StringIO()
        myghty.request.instance().execute_component(method_component, args = params, base_component = self, store = buffer)
        return buffer.getvalue()
    
    def use_auto_flush(self):
        """returns True if this component defines the "autoflush" flag as True, or
        if an inherited component defines this flag."""
        return self.get_flag('autoflush', inherit = True)
    

    # these are all deprecated
    def get_attribute(self, key, inherit = True): 
        return self.attributes(key)
    def set_attribute(self, key, value): 
        self.attributes(key, value)
    def get_attributes(self): 
        return self.attributes
    def attribute_exists(self, key): 
        return self.attributes.has_key(key)

    def get_owner(self):
        return self.owner
    def get_parent_component(self):
        return self.parent_component
    def get_id(self):
        return self.id
    def get_name(self):
        return self.name 
    def get_source_id(self):
        return self.source_id
    def get_file(self): 
        return self.file
    def get_path(self): 
        return self.path
    def get_dir_name(self): 
        return self.dir_name
    def is_method_component(self):
        return self.is_method
    def is_module_component(self):
        return self.is_module
    def is_file_component(self):
        return self.is_file
    def is_sub_component(self):
        return self.is_subcomponent
    
    

class FileComponent(Component):
    "a component that corresponds to a Myghty template file"

    def __init__(self, interpreter, component_source, **params):
        Component.__init__(self, interpreter, component_source, **params)

        
        self.defs = None
        self.methods = None
        self.inherit_path = None
        self.inherit_start_path = None
        self.is_file = True

        self.size = component_source.modulesize

        self.component_init()

        if self.uses_thread_local():
            self.thread_local = ThreadLocal(creator = self.thread_local_initializer)
        
        if self.uses_request_local():
            self.request_local = weakref.WeakKeyDictionary()
            
        self.subcomponents = self.defs.copy()
        self.subcomponents.update(self.methods)
        self._determine_inheritance()
        
        

    def uses_thread_local(self):raise NotImplementedError()
    def uses_request_local(self):raise NotImplementedError()

    def is_file_component(self):return True

    def get_sub_component(self, name):
        if self.subcomponents.has_key(name):
            return self.subcomponents[name]
        else:
            return None

    def _call_dynamic(self, key, m, ARGS, **params):
        """handles components with %threadlocal and/or %requestlocal sections"""
        
        context = None
        
        if self.uses_thread_local():
            if self.uses_request_local():
                if self.request_local.has_key(m):
                    context = self.request_local[m]
                else:
                    initializer = self.thread_local.get(self, m, ARGS, **params)
                    context = initializer(self, m, ARGS, **params)
                    self.request_local[m] = context
                
            else:
                context = self.thread_local.get(self, m, ARGS, **params)
            
        elif self.uses_request_local():
            if self.request_local.has_key(m):
                context = self.request_local[m]
            else:
                context = self.request_local_initializer(self, m, ARGS, **params)
                self.request_local[m] = context
                
        if context is None:
            raise exception.Error("dynamic method context not found")
        else:
            return context[key](m, ARGS, **params)


        
    def locate_inherited_method(self, method_name):
        component = self
        while component:
            if component.methods.has_key(method_name):
                return component.methods[method_name]
            component = component.parent_component

        raise exception.MethodNotFound("no such method '%s' found" % method_name)
        
    
    def _determine_inheritance(self):
    
        interpreter = self.interpreter
        source = self.component_source

        if self.flags.has_key('inherit'):
            if self.flags['inherit'] is None:
                pass
            else:
                self.inherit_path = unixpath.normpath(unixpath.join(source.dir_name, self.flags['inherit']))
        elif interpreter.use_auto_handlers:
            if source.name == interpreter.auto_handler_name:
                if source.dir_name and source.dir_name != '/':
                    self.inherit_start_path = unixpath.dirname(source.dir_name)
                else:
                    # we are the autohandler in the root directory
                    pass
            else:
                self.inherit_start_path = self.component_source.dir_name
        

    def _parent_component(self):
        """returns the parent component of this component, taking into account
        the component's inherit flag as well as the interpreter's autohandler properties"""

        try:
            request = myghty.request.instance()

            # optional - cache results of this function on the request
            #try:
            #   return request.attributes['_parent_comp_%s' % self.id]
            #except KeyError: pass
            
        except KeyError:
            # no current request for whatever reason, so call
            # load() off the interpreter
            request = None

        if self.inherit_path is not None:
            if request is not None:
                component = request.load_component(self.inherit_path, resolver_context = 'inherit')
            else:
                component = self.interpreter.load(self.inherit_path, resolver_context = 'inherit')
        elif self.inherit_start_path is not None:
            if request is not None:
                component = request.load_component(unixpath.join(self.inherit_start_path, self.interpreter.auto_handler_name), search_upwards = True, raise_error = False, resolver_context = 'inherit')
            else:
                component = self.interpreter.load(unixpath.join(self.inherit_start_path, self.interpreter.auto_handler_name), search_upwards = True, raise_error = False, resolver_context = 'inherit')
        else:
            component = None
        
        #if request is not None:
        #   request.attributes['_parent_comp_%s' % self.id] = component
            
        return component

    parent_component = property(_parent_component, lambda s, p: None)


class SubComponent(Component):
    """a component that corresponds to a <%def> or <%method> tag 
    inside a file-based component."""
    
    def __init__(self, name, owner, is_method, **params):
        Component.__init__(self, owner.interpreter, owner.component_source, **params)
        self.__name = name
        self.__owner = owner
        self.is_method = is_method
        self.is_subcomponent = True

        self.component_init()


    def _call_dynamic(self, key, m, ARGS, **params):
        return self.owner._call_dynamic(key, m, ARGS, **params)

    id = property(lambda self: self.owner.id + ":" + self.name)
    parent_component = property(lambda self: self.owner.parent_component, lambda s, p:None)
    name = property(lambda self: self.__name, lambda s,p:None)
    owner = property(lambda self: self.__owner, lambda s,p:None)
    
    def get_sub_component(self, name):return self.owner.get_sub_component(name)

    def locate_inherited_method(self, method_name):return self.owner.locate_inherited_method(method_name)
    def call_method(self, *args, **params):return self.owner.call_method(*args, **params)
    def scall_method(self, *args, **params):return self.owner.scall_method(*args, **params)




class ModuleComponent(Component):
    """A component that is a regular Python class inside of a plain Python module."""
    
    def __init__(self, interp, component_source, owner = None, do_init = True):
        Component.__init__(self, interp, component_source)
        self.__name = self.__class__.__name__
        self.is_method = True
        self.creationtime = component_source.last_modified
        
        self.methods = Registry()
        if owner is None:
            self.__owner = self
        else:
            self.__owner = owner

        if do_init:
            self.component_init()


    owner = property(lambda self: self.__owner, lambda s, p:None)
    name = property(lambda self: self.__name, lambda s, p:None)

    def _inspect_args(self, function):
        csource = self.component_source

        argspec = inspect.getargspec(function)
            
        argnames = argspec[0] or []
        defaultvalues = argspec[3] or []

        d = dict([(a, True) for a in self.interpreter.compiler().allow_globals + ['m', 'ARGS', 'self']])

        (self.required_args, self.args) = (
                [a for a in argnames[0:len(argnames) - len(defaultvalues)] if not d.has_key(a)], 
                [a for a in argnames[len(argnames) - len(defaultvalues):] if not d.has_key(a)]
                )
        
        self._allargs = argnames
        self._has_params = argspec[2] is not None

    def component_init(self):
        self.do_component_init()

        # if no new-style argument list has been set up
        if len(self.arguments) == 0:
            # and no old-style argument lists have been added
            for argtype in argtypes:
                if hasattr(self, argtype[2]):
                    break
            else:
                # then inspect the do_component_init function and figure out the args
                # that way.
                self._inspect_args(self.do_run_component.im_func)

        # tell base class to set up arguments list    
        self._convert_component_args()
        
    def do_component_init(self):pass

    def do_run_component(self, m, ARGS, **params):raise NotImplementedError()
    
    def is_module_component(self):return True

    def _find_method(self, method_name):
        if self.__class__.__name__ == method_name:
            return self

        return self.interpreter.load_module_component(self.__module__ + ":" + method_name)            
    
    def locate_inherited_method(self, method_name):
        if self.owner is self:
            return self.methods.get(method_name, createfunc = lambda: ModuleComponent._find_method(self, method_name))
        else:
            return self.owner.locate_inherited_method(method_name)
        
    
    
class HTTPModuleComponent(ModuleComponent):
    """A ModuleComponent that contains methods specific to a generic HTTP request."""

    def do_post(self, m, r, **params):
        # 'method not allowed', unless this is overridden
        m.abort(405)

    def do_get(self, m, r, **params):
        # 'method not allowed', unless this is overridden
        m.abort(405)
    
    def do_run_component(self, m, r, **params):
        methods = {
            'GET': HTTPModuleComponent.do_get,
            'POST': HTTPModuleComponent.do_post,
        }
        
        try:
            f = methods[r.method]
            return f(self, m, r, **params)
        except KeyError:
            m.abort(405)
            
class FunctionComponent(ModuleComponent):
    """a module component that "wraps" a regular Python function or method, including
    introspection of its signature to automatically produce the required_args
    and args lists """
    
    def do_component_init(self):
        csource = self.component_source

        self._inspect_args(csource.callable_)
        
        # if we are linked to a method off of an object instance,
        # see if the object instance has a do_component_init method and if the object instance
        # does not have a _component_init attribute.  call do_component_init() and 
        # set the _component_init attribute to True
        if self.component_source.has_method:
            target = self.component_source.callable_.im_self
            if hasattr(target, 'do_component_init') and not hasattr(target, '_component_init'):
                try:
                    getattr(target, 'do_component_init')(self)
                finally:
                    target._component_init = True
               
    def do_run_component(self, **params):
        if self._has_params:
            return self.component_source.callable_(**params)    
        else:
            d = {}
            for a in self._allargs:
                if params.has_key(a):
                    d[a] = params[a]
            return self.component_source.callable_(**d)
                
    def get_method_csource(self, name):    
        if not self.component_source.has_method:
            return None
        obj = self.component_source.callable_.im_self
        meth = getattr(obj, name)
        return myghty.csource.ModuleComponentSource(module=self.component_source.module, callable_=meth, name="method:" + meth.im_func.__name__)

    def get_method(self, m, name):
        cs = self.get_method_csource(name)
        return m.interpreter.load_component(cs)
