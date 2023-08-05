# $Id: importer.py 2013 2005-12-31 03:19:39Z zzzeek $
# importer.py - Myghty memory-managed module importer
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

import string, os, sys, imp, re, stat, types, time, weakref, __builtin__

"""
module loading and management.  loads modules by file paths directly, as well
as via module names.  keeps track of last modified time to provide a "reasonable"
level of "reload when changed" behavior without restarting the application.  By 
"reasonable" we include the module itself, but not its parent package or any 
of its named dependencies.

in the case of file-based modules, which correspond to compiled templates as well
as module components resolved via file paths, they are kept out
of sys.modules so they can be cleanly reloaded when modified, and removed from 
memory when they fall out of scope.   To maintain "importability" of these 
modules, the builtin __import__ method is overridden application-wide to 
search for these modules in a local weak dictionary first before proceeding to 
normal import behavior.

in the case of modules located by a package/module name, 
they are loaded into sys.modules via the default __import__ method
and are reloaded via reload().  For these modules, the "singleton" behavior of 
Python's regular module system applies.  This behavior includes the caveats that old 
attributes stay lying around, and the module is reloaded "in place" which in rare 
circumstances could affect code executing against the module.  The advantage is that
the module's parent packages all remain pointing to the correctly reloaded module 
and no exotic synchronization-intensive "reconnection" of newly reloaded modules 
to their packages needs to happen.

The "importability" of a module loaded here is usually not even an issue as it
typcially is only providing Myghty components which are solely invoked by the Interpreter.
However, in addition to the case where the developer is explicitly importing 
from a module that also provides Myghty components, the other case when the module requires 
import is when a class defined within it is deserialized, such as from a cache or session 
object; hence the need to override __import__ as well as maintaining the structure
of packages.  

"""

modules = weakref.WeakValueDictionary()

# override __import__ to look in our own local module dict first
builtin_importer = __builtin__.__import__
def import_module(name, globals = None, locals = None, fromlist = None):
    try:
        return modules[name].module
    except KeyError:
        return builtin_importer(name, globals, locals, fromlist)

__builtin__.__import__ = import_module

class ModValue:
    """2.3 is not letting us make a weakref to a module.  so create a lovely 
    circular reference thingy and weakref to that."""
    def __init__(self, module):
        self.module = module
        module.__modvalue__ = self

def module(name):
    """imports a module by string name via normal module importing, attaches timestamp information"""
    if name == '__main__':
        return sys.modules[name]
    mod = builtin_importer(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
        
    if not hasattr(mod, "__modified_time"):
        mod.__modified_time = modulemodtime(mod)
        
    mod.__is_file = False
    return mod

def filemodule(path, id = None, reload = True, forcereload = False):
    """loads a module directly from a file path."""
    
    if id is None:
        id = re.sub(r'\W+','_',path)

    if not forcereload:
        try:
            module = modules[id].module
            if not reload or module.__modified_time >= modulemodtime(module):
                return module
        except KeyError:
            pass
        
    modfile = open(path, 'r')
    try:
        #print "loading: " + path

        # Check mtime before loading module, so that modified_time
        # is guaranteed not to be later than the mtime of the loaded
        # version of the file.
        modified_time = os.fstat(modfile.fileno())[stat.ST_MTIME]
        module = imp.load_source(id, path, modfile)
        del sys.modules[id]
        modules[id] = ModValue(module)
        module.__modified_time = modified_time
        module.__is_file = True
        return module
    finally:
        modfile.close()


def reload_module(module):
    """reloads any module that was loaded with filemodule(), if its 
    modification time has changed.
    """    
    
    if not hasattr(module, '__modified_time'):
        # if we didnt load it, we dont change it
        return module
    elif module.__modified_time < modulemodtime(module):
        if module.__is_file is False:
            #print "regular reload: " + module.__name__
            # Get mtime before reload to ensure it is <= the actual mtime
            # of the reloaded module.
            modified_time = modulemodtime(module)
            reload(module)
            module.__modified_time = modified_time
            return module
        else:
            file = module.__file__
            file = re.sub(r'\.pyc$|\.pyo$', '.py', file)
            return filemodule(file, id = module.__name__, forcereload = True)
    else:
        return module
        

def mod_time(module):
    try:
        return module.__modified_time
    except AttributeError:
        return modulemodtime(module)

def modulemodtime(module):
    """returns the modified time of a module's source file"""
    try:
        file = module.__file__
        pyfile = re.sub(r'\.pyc$|\.pyo$', '.py', file)
        if os.access(pyfile, os.F_OK): 
            file = pyfile

        #print "checking time on " + file
        st = os.stat(file)
        return st[stat.ST_MTIME]
    except AttributeError:
        return None

    

class ObjectPathIterator:
    """walks a file path looking for a python module.  once it loads the
    python module, then continues walking the path into module's attributes."""
    
    def __init__(self, path, reload = True):
        self.path = path
        self.reload = reload
        self.module = None
        self.objpath = []
        if isinstance(path, types.ModuleType):
            self.module = path
            if reload:
                reload_module(self.module)
            self.last_modified = None
            
    def get_unit(self, tokens, stringtokens = [], moduletokens = []):
        if isinstance(self.path, str):
            return self.get_string_unit(tokens + stringtokens)
        else:
            return self.get_attr_unit(tokens + moduletokens)
        
    def get_string_unit(self, tokens):
        for token in tokens:
            path = self.path + "/" + token

            #print "check path " + repr(path)
            if self._check_module(path):
                return (self.path, token)
                
            if not os.access(path, os.F_OK):
                continue

            self.path = path
            return (self.path, token)
        else:
            raise StopIteration
            
    def get_attr_unit(self, tokens):
        for token in tokens:
            try:
                #print "check attr path " + repr(self.path) + " " + token
                attr = getattr(self.path, token)
                if isinstance(attr, types.ModuleType):
                    raise AttributeError(token)
                self.path = attr
                self.objpath.append(token)
                return (self.path, token)
            except AttributeError:
                continue
        else:
            self.path = None
            raise StopIteration
            
    def _check_module(self, path):
        try:
            st = os.stat(path + ".py")
        except OSError:
            return False

        if stat.S_ISREG(st[stat.ST_MODE]):
            self.path = filemodule(path + ".py", reload = self.reload)
            self.module = self.path
            self.last_modified = mod_time(self.module)
            return True
