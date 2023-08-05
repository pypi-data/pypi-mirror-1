# $Id: container.py 2133 2006-09-06 18:52:56Z dairiki $
# container.py - file/memory data containment API and implementation for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
# 


import os.path, re, string, time, weakref, sys
from myghty.util import *
from myghty import exception
from myghty.synchronization import *
import cPickle


__all__ = ['NamespaceContext', 'ContainerContext', 'Container', 'MemoryContainer', 'DBMContainer',
    'NamespaceManager', 'MemoryNamespaceManager', 'DBMNamespaceManager', 'FileContainer', 'FileNamespaceManager', 
    'CreationAbortedError', 'container_registry']


def container_registry(name, classtype):
    if name.startswith('ext:'):
        name = name[4:]
        modname = "myghty.ext." + name 
        mod = getattr(__import__(modname).ext, name)
    else:
        mod = sys.modules[__name__]

    cname = string.capitalize(name) + classtype
    return getattr(mod, cname)
    
class NamespaceContext:
    """initial context supplied to NamespaceManagers"""
    
    def __init__(self, log_file = None):
        self.log_file = log_file

    def debug(self, message, nsm, container = None):
        if self.log_file is not None: 
            if container is not None:
                message = "[%s:%s:%s] %s\n" % (container.__class__.__name__, nsm.namespace, container.key, message)
            else:
                message = "[%s] %s\n" % (nsm.namespace, message)

            self.log_file.write(message)


class NamespaceManager:
    """handles dictionary operations and locking for a namespace of values.  
    
    the implementation for setting and retrieving the namespace data is handled
    by subclasses.
    
    acts as a service for a Container, which stores and retreives a particular
    key from the namespace, coupled with a "stored time" setting.

    NamespaceManager may be used alone, or may be privately managed by
    one or more Container objects.  Container objects provide per-key services
    like automatic expiration and recreation of individual keys and can manange
    many types of NamespaceManagers for one or more particular 
    namespaces simultaneously.  
    
    the class supports locking relative to its name.  many namespacemanagers within
    multiple threads or across multiple processes must read/write synchronize their 
    access to the actual dictionary of data referenced by the name.     
    """
    
    def __init__(self, context , namespace, **params):
        # caution: this might create a circular reference
        # (which was giving me very weird gc() problems 
        # in previous configurations)
        self.context = context
        
        self.namespace = namespace
        self.openers = 0
        self.mutex = _threading.Lock()
        
    def do_acquire_read_lock(self): raise NotImplementedError()
    def do_release_read_lock(self): raise NotImplementedError()
    def do_acquire_write_lock(self, wait = True): raise NotImplementedError()
    def do_release_write_lock(self): raise NotImplementedError()

    def do_open(self, flags): raise NotImplementedError()
    def do_close(self): raise NotImplementedError()

    def do_remove(self):
        """removes this namespace from wherever it is stored"""
        raise NotImplementedError()

    def has_key(self, key):
        return self.__contains__(key)

    def __getitem__(self, key):
        raise NotImplementedError()
        
    def __setitem__(self, key, value):
        raise NotImplementedError()
        
    def __contains__(self, key):
        raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()

    def keys(self):
        raise NotImplementedError()

    def acquire_read_lock(self): 
        """acquires a read lock for this namespace, and 
        insures that the datasource has been opened for reading
        if it is not already opened.
        
        acquire/release supports reentrant/nested operation."""
        
        self.do_acquire_read_lock()
        self.open('r', checkcount = True)
        
    def release_read_lock(self):
        """releases the read lock for this namespace, and possibly
        closes the datasource, if it was opened as a product of
        the read lock's acquire/release block. 

        acquire/release supports reentrant/nested operation."""
    
        self.close(checkcount = True)
        self.do_release_read_lock()
        
    def acquire_write_lock(self, wait = True): 
        """acquires a write lock for this namespace, and 
        insures that the datasource has been opened for writing if
        it is not already opened.

        acquire/release supports reentrant/nested operation."""
        
        r = self.do_acquire_write_lock(wait)
        if (wait or r): self.open('c', checkcount = True)
        return r
        
    def release_write_lock(self): 
        """releases the write lock for this namespace, and possibly
        closes the datasource, if it was opened as a product of
        the write lock's acquire/release block. 

        acquire/release supports reentrant/nested operation."""

        self.close(checkcount = True)
        self.do_release_write_lock()

    def open(self, flags, checkcount = False):
        """opens the datasource for this namespace.
        
        the checkcount flag indicates an "opened" counter
        should be checked for zero before performing the open operation,
        which is incremented by one regardless."""
        
        self.mutex.acquire()
        try:
            if checkcount:
                if self.openers == 0: self.do_open(flags)
                self.openers += 1
            else:
                self.do_open(flags)
                self.openers = 1
        finally:
            self.mutex.release()

    def close(self, checkcount = False):
        """closes the datasource for this namespace.
        
        the checkcount flag indicates an "opened" counter should be
        checked for zero before performing the close operation, which
        is otherwise decremented by one."""
        
        self.mutex.acquire()
        try:
            if checkcount:
                self.openers -= 1
                if self.openers == 0: self.do_close()
            else:
                if self.openers > 0:
                    self.do_close()
                self.openers = 0
        finally:
            self.mutex.release()

        
    def remove(self):
        self.do_acquire_write_lock()
        try:
            self.close(checkcount = False)
            self.do_remove()
        finally:
            self.do_release_write_lock()
            
    def debug(self, message, container = None):
        self.context.debug(message, self, container)    



