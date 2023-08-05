# $Id: csource.py 2133 2006-09-06 18:52:56Z dairiki $
# csource.py - component source objects for Myghty
# Copyright (C) 2005 Michael Bayer mike_mp@zzzcomputing.com
# Original Perl code and documentation copyright (c) 1998-2003 by Jonathan Swartz. 
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

import posixpath as unixpath
import time, re, os, stat, types, sys, string
import __builtin__ as builtin
import myghty.util as util
import myghty.importer as importer
import myghty.exception as exception

class ComponentSource(object):
    """a time-sensitive descriptor object for a Myghty component."""
    def __init__(self, id, last_modified = None ):
    
        "unique identifier of the component."
        self.id = id
        
        "for file components, the filename without path."
        self.name = ""
        
        "for file components, relative directory where the component lives."
        self.dir_name = ""
        
        "for file components, this is dir_name + name"
        self.path = ""
        
        "for file components, this is the real filesystem path of the component."
        self.file_path = ""
        
        "for file components, id of the path, i.e. the key in the component_root hash."
        self.path_id = ""
        
        "the module containing the actual code for the component."
        self.module = None
        
        "guesstimate of the size of the component. this is filled in by Interpreter."
        self.modulesize = 0
                
        if last_modified:
            self.last_modified = last_modified
        else:
            self.last_modified = int(time.time())

    def can_compile(self):return True
    
    def get_component_source_file(self):raise NotImplementedError()
    
    def get_component_source(self):raise NotImplementedError()
    
    def get_object_code(self, compiler, file):
        """compiles the source of this component using the given compiler,
        sending output to the given file"""
        compiler.compile(
            source = self.get_component_source(),
            name = self.id,
            file = file,
            input_file = self.file_path,
        )
        
class ModuleComponentSourceSingleton(type):
    """a metaclass for ModuleComponentSource which allows its constructor to cache the 
    inspection results of the "arg" constructor parameter. """
    def __call__(self, **kwargs):
        arg = kwargs.get('arg', None)
        arg_cache = kwargs.pop('arg_cache', None)
        use_static_source = kwargs.pop('use_static_source', False)
        if arg_cache is not None and arg is not None:
            try:
                mc = arg_cache[arg]
            except KeyError:
                mc = type.__call__(self, **kwargs)
                arg_cache[arg] = mc
            return mc.copy(use_static_source=use_static_source)
        else:
            return type.__call__(self, **kwargs)
       
class ModuleComponentSource(ComponentSource):
    """represents a loadable module containing either a ModuleComponent class, a function, a class
    instance which is callable or a method on a class instance. """
    
    __metaclass__ = ModuleComponentSourceSingleton
    
    def __init__(self, 
        arg = None,
        module = None, 
        objpath = None,
        name = None,
        callable_ = None,
        class_ = None,
        last_modified = None):

        if arg is not None:
            if isinstance(arg, str):
                (modname, objname) = arg.split(':')
                module = importer.module(modname)
                objpath = objname.split('.')

            if objpath is not None:
                arg = module
                for t in objpath:
                    arg = getattr(arg, t)

            name = self.inspect_target(arg, objpath)

            if module is None:
                if self.class_ is not None:
                    module = sys.modules[self.class_.__module__]
                elif self.has_method:
                    module = importer.module(self.callable_.im_class.__module__)
                else:
                    module = importer.module(self.callable_.__module__)

        else:
            self.class_ = class_
            self.callable_ = callable_
            self.has_method = callable_ is not None and (isinstance(arg, types.MethodType) or not isinstance(arg, types.FunctionType))
            
        if last_modified is None:
            last_modified = importer.mod_time(module)

        ComponentSource.__init__(self, "module|%s:%s" % (module.__name__, name), last_modified = last_modified)
            
        self.module = module
        self.objpath = objpath
        self.name = name


    def reload(self, module):
        # the "objpath" is a list of tokens that allow us to traverse from the
        # module to the callable/class unit.  if we dont have that, then we can't 
        # reload dynamically.
        if self.objpath is None:
            return

        self.module = module        
        arg = module
        for t in self.objpath:
            arg = getattr(arg, t)

        self.inspect_target(arg, self.objpath)

    def inspect_target(self, arg, objpath):
        self.has_method = False

        self.class_ = None
        self.callable_ = None
        
        if isinstance(arg, types.TypeType) or isinstance(arg, types.ClassType):
            self.class_ = arg
            name = "class:" + arg.__name__
        elif isinstance(arg, types.MethodType):
            self.callable_ = arg
            if objpath is not None:
                name = "method:" + string.join(objpath, '_')
            else:
                name = "method:" + arg.im_func.__name__
            self.has_method = True
        elif isinstance(arg, types.FunctionType):
            self.callable_ = arg
            if objpath is not None:
                name = "function:" + string.join(objpath, '_')
            else:
                name = "function:" + arg.__name__
        elif callable(arg):
            arg = arg.__call__
            self.callable_ = arg
            if objpath is not None:
                name = "callable:" + string.join(objpath, '_')
            else:
                name = "callable:" + arg.__class__.__name__
            self.has_method = True
        else:
            raise "arg is " + repr(arg)
            
        return name
    
    def copy(self, use_static_source = False): 
        if use_static_source:
            last_modified = self.last_modified
        else:
            last_modified = importer.modulemodtime(self.module)
            
        return ModuleComponentSource(module = self.module, objpath = self.objpath, callable_ = self.callable_, name=self.name, class_ = self.class_, last_modified = last_modified)
        
    def can_compile(self):
        return False


class MemoryComponentSource(ComponentSource):
    def __init__(self, source, id = None,  last_modified = None):
        if id is None:
            id = str(builtin.id(self))
            
        ComponentSource.__init__(self, id, last_modified)
        self.source = source
            
    def get_component_source_file(self):
        return util.StringIO(self.source)
    
    def get_component_source(self):
        return self.source

    
class FileComponentSource(ComponentSource):
    def __init__(self, id, path_id, path, file_path, last_modified=None):
        if last_modified is None:
            last_modified = os.stat(file_path)[stat.ST_MTIME]
            
        ComponentSource.__init__(self, id, last_modified)
        self.file_path = file_path
        self.path = path
        self.path_id = path_id
        (self.dir_name, self.name) = unixpath.split(path)
    
    def get_component_source_file(self):
        return open(self.file_path)
    
    def get_component_source(self):
        return self.get_component_source_file().read()
