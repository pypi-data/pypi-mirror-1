# $Id: util.py 2133 2006-09-06 18:52:56Z dairiki $
# util.py - utility functions for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

__all__  = ["OrderedDict", "ThreadLocal", "Value", "InheritedDict", "ConstructorClone", "Registry", "WeakValuedRegistry", "SyncDict", "LRUCache", "argdict", "EncodedPath", "pid", "thread_id", "verify_directory", "PrefixArgs", "module", "StringIO"]

    
try:
    import thread as _thread
    import threading as _threading
except ImportError:
    import dummy_thread as _thread
    import dummy_threading as _threading

    
import weakref, inspect, sha, string, os, UserDict, copy, sys, imp, re, stat, types, time

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    
def thread_id():
    return _thread.get_ident()

def pid():
    return os.getpid()


def verify_directory(dir):
    """verifies and creates a directory.  tries to
    ignore collisions with other threads and processes."""

    tries = 0
    while not os.access(dir, os.F_OK):
        try:
            tries += 1
            os.makedirs(dir, 0750)
        except:
            if tries > 5:
                raise

def module(name):
    """imports a module, in the ordinary way, by string name"""
    
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


class argdict(dict):
    """supports the argument constructor form of dict which doesnt seem to 
    be present in python 2.2"""
    def __init__(self, **params):
        dict.__init__(self)
        self.update(params)



class Value:
    """allows pass-by-reference operations"""
    def __init__(self, value = None): self.value = value
    
    def __call__(self, *arg):
        if len(arg):
            self.assign(arg[0])
        else:
            return self.value

    def __str__(self):
        return str(self.value)

    def assign(self, value):
        self.value = value

    
class ThreadLocal:
    """stores a value on a per-thread basis"""
    def __init__(self, value = None, default = None, creator = None):
        self.dict = {}
        self.default = default
        self.creator = creator
        if value:
            self.put(value)

    def __call__(self, *arg):
        if len(arg):
            self.put(arg[0])
        else:
            return self.get()

    def __str__(self):
        return str(self.get())
    
    def assign(self, value):
        self.dict[_thread.get_ident()] = value
    
    def put(self, value):
        self.assign(value)
    
    def exists(self):
        return self.dict.has_key(_thread.get_ident())
            
    def get(self, *args, **params):
        if not self.dict.has_key(_thread.get_ident()):
            if self.default is not None: 
                self.put(self.default)
            elif self.creator is not None: 
                self.put(self.creator(*args, **params))
        
        return self.dict[_thread.get_ident()]
            
    def remove(self):
        del self.dict[_thread.get_ident()]
        
class OrderedDict(UserDict.DictMixin):
    """A Dictionary that keeps its own internal ordering"""
    def __init__(self, values = None):
        self.list = []
        self.dict = {}
        if values is not None:
            for val in values:
                self.update(val)

    def keys(self):
        return self.list
    
    def update(self, dict):
        for key in dict.keys():
            self.__setitem__(key, dict[key])
            
    def values(self):
        return map(lambda key: self[key], self.list)
        
    def __iter__(self):
        return iter(self.list)

    def itervalues(self):
        return iter([self[key] for key in self.list])
        
    def iterkeys(self):return self.__iter__()
    
    def iteritems(self):
        return iter([(key, self[key]) for key in self.keys()])
        
    def __delitem__(self, key):
        del self.dict[key]
        del self.list[self.list.index(key)]
        
    def __setitem__(self, key, object):
        if not self.has_key(key):
            self.list.append(key)

        self.dict.__setitem__(key, object)
        
    def __getitem__(self, key):
        return self.dict.__getitem__(key)

class InheritedDict(UserDict.DictMixin):
    """a dictionary that can defer lookups to a second dictionary
    if the key is not found locally."""

    def __init__(self, dict, superfunc):
        self.dict = dict
        self.superfunc = superfunc
        
    def __call__(self, key = None, value = None):
        if key is None and value is None:
            return self.dict
        elif value is None:
            try:
                return self.__getitem__(key)
            except KeyError:
                return None
        else:
            self.__setitem__(key, value)
                
    def __getitem__(self, key):
        dict = self.dict
        if dict.has_key(key): return dict[key]
        else:
            parent = self.superfunc()
            if parent is not None:
                return parent[key]

        raise KeyError(key)

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __delitem__(self, key):
        del self.dict[key]
        
    def keys(self):
        return self.dict.keys()
        
    def __contains__(self, key):
        return self.has_key(key)
        
    def has_key(self, key):
        if self.dict.has_key(key):
            return True
    
        parent = self.superfunc()
        if parent is not None:
            return parent.has_key(key)
            
        return False        