class ContainerContext(NamespaceContext):
    """initial context supplied to Containers. 
    
    Keeps track of namespacemangers keyed off of namespace names and container types.

    also keeps namespacemanagers thread local for nsm instances that arent threadsafe
    (i.e. gdbm)
    """
    
    def __init__(self, log_file = None):
        NamespaceContext.__init__(self, log_file)
        self.registry = {}
        
    def get_namespace_manager(self, namespace, container, **params):
        key = str(_thread.get_ident()) + "|" + container.__class__.__name__ + "|" + namespace
        try:
            return self.registry[key]
        except KeyError:
            return self.registry.setdefault(key, self.create_nsm(namespace, container, **params))
    
    

    def create_nsm(self, namespace, container, **params):
        nsm = container.do_create_namespace_manager(context = self, namespace = namespace, **params)
        return nsm
        


class Container:
    """represents a value, its stored time, and a value creation function corresponding to 
    a particular key in a particular namespace.
    
    handles storage and retrieval of its value via a single NamespaceManager, as well as handling
    expiration times and an optional creation function that can create or recreate its value
    when needed.
    
    the Container performs locking operations on the NamespaceManager, including a
    pretty intricate one for get_value with a creation function, so its best not
    to pass a NamespaceManager that has been externally locked or open, as it stands
    currently (i hope to improve on this).
    
    Managing multiple Containers for a set of keys within a certain namespace allows 
    management of multiple namespace implementations, expiration properties, 
    and thread/process synchronization, on a per-key basis.
    """
    
    def __init__(self, key, context, namespace, createfunc = None, expiretime = None, starttime = None, **params):
        """create a container that stores one cached object.
        
        createfunc - a function that will create the value.  this function is called
        when value is None or expired.  the createfunc 
        call is also synchronized against any other threads or processes calling this 
        cache.
        expiretime - time in seconds that the item expires.
        """
        self.key = key
        self.createfunc = createfunc
        self.expiretime = expiretime
        self.starttime = starttime
        self.storedtime = -1
        self.namespacemanager = context.get_namespace_manager(namespace, self, **params)
        self.do_init(**params)



    def acquire_read_lock(self):
        self.namespacemanager.acquire_read_lock()
        
    def release_read_lock(self):
        self.namespacemanager.release_read_lock()
        
    def acquire_write_lock(self, wait = True):
        return self.namespacemanager.acquire_write_lock(wait)
        
    def release_write_lock(self):
        self.namespacemanager.release_write_lock()
    
    def debug(self, message):
        self.namespacemanager.debug(message, self)

    def do_create_namespace_manager(self, context, namespace, **params): 
        """subclasses should return a newly created instance of their 
        corresponding NamespaceManager."""
        raise NotImplementedError()
    
    def do_init(self, **params): 
        """subclasses can perform general initialization.
        
        optional template method."""
        pass

    def do_get_value(self):
        """retrieves the native stored value of this container, regardless of if its
        expired, or raise KeyError if no value is defined.
        optionally a template method."""
    
        return self.namespacemanager[self.key]  
    
    def do_set_value(self, value):
        """sets the raw value in this container.
        optionally a template method."""
        self.namespacemanager[self.key] = value
        
    def do_clear_value(self):
        """clears the value of this container.  
        
        subsequent do_get_value calls should raise KeyError.
        optionally a template method."""
        
        if self.namespacemanager.has_key(self.key):
            del self.namespacemanager[self.key]
            
        
    def has_value(self):
        """returns true if the container has a value stored, 
        regardless of it being expired or not.
        
        optionally a template method."""

        self.acquire_read_lock()
        try:    
            return self.namespacemanager.has_key(self.key)
        finally:
            self.release_read_lock()
    

    def lock_createfunc(self, wait = True): 
        """required template method that locks this container's namespace and key
        to allow a single execution of the creation function."""
        
        raise NotImplementedError()
        
    def unlock_createfunc(self): 
        """required template method that unlocks this container's namespace and key
        when the creation function is complete."""
        
        raise NotImplementedError()
    
    def can_have_value(self):
        """returns true if this container either has a non-expired value, or is capable of creating one
        via a creation function"""
        return self.has_current_value() or self.createfunc is not None  

    def has_current_value(self):
        """returns true if this container has a non-expired value"""
        return self.has_value() and not self.is_expired()

    def stored_time(self):
        return self.storedtime

    def get_namespace_manager(self):
        return self.namespacemanager
    
    def get_all_namespaces(self):
        return self.namespacemanager.context._container_namespaces.values()
        
    def is_expired(self):
        """returns true if this container's value is expired, based
        on the last time get_value was called."""
        
        return (
            (
                self.storedtime == -1
            )
            or
            (
                self.starttime is not None and
                self.storedtime < self.starttime
            )
            or
            (
                self.expiretime is not None and
                time.time() >= self.expiretime + self.storedtime
            )
        )

    def get_value(self):
        """get_value performs a get with expiration checks on its namespacemanager.
        if a creation function is specified, a new value will be created if the 
        existing value is nonexistent or has expired."""
        
        self.acquire_read_lock()
        try:
            has_value = self.has_value()
            if has_value:
                [self.storedtime, value] = self.do_get_value()
                if not self.is_expired():
                    return value
    
            if not self.can_have_value():
                raise KeyError(self.key)


        finally:
            self.release_read_lock()

        has_createlock = False
        if has_value:
            if not self.lock_createfunc(wait = False):
                self.debug("get_value returning old value while new one is created")
                return value
            else:
                self.debug("lock_creatfunc (didnt wait)")
                has_createlock = True

        if not has_createlock:
            self.debug("lock_createfunc (waiting)")
            self.lock_createfunc()
            self.debug("lock_createfunc (waited)")

        try:
            # see if someone created the value already
            self.acquire_read_lock()
            try:
                if self.has_value():
                    [self.storedtime, value] = self.do_get_value()
                    if not self.is_expired():
                        return value
            finally:
                self.release_read_lock()

            self.debug("get_value creating new value")
            try:
                v = self.createfunc()
            except CreationAbortedError, e:
                raise
                
            self.set_value(v)
            
            return v
        finally:
            self.unlock_createfunc()
            self.debug("unlock_createfunc")
                
            
    def set_value(self, value):
        self.acquire_write_lock()
        try:
            self.storedtime = time.time()
            self.debug("set_value stored time %d" % self.storedtime)
            self.do_set_value([self.storedtime, value])
        finally:
            self.release_write_lock()

    def clear_value(self):
        self.acquire_write_lock()
        try:
            self.debug("clear_value")
            self.do_clear_value()
            self.storedtime = -1
        finally:
            self.release_write_lock()
        
