# $Id: interp.py 2133 2006-09-06 18:52:56Z dairiki $
# interp.py - interprets requests to Myghty templates
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
# Original Perl code and documentation copyright (c) 1998-2003 by Jonathan Swartz. 
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#


"""The interp package and its primary class, Interpreter, represents the runtime environment 
for Myghty components.  It serves as a "home base" for configuration information and request
construction, and also assists the Request object in locating components.  The Interpreter
maintains a pool of component objects and handles, at a high level, their compilation 
and filesystem representation."""

from myghty.util import *
import myghty.util as util
from myghty.synchronization import *
import myghty.exception as exception
import myghty.resolver
import myghty.request
import myghty.csource
import myghty.compiler
import myghty.escapes
import myghty.importer as importer
import myghty.buffer
import myghty.cache
import myghty.component
from stat import *
import time, os, stat, re, types, sys, string, random
import posixpath as unixpath
import weakref, imp, py_compile

__all__ = ['Interpreter']

class Interpreter:
    """Represents an environment in which to create requests, compile and execute components."""
    def __init__(self, 
            attributes = None, 
            data_dir = None, 
            compiler = None, 
            resolver = None, 
            request = None,
            code_cache_size = 16777216,
            use_auto_handlers = True,
            use_object_files = True,
            debug_file = myghty.buffer.LinePrinter(sys.stderr),
            debug_threads = False,
            debug_elements = [],
            escapes = {},
            global_args = None,
            auto_handler_name = 'autohandler',
            **params):
        """constructs a new Interpreter object.  All Myghty configuration parameters are sent to this
        method as keyword parameters.  Those parameters that are used directly by this Interpreter are
        consumed.  Remaining arguments are sent off to other constructed objects, which include a
        Compiler, a Resolver, and a Request prototype object."""
        self.global_args = global_args or {}
        self._attributes = {}
        if attributes is not None:
            self._attributes.update(attributes)
            
        self.attributes = InheritedDict(self._attributes, lambda: None)
    
        self.init_params = params
        self.use_auto_handlers = use_auto_handlers
        self.auto_handler_name = auto_handler_name
        self.use_object_files = use_object_files

        self.use_static_source = params.get('use_static_source', False)
    
        # set up debug stuff
        self.debuggers = {}

        self.log_file = myghty.buffer.LogFormatter(debug_file, 'Myghty', id_threads = debug_threads)
        if len(debug_elements):
            self._debug = True

            for elem in debug_elements:
                # how very strange this is !  
                s = ( 
                "def log(msg):\n" +
                "    self.log_file.write('[%s] ' + msg)\n" +
                "self.debuggers[elem] = log") % elem
                exec s in locals()
        
            self.log_file.write("%s starting - debug logging: %s" % (repr(self),  string.join(debug_elements, ' ')))
        else:
            self._debug = False
        # ------------------

        if params.has_key('component'):
            del params['component']

        # set up cache object creator
        self.cache_args = myghty.cache.CacheArgs(cache_data_dir = data_dir, **params)
        if self.debuggers.get('cache', None) is not None:
            self.cache_args.set_params(debug_file = myghty.buffer.FunctionBuffer(self.debuggers['cache']))

        # set up resolver
        if resolver:
            self.resolver = resolver
        else:
            self.resolver = myghty.resolver.Resolver(**params)
        
        if self.debuggers.get('resolution', None) is not None:
            self.resolver.debug_file = myghty.buffer.FunctionBuffer(self.debuggers['resolution'])

        # set up thread-local compiler prototype        
        if not compiler: compiler = myghty.compiler.Compiler(**params)
        self.compiler = ThreadLocal(creator = lambda: compiler.clone())
                
        # set up request prototype
        if request:
            self.request = request
        else:
            self.request = myghty.request.Request(self, **params)


        # data directory stuff, make sure directories exist     
        if data_dir is not None:
            self.data_dir = data_dir
            self.object_dir = unixpath.join(data_dir, 'obj')
            self.lock_dir = unixpath.join(data_dir, 'lock')
        else:
            self.data_dir = None
            self.object_dir = None
            self.lock_dir = None
        
        if data_dir is None:
            self.use_object_files = False
        else:
            self._verify_directory(self.object_dir)
            self._verify_directory(self.lock_dir)

        # a dictionary of CompileRecord objects linked to the filename they
        # are compiled into.  strong reference provided by the resulting FileComponent
        # object.
        self.reverse_lookup = weakref.WeakValueDictionary()
        
        def componentdeleted(comp):
            if self._debug: self.debug("code_cache size %d - removing %s (%d bytes)" % (self.code_cache.currentsize, comp.id, comp.size), "codecache") 

        self.code_cache = LRUCache(code_cache_size, deletefunc=componentdeleted)

        self.escapes = {'h':myghty.escapes.html_escape, 'u':myghty.escapes.url_escape, 'x':myghty.escapes.xml_escape}
        self.escapes.update(escapes)


    
    def execute(self, component, **params):
        """executes the given component with the given request construction arguments.
        
        The component can be a string path which will be resolved, or a Component object."""
        return self.make_request(component = component, **params).execute()

    def make_request(self, component, **params):
        """creates a new request with the given component and request construction arguments.
        
        The request is copied from an existing request instance, overriding its parameters
        with those given.  The returned request is executed by calling its execute() method.
        
        The component can be a string path which will be resolved when the request is 
        executed, or a Component object."""
        return self.request.clone(component = component, interpreter = self, **params)

    def raise_error(self, error):   
        """raises an Interpreter error with the given message string."""
        raise exception.Interpreter(error)      


    def component_exists(self, path, **params):
        """returns True if the given path can be resolved to a ComponentSource instance,
        i.e. if a component can be loaded for this path."""
        if self.resolver.resolve(path, raise_error = False, **params):
            return True
        else:
            return False


    def load(self, path, **params):
        """resolves and loads the component specified by the given path.  **params 
        is a set of keyword arguments passed to the resolution system."""
        resolution = self.resolve_component(path, **params)
        if not resolution: return None
        return self.load_component(resolution.csource)
        
    def load_module_component(self, raise_error = True, **params):
        """resolves and loads a module component specified within the given keyword 
        parameters.  The keyword parameters are passed directly to 
        myghty.csource.ModuleComponentSource.  The easiest way to use this method
        is to pass the keyword parameter "arg", which references a string in the form 
        "<modulename>:<callable_or_class>", where <modulename> is a regular Python module
        to be loaded via __import__, and <callable_or_class> is the dotted path
        to either a callable object inside the module or a class inside the module which
        subclasses myghty.component.ModuleComponent."""
        csource = myghty.csource.ModuleComponentSource(**params)
        return self.load_component(csource)

    def resolve_component(self, path, **params):
        """resolves the component specified by the given path.  a myghty.resolver.Resolution
        object is returned containing a myghty.csource.ComponentSource reference.
        Raises ComponentNotFound by default if the path cannot be resolved.  **params is a
        set of keyword parameters sent directly to the resolve() method on myghty.resolver.Resolver."""
        return self.resolver.resolve(path, **params)
        
    def load_component(self, csource):
        """loads the component corresponding to the given ComponentSource object.  This can 
        be any subclass of ComponentSource.  If the component was already loaded and exists
        within this Interpreter's code cache, returns the existing Component.  If the Component
        has been modified at its source, it will re-load or re-compile the Component as needed.
        If this Component has not been loaded, it will import or compile the Component as needed.
        This operation is also synchronized against other threads.  On systems that support
        file-locking it is synchronized against other processes as well.
        """
        component_id = csource.id
        try:
            component = self.code_cache[component_id]

            if  (
                self.use_static_source or
                (component.component_source.last_modified >= csource.last_modified and
                component.load_time >= csource.last_modified)
                ):
                return component
            else:
                component.needs_reload = True

        except KeyError: pass

        # lock this block to other threads based on the ID of the component
        name_lock = self._get_component_mutex(component_id)
       
 
        def create():
            component = self.get_compiled_component(csource, use_file = self.use_object_files, recompile_newer = not self.use_static_source)
            if self._debug: self.debug("code_cache size %d - adding %s (%d bytes)" % (self.code_cache.currentsize, component.id, component.size), "codecache")
            component.load_time = int(time.time())
            component.needs_reload = False
            return component

        def isvalid(component):
            return not component.needs_reload
    
        component = self.code_cache.sync_get(component_id, create, name_lock, isvalid)
        return component
                
    def _get_component_mutex(self, component_id):
        return NameLock(identifier = "interpreter/loadcomponent/%s" % component_id)

    def make_component(self, source, id = None):
        """creates an in-memory template Component given its source as a string...this can
        be any Myghty template that would ordinarily be compiled from the filesystem.  
        the optional "id" string parameter is used to identify this component within 
        this Interpreter's code cache.  If not given, one will be generated."""
        csource = myghty.csource.MemoryComponentSource(source = source, id = id)
        return self.get_compiled_component(csource, use_file = False)
        
    def get_component_object_files(self, component_source):
        """returns a tuple containing the full paths to the .py, .pyc, and .pyo files corresponding to the
        given FileComponentSource object."""
        return (
                self.object_dir + '/' + component_source.path_id + '/' + component_source.path + ".py",
                self.object_dir + '/' +  component_source.path_id + '/' + component_source.path + ".pyc",
                self.object_dir + '/' +  component_source.path_id + '/' + component_source.path + ".pyo"
            )
            


    class CompileRecord:
        """a record used to link exception reporting back to the originating python
        and myghty template source"""
        
        def __init__(self, module_id, csource, compiledto = None, compiledsource = None):
            self.module_id = module_id
            self.csource = csource
            self.compiledto = compiledto
            self.compiledsource = compiledsource

        def get_compiled_source(self):
            if self.compiledsource is not None:
                return util.StringIO(self.compiledsource)
            else:
                return open(self.compiledto)
                
    def get_compiled_component(self, csource, always_recompile = False, recompile_newer = True, use_file = True):
        """used by load_component to deliver a new Component object from a ComponentSource."""
        if not csource.can_compile():
            return self._get_module_component(csource, always_recompile, recompile_newer)
        elif not use_file:
            return self._get_inmemory_component(csource, always_recompile, recompile_newer)
        else:
            return self._get_file_component(csource, always_recompile, recompile_newer)

    def _get_module_component(self, csource, always_recompile = False, recompile_newer = True):
        """loads a module component from a regular Python module.  
        Most of the module-loading code is in the util package."""
        
        module = csource.module
        if self._debug: self.debug("loading component %s from module object %s" % (csource.id, repr(module)), "classloading")

        if module.__name__ != '__main__':
            if recompile_newer or always_recompile: 
                csource.reload(importer.reload_module(module))
           
        if csource.class_ is not None and issubclass(csource.class_, myghty.component.ModuleComponent):
            return csource.class_(self, csource)
        else:
            return myghty.component.FunctionComponent(self, csource)

            
    def _get_file_component(self, csource, always_recompile = False, recompile_newer = True):
        """loads and compiles a file-based component as a regular Python module with a .py and .pyc file."""

        destbuf = None
    
        compiler = self.compiler.get()

        # the full module name of the component to be compiled
        cid = "_myghtycomp_" + re.sub(r"\W", "_", csource.path_id) + "_" + re.sub(r"\W", "_", csource.id)

        (object_file, compiled_object_file, optimized_object_file) = self.get_component_object_files(csource)

        # since we might write to a file in this area, synchronize against other threads and processes
        file_name_lock = Synchronizer("interpreter/filewriter/%s" % csource.id, use_files = True, lock_dir = self.lock_dir)

        def needs_recompile():
            # the _need_file checks the csource last modified, which corresponds to the .myt
            # file's last modified, to the actual .py file's modified time.
            return (
                always_recompile or
                (recompile_newer and self._need_file(csource.last_modified, object_file)) or
                (not self._file_exists(object_file))
                or (hasattr(csource, '_bad_magic_number') and csource._bad_magic_number)
                )

        force_reload = False
        
        # check if we have to recompile to a file
        if needs_recompile():

            file_name_lock.acquire_write_lock()
            try:
                # through the lock, check again to see if another fork already compiled
                if needs_recompile():

                    self._verify_directory(unixpath.join(self.object_dir, "./" +  csource.path_id + "/" + csource.dir_name))

                    if self._file_exists(compiled_object_file):
                        os.remove(compiled_object_file)
                    if self._file_exists(optimized_object_file):
                        os.remove(optimized_object_file)

                    if self._debug: self.debug("compiling %s in file %s" % (csource.id, object_file), "classloading")

                    destbuf = file(object_file, 'w')

                    csource.get_object_code(compiler, destbuf)

                    destbuf.close()

                    if getattr(csource, '_bad_magic_number', False):
                        force_reload = True
                    csource._bad_magic_number = False
            finally:
                file_name_lock.release_write_lock()

        file_name_lock.acquire_read_lock()
        try:

            comprec = Interpreter.CompileRecord(cid, csource, compiledto = object_file)
            self.reverse_lookup[object_file] = comprec

            if self._debug: self.debug("loading component from source file %s" % object_file, "classloading")
            module = importer.filemodule(object_file, id = cid, forcereload = force_reload)
            csource.module = module

            # attach the compile record to the module so it remains
            # referenced as long as the module does
            module.__compile = comprec
            
            # get the size of the source file and attach to the component source
            csource.modulesize = os.stat(object_file)[ST_SIZE]

            # check for bad magic number (incompatible compiler version), 
            # and recompile if needed
            if (
                not hasattr(module, '_MAGIC_NUMBER') or
                module._MAGIC_NUMBER != compiler.get_magic_number()
                ):

                # paranoid check against impossible endless loop
                if hasattr(csource, '_bad_magic_number') and csource._bad_magic_number:
                    raise "assertion failed: csource magic number check completed but recompile still produces bad magic number"

                # set a flag, we'll call again
                csource._bad_magic_number = True
            else:
                csource._bad_magic_number = False
        finally:
            file_name_lock.release_read_lock()

        if csource._bad_magic_number:
            return self.get_compiled_component(csource, always_recompile = always_recompile, recompile_newer = recompile_newer, use_file = True)
        else:
            return module.get_component(self, csource)
                    
    def _get_inmemory_component(self, csource, always_recompile = False, recompile_newer = True):
        """loads and compiles a file-based component as an in-memory module."""
        destbuf = None
    
        compiler = self.compiler.get()

        # the full module name of the component to be compiled
        cid = "_myghtycomp_" + re.sub(r"\W", "_", csource.path_id) + "_" + re.sub(r"\W", "_", csource.id)

        if self._debug: self.debug("compiling %s in memory" % csource.id, "classloading")
        destbuf = util.StringIO()
        csource.get_object_code(compiler, destbuf)

        filename = "memory:" + cid

        module = csource.module
            
        def needs_recompile():
            return (
                always_recompile or
                module is None 
                or 
                (recompile_newer and csource.last_modified > module._modified_time)
                )

        if needs_recompile():
            module = imp.new_module(cid)
            code = compile(destbuf.getvalue(), filename, 'exec')
            exec code in module.__dict__, module.__dict__
            module._modified_time = time.time()
            csource.module = module

        comprec = Interpreter.CompileRecord(cid, csource, compiledsource = destbuf.getvalue())
        self.reverse_lookup[filename] = comprec

        module.__compile = comprec
        csource.modulesize = len(destbuf.getvalue())
        
        csource._bad_magic_number = False

        return module.get_component(self, csource)

    def _file_exists(self, file):           
        return os.access(file, os.F_OK)
    
    def _need_file(self, modified_time, file):
        return (not os.access(file, os.F_OK) or
            modified_time > os.stat(file)[ST_MTIME] or
            os.stat(file)[ST_SIZE] == 0)

    def _verify_directory(self, dir):
        verify_directory(dir)


    def debug(self, message, type = None):
        """writes a debug message to the debug file.  the optional type string refers to a "debug_element" type,
        i.e. 'resolution', 'cache', etc. which will only write a message if that debug_element was 
        enabled with this Interpreter."""
        if type is None:
            self.log_file.write(message)
        else:
            log = self.debuggers.get(type, None)
            if log is not None: log(message)

    # deprecated 
    def get_attribute(self, key):
        """gets an attribute from this Interpreter.  deprecated, use the "attributes"
        member directly instead."""
        return self.attributes(key)
        
    def set_attribute(self, key, value):
        """sets an attribute on this Interpreter.  deprecated, use the "attributes"
        member directly instead."""
        self.attributes(key, value)

    def get_attributes(self):
        """returns the attributes dictionary for this Interpreter.  
        deprecated, use the "attributes" member directly instead."""
        return self.attributes()