class ConstructorClone:
    """cloning methods that take additional parameters. one method is a straight shallow copy,
    the other recreates the object via its constructor.  both methods assume a relationship
    between the given parameters and the attribute names of the object."""
    
    def __init__(self, instance, **params):
        self.classobj = instance.__class__
        self.instance = instance
        self.params = params
        
    def copyclone(self):
        cl = copy.copy(self.instance)
        for key, value in self.params.iteritems():
            setattr(cl, key, value)
        return cl
        

    # store the argument specs in a static hash
    argspecs = {}

    def clone(self):
        """creates a new instance of the class using the regular class
        constructor.  the arguments to the constructor are divined from 
        inspecting the parameter names, and pulling those parameters from the
        original instance's attributes.

        this is essentially a quickie cheater way to get a clone of an object 
        if you can name your instance variables the same as that of the constructor
        arguments.  """
        
        key = self.classobj.__module__ + "." + self.classobj.__name__
        if not ConstructorClone.argspecs.has_key(key):
            argspec = inspect.getargspec(self.classobj.__init__.im_func)
    
            argnames = argspec[0] or []
            defaultvalues = argspec[3] or []
        
            (requiredargs, namedargs) = (
                    argnames[0:len(argnames) - len(defaultvalues)], 
                    argnames[len(argnames) - len(defaultvalues):]
                    )
                    
            ConstructorClone.argspecs[key] = (requiredargs, namedargs)
            
        (requiredargs, namedargs) = ConstructorClone.argspecs[key]
        
        newargs = []
        newparams = {}
        addlparams = self.params.copy()
        
        for arg in requiredargs:
            if arg == 'self': continue
            elif self.params.has_key(arg):
                newargs.append(self.params[arg])
            else:
                newargs.append(getattr(self.instance, arg))

            if addlparams.has_key(arg): del addlparams[arg]

        for arg in namedargs:
            if addlparams.has_key(arg): del addlparams[arg]
            
            if self.params.has_key(arg):
                newparams[arg] = self.params[arg]
            else:
                if hasattr(self.instance, arg):
                    newparams[arg] = getattr(self.instance, arg)
                else:
                    raise "instance has no attribute '%s'" % arg

        newparams.update(addlparams)
            
        return self.classobj(*newargs, **newparams)
    
class PrefixArgs:
    """extracts from the given argument dictionary all values with a key '<prefix><key>'
    and stores a reference.  """
    
    def __init__(self, prefix):
        self.prefix = prefix
        self.params = {}
        self.prelen = len(prefix)


    def set_prefix_params(self, **params):      
        """from the given dictionary, copies all values with keys in the 
        form "<prefix><key>" to this one."""
        for key, item in params.iteritems():
            if key[0:self.prelen] == self.prefix:
                self.params[key[self.prelen:]] = item

    def set_params(self, **params):
        """from the given dictionary, copies all key/values to this one."""
        
        self.params.update(params)
    
    def get_params(self, **params):
        """returns a new dictionary
        with this object's values plus those in the given dictionary,
        with prefixes stripped from the keys."""
        
        p = self.params.copy()
        for key, item in params.iteritems():
            if key[0:self.prelen] == self.prefix:
                p[key[self.prelen:]] = item
            else:
                p[key] = item
        return p
                                        



class SyncDict:
    """
    an efficient/threadsafe singleton map algorithm, a.k.a.
    "get a value based on this key, and create if not found or not valid" paradigm:
    
        exists && isvalid ? get : create

    works with weakref dictionaries and the LRUCache to handle items asynchronously 
    disappearing from the dictionary.  

    use python 2.3.3 or greater !  a major bug was just fixed in Nov. 2003 that
    was driving me nuts with garbage collection/weakrefs in this section.
    """
    
    def __init__(self, mutex, dictionary):
        self.mutex = mutex
        self.dict = dictionary
        
    def get(self, key, createfunc, mutex = None, isvalidfunc = None):
        """regular get method.  returns the object asynchronously, if present
        and also passes the optional isvalidfunc,
        else defers to the synchronous get method which will create it."""
        try:
            if self.has_key(key):
                return self._get_obj(key, createfunc, mutex, isvalidfunc)
            else:
                return self.sync_get(key, createfunc, mutex, isvalidfunc)
        except KeyError:
            return self.sync_get(key, createfunc, mutex, isvalidfunc)

    def sync_get(self, key, createfunc, mutex = None, isvalidfunc = None):
        if mutex is None: mutex = self.mutex

        mutex.acquire()
        try:
            try:
                if self.has_key(key):
                    return self._get_obj(key, createfunc, mutex, isvalidfunc, create = True)
                else:
                    return self._create(key, createfunc)
            except KeyError:
                return self._create(key, createfunc)
        finally:
            mutex.release()

    def _get_obj(self, key, createfunc, mutex, isvalidfunc, create = False):
        obj = self[key]
        if isvalidfunc is not None and not isvalidfunc(obj):
            if create:
                return self._create(key, createfunc)
            else:
                return self.sync_get(key, createfunc, mutex, isvalidfunc)
        else:
            return obj
    
    def _create(self, key, createfunc):
        obj = createfunc()
        self[key] = obj
        return obj

    def has_key(self, key):
        return self.dict.has_key(key)
    def __contains__(self, key):
        return self.dict.__contains__(key)
    def __getitem__(self, key):
        return self.dict.__getitem__(key)
    def __setitem__(self, key, value):
        self.dict.__setitem__(key, value)
    def __delitem__(self, key):
        return self.dict.__delitem__(key)
    