class CreationAbortedError(Exception):
    """a special exception that allows a creation function to abort what its doing"""
    
    def __init__(self, **params):
        self.params = params
        




class MemoryNamespaceManager(NamespaceManager):
    namespaces = SyncDict(_threading.Lock(), {})

    def __init__(self, context, namespace, **params):
        NamespaceManager.__init__(self, context, namespace, **params)

        self.lock = Synchronizer(identifier = "memorycontainer/namespacelock/%s" % self.namespace, use_files = False)
        
        self.dictionary = MemoryNamespaceManager.namespaces.get(self.namespace, lambda: {})
        
    def do_acquire_read_lock(self): self.lock.acquire_read_lock()
    def do_release_read_lock(self): self.lock.release_read_lock()
    def do_acquire_write_lock(self, wait = True): return self.lock.acquire_write_lock(wait)
    def do_release_write_lock(self): self.lock.release_write_lock()

    # the open and close methods are totally overridden to eliminate
    # the unnecessary "open count" computation involved
    def open(self, *args, **params):pass
    def close(self, *args, **params):pass
    
    def __getitem__(self, key): return self.dictionary[key]

    def __contains__(self, key): 
        return self.dictionary.__contains__(key)

    def has_key(self, key): 
        return self.dictionary.__contains__(key)
        
    def __setitem__(self, key, value):self.dictionary[key] = value
    
    def __delitem__(self, key):
        del self.dictionary[key]

    def do_remove(self):
        self.dictionary.clear()
        
    def keys(self):
        return self.dictionary.keys()


