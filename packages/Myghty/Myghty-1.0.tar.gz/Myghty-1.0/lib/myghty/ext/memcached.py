import memcache
from myghty.synchronization import *
from myghty.container import NamespaceManager, Container

import sys

class MemcachedNamespaceManager(NamespaceManager):

    def __init__(self, context, namespace, url, **params):
        NamespaceManager.__init__(self, context, namespace, **params)
        self.mc = memcache.Client([url], debug=0)

    # memcached does its own locking.  override our own stuff
    def do_acquire_read_lock(self): pass
    def do_release_read_lock(self): pass
    def do_acquire_write_lock(self, wait = True): return True
    def do_release_write_lock(self): pass

    # override open/close to do nothing, keep memcache connection open as long
    # as possible
    def open(self, *args, **params):pass
    def close(self, *args, **params):pass

    def __getitem__(self, key):
        value = self.mc.get(self.namespace + "_" + key)
        if value is None:
            raise KeyError(key)
        return value

    def __contains__(self, key):
        return self.mc.get(self.namespace + "_" + key) is not None

    def has_key(self, key):
        return self.mc.get(self.namespace + "_" + key) is not None

    def __setitem__(self, key, value):
        keys = self.mc.get(self.namespace + ':keys')
        if keys is None:
            keys = {}
        keys[key] = True
        self.mc.set(self.namespace + ':keys', keys)
        self.mc.set(self.namespace + "_" + key, value)

    def __delitem__(self, key):
        keys = self.mc.get(self.namespace + ':keys')
        try:
            del keys[key]
            self.mc.delete(self.namespace + "_" + key)
            self.mc.set(self.namespace + ':keys', keys)
        except KeyError:
            raise

    def do_remove(self):
        pass

    def keys(self):
        keys = self.mc.get(self.namespace + ':keys')
        if keys is None:
            return []
        else:
            return keys.keys()

class MemcachedContainer(Container):

    def do_init(self, **params):
        self.funclock = None

    def do_create_namespace_manager(self, context, namespace, url, **params):
        return MemcachedNamespaceManager(context, namespace, url, **params)

    def lock_createfunc(self, wait = True):
        if self.funclock is None:
            self.funclock = Synchronizer(identifier =
"memcachedcontainer/funclock/%s" % self.namespacemanager.namespace,
use_files = True, lock_dir = self.namespacemanager.lock_dir)

        return self.funclock.acquire_write_lock(wait)

    def unlock_createfunc(self):
        self.funclock.release_write_lock()