class Registry(SyncDict):
    """a registry object."""
    def __init__(self):
        SyncDict.__init__(self, _threading.Lock(), {})

class WeakValuedRegistry(SyncDict):
    """a registry that stores objects only as long as someone has a reference to them."""
    def __init__(self):
        # weakrefs apparently can trigger the __del__ method of other
        # unreferenced objects, when you create a new reference.  this can occur
        # when you place new items into the WeakValueDictionary.  if that __del__
        # method happens to want to access this same registry, well, then you need
        # the RLock instead of a regular lock, since at the point of dictionary
        # insertion, we are already inside the lock.
        SyncDict.__init__(self, _threading.RLock(), weakref.WeakValueDictionary())

class LRUCache(SyncDict):
    """a cache (mapping class) that stores only a certain number of elements, and discards
    its least recently used element when full."""
    
    class ListElement:
        def __init__(self, key, value):
            self.key = key
            self.setvalue(value)
                    
        def setvalue(self, value):          
            self.value = value

            if hasattr(value, 'size'):
                self.size = value.size
            else:
                self.size = 1
            
    def __init__(self, size, deletefunc = None, sizethreshhold = .2):
        SyncDict.__init__(self, _threading.Lock(), {})
        self.size = size
        self.maxelemsize = sizethreshhold * size
        self.head = None
        self.tail = None
        self.deletefunc = deletefunc
        self.currentsize = 0
        
        # inner mutex to synchronize list manipulation 
        # operations independently of the SyncDict
        self.listmutex = _threading.Lock()  
        
    def __setitem__(self, key, value):
        self.listmutex.acquire()
        try:
            existing = self.dict.get(key, None)

            if existing is None:
                element = LRUCache.ListElement(key, value)
                #if element.size > self.maxelemsize: return
                self.dict[key] = element
                self._insertElement(element)
            else:
                #if element.size > self.maxelemsize: 
                    #del self.dict[key]
                    #self._removeElement(element)
                oldsize = existing.size
                existing.setvalue(value)
                self.currentsize += (existing.size - oldsize)

                self._updateElement(existing)
                self._manageSize()
        finally:
            self.listmutex.release()
    
    def __getitem__(self, key):
        self.listmutex.acquire()
        try:
            element = self.dict[key]
            self._updateElement(element)
            return element.value
        finally:
            self.listmutex.release()
            

    def __contains__(self, key):
        return self.dict.has_key(key)

    def has_key(self, key):
        return self.dict.has_key(key)
        
    def _insertElement(self, element):
        # zero-length elements are not managed in the LRU queue since they
        # have no affect on the total size
        if element.size == 0:
            return
            
        element.previous = None
        element.next = self.head

        if self.head is not None:
            self.head.previous = element
        else:
            self.tail = element

        self.head = element

        self.currentsize += element.size
        
        self._manageSize()

    def _manageSize(self):      
        # TODO: dont remove one element at a time, remove the 
        # excess in one step
        while self.currentsize  > self.size:
            oldelem = self.dict[self.tail.key]
            if self.deletefunc is not None:
                self.deletefunc(oldelem.value)
            self.currentsize -= oldelem.size
            del self.dict[self.tail.key]
            if self.tail != self.head:
                self.tail = self.tail.previous
                self.tail.next = None
            else:
                self.tail = None
                self.head = None
                
    def _updateElement(self, element):
        # zero-length elements are not managed in the LRU queue since they
        # have no affect on the total size
        if element.size == 0:
            return

        if self.head == element: return
    
        e = element.previous

        e.next = element.next

        if element.next is not None:
            element.next.previous = e
        else:
            self.tail = e

        element.previous = None
        element.next = self.head

        self.head.previous = element

        self.head = element

    # TODO: iteration
            
class EncodedPath:
    """generates a unique file-accessible path from the given list of identifiers
    starting at the given root directory."""
    def __init__(self, root, identifiers, extension = ".enc", depth = 3, verify = True, digest = True):
        ident = string.join(identifiers, "_")

        if digest:
            ident = sha.new(ident).hexdigest()

        tokens = []
        for d in range(1, depth):
            tokens.append(ident[0:d])
        
        dir = os.path.join(root, *tokens)
        if verify:
            verify_directory(dir)
        
        self.dir = dir
        self.path = os.path.join(dir, ident + extension)

    def verify_directory(self):
        verify_directory(self.dir)
        
    def get_path(self):
        return self.path



        