class MemoryContainer(Container):

    def do_init(self, **params):
        self.funclock = None
    
    def do_create_namespace_manager(self, context, namespace, **params):
        return MemoryNamespaceManager(context, namespace, **params)
        
    def lock_createfunc(self, wait = True): 
        if self.funclock is None:
            self.funclock = NameLock(identifier = "memorycontainer/funclock/%s/%s" % (self.namespacemanager.namespace, self.key), reentrant = True)
            
        return self.funclock.acquire(wait)

    def unlock_createfunc(self): self.funclock.release()


class DBMNamespaceManager(NamespaceManager):

    def __init__(self, context, namespace, dbmmodule = None, data_dir = None, dbm_dir = None, lock_dir = None, digest_filenames = True, **params):
        NamespaceManager.__init__(self, context, namespace, **params)

        if dbm_dir is not None:
            self.dbm_dir = dbm_dir
        elif data_dir is None:
            raise "data_dir or dbm_dir is required"
        else:
            self.dbm_dir = data_dir + "/container_dbm"
        
        if lock_dir is not None:
            self.lock_dir = lock_dir
        elif data_dir is None:
            raise "data_dir or lock_dir is required"
        else:
            self.lock_dir = data_dir + "/container_dbm_lock"

        if dbmmodule is None:
            import anydbm
            self.dbmmodule = anydbm
        else:
            self.dbmmodule = dbmmodule
        
        verify_directory(self.dbm_dir)
        verify_directory(self.lock_dir)

        self.dbm = None

        self.lock = Synchronizer(identifier = self.namespace, use_files = True, lock_dir = self.lock_dir, digest_filenames = digest_filenames)
        self.encpath = EncodedPath(root = self.dbm_dir, identifiers = [self.namespace], digest = digest_filenames, extension = '.dbm')
        self.file = self.encpath.path
        
        self.debug("data file %s" % self.file)
        
        self._checkfile()

    def file_exists(self, file):
        if os.access(file, os.F_OK): return True
        else:
            for ext in ('db', 'dat', 'pag', 'dir'):
                if os.access(file + os.extsep + ext, os.F_OK):
                    return True
                    
        return False
    
    def _checkfile(self):
        if not self.file_exists(self.file):
            g = self.dbmmodule.open(self.file, 'c') 
            g.close()
                
    def get_filenames(self):
        list = []
        if os.access(self.file, os.F_OK):
            list.append(self.file)
            
        for ext in ('pag', 'dir', 'db', 'dat'):
            if os.access(self.file + os.extsep + ext, os.F_OK):
                list.append(self.file + os.extsep + ext)
        return list
        

    def do_acquire_read_lock(self): 
        self.lock.acquire_read_lock()
        
    def do_release_read_lock(self): 
        self.lock.release_read_lock()
        
    def do_acquire_write_lock(self, wait = True): 
        return self.lock.acquire_write_lock(wait)
        
    def do_release_write_lock(self): 
        self.lock.release_write_lock()

    def do_open(self, flags):
        # caution: apparently gdbm handles arent threadsafe, they 
        # are using flock(), and i would rather not have knowledge
        # of the "unlock" 'u' option just for that one dbm module.
        # therefore, neither is an individual instance of
        # this namespacemanager (of course, multiple nsm's
        # can exist for each thread).
        self.debug("opening dbm file %s" % self.file)
        try:
            self.dbm = self.dbmmodule.open(self.file, flags)
        except:
            self.encpath.verify_directory()
            self._checkfile()
            self.dbm = self.dbmmodule.open(self.file, flags)

    def do_close(self):
        if self.dbm is not None:
            self.debug("closing dbm file %s" % self.file)
            self.dbm.close()
        
    def do_remove(self):
        for f in self.get_filenames():
            os.remove(f)
        
    def __getitem__(self, key): 
        return cPickle.loads(self.dbm[key])

    def __contains__(self, key): 
        return self.dbm.has_key(key)
        
    def __setitem__(self, key, value):
        self.dbm[key] = cPickle.dumps(value, cPickle.HIGHEST_PROTOCOL)

    def __delitem__(self, key):
        del self.dbm[key]

    def keys(self):
        return self.dbm.keys()
        


class DBMContainer(Container):

    def do_init(self, **params):
        self.funclock = None
        
    def do_create_namespace_manager(self, context, namespace, **params):
        return DBMNamespaceManager(context, namespace, **params)
    
    def lock_createfunc(self, wait = True): 
        if self.funclock is None:
            self.funclock = Synchronizer(identifier = "dbmcontainer/funclock/%s" % self.namespacemanager.namespace, use_files = True, lock_dir = self.namespacemanager.lock_dir)
        
        return self.funclock.acquire_write_lock(wait)

    def unlock_createfunc(self): self.funclock.release_write_lock()
    
DbmNamespaceManager = DBMNamespaceManager
DbmContainer = DBMContainer


class FileNamespaceManager(NamespaceManager):

    def __init__(self, context, namespace, data_dir = None, file_dir = None, lock_dir = None, digest_filenames = True, **params):
        NamespaceManager.__init__(self, context, namespace, **params)

        if file_dir is not None:
            self.file_dir = file_dir
        elif data_dir is None:
            raise "data_dir or file_dir is required"
        else:
            self.file_dir = data_dir + "/container_file"
        
        if lock_dir is not None:
            self.lock_dir = lock_dir
        elif data_dir is None:
            raise "data_dir or lock_dir is required"
        else:
            self.lock_dir = data_dir + "/container_file_lock"

        verify_directory(self.file_dir)
        verify_directory(self.lock_dir)

        self.lock = Synchronizer(identifier = self.namespace, use_files = True, lock_dir = self.lock_dir, digest_filenames = digest_filenames)
        self.file = EncodedPath(root = self.file_dir, identifiers = [self.namespace], digest = digest_filenames, extension = '.cache').path
        self.hash = {}
        
        self.debug("data file %s" % self.file)
        
    def file_exists(self, file):
        if os.access(file, os.F_OK): return True
        else: return False
            

    def do_acquire_read_lock(self): 
        self.lock.acquire_read_lock()
        
    def do_release_read_lock(self): 
        self.lock.release_read_lock()
        
    def do_acquire_write_lock(self, wait = True): 
        return self.lock.acquire_write_lock(wait)
        
    def do_release_write_lock(self): 
        self.lock.release_write_lock()

    def do_open(self, flags):
        if self.file_exists(self.file):
            fh = open(self.file, 'r')
            self.hash = cPickle.load(fh)
            fh.close()
        self.flags = flags
        
    def do_close(self):
        if self.flags is not None and (self.flags == 'c' or self.flags == 'w'):
            fh = open(self.file, 'w')
            cPickle.dump(self.hash, fh, cPickle.HIGHEST_PROTOCOL)
            fh.close()

        self.flags = None
                
    def do_remove(self):
        os.remove(self.file)
        self.hash = {}
        
    def __getitem__(self, key): 
        return self.hash[key]

    def __contains__(self, key): 
        return self.hash.has_key(key)
        
    def __setitem__(self, key, value):
        self.hash[key] = value

    def __delitem__(self, key):
        del self.hash[key]

    def keys(self):
        return self.hash.keys()
        


class FileContainer(Container):

    def do_init(self, **params):
        self.funclock = None
        
    def do_create_namespace_manager(self, context, namespace, **params):
        return FileNamespaceManager(context, namespace, **params)
    
    def lock_createfunc(self, wait = True): 
        if self.funclock is None:
            self.funclock = Synchronizer(identifier = "filecontainer/funclock/%s" % self.namespacemanager.namespace, use_files = True, lock_dir = self.namespacemanager.lock_dir)
        
        return self.funclock.acquire_write_lock(wait)

    def unlock_createfunc(self): self.funclock.release_write_lock()



        
