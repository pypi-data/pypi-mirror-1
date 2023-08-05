# $Id: cache.py 2062 2006-05-03 05:40:30Z dairiki $
# cache.py - cache API and implementation for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
# 


from myghty.container import *
from myghty.util import *
import myghty.buffer
import re

class Cache:
    """a front-end to the containment API implementing a data cache.
    
    This is a per-request object and is not synchronized against other threads
    or processes.  (the containment API it talks to, is)."""
    

        
    def __init__(self, component, type = None, container_class = None , debug_file = None, **params):

        self.params = CacheArgs()
        self.params.set_params(**params)

        self.type = type    
        if component is not None:
            self.namespace = component.id
        else:
            self.namespace = None
        self.dict = {}

        # attach a ContainerContext to the component, which will hold
        # onto the namespacemanager(s) corresponding to that component.
        # the scope of the context is the same as that of the component,
        # so if a component is unused and gets garbage collected, its 
        # namespacemanagers will get collected as well.
        if component is not None:
            if hasattr(component, "_container_context"):
                self.context = component._container_context
            else:
                self.context = ContainerContext(log_file = debug_file)
                component._container_context = self.context
        
        
        if type is not None:
            self.container_class = container_registry(type, 'Container')
            
        elif container_class is None:
        
            if params.setdefault('data_dir', None) is not None:
                # DBMContainer is definitely faster than FileContainer
                # for caching
                self.container_class = DBMContainer
            else:
                self.container_class = MemoryContainer
                
        else:
            self.container_class = container_class



    
    def _get_container(self, key, **params):
        if not self.dict.has_key(key):
            self.dict[key] = self._create_container(self.namespace, key, **params)

        return self.dict[key]


    def _create_container(self, namespace, key, type = None, container_class = None, **params):
        if container_class is None:
            if type is not None:
                container_class = container_registry(type, 'Container')
            else:
                container_class = self.container_class

        cparams = self.params.get_params(**params)
        
        return container_class(context = self.context, namespace = namespace, key = key, **cparams)
    
        
    def set_container(self, key, **params):
        self.dict[key] = self._create_container(self.namespace, key, **params)
        return self.dict[key]

    def get_container(self, key, **params):
        return self._get_container(key, **params)
        
    def get_value(self, key, **params):
        return self._get_container(key, **params).get_value()

    def set_value(self, key, value, **params):
        self._get_container(key, **params).set_value(value)

    def remove_value(self, key):
        if self.dict.has_key(key):
            self.dict[key].clear_value()
            del self.dict[key]
            
    def clear(self):
        nm = self.get_container(None).get_namespace_manager()
        nm.remove()
        self.dict = {}
        
    # public dict interface
    def __getitem__(self, key):
        return self.get_value(key)
    
    def __contains__(self, key): 
        container = self._get_container(key)
        return container.has_current_value()

    def has_key(self, key): 
        container = self._get_container(key)
        return container.has_current_value()

       
    def __delitem__(self, key):
        self.remove_value(key)
 
    def __setitem__(self, key, value):
        self.set_value(key, value)


class CacheArgs(PrefixArgs):
    
    def __init__(self, **params):
        PrefixArgs.__init__(self, 'cache_')
        self.set_prefix_params(**params)
        
    def clone(self, **params):
        p = self.get_params(**params)
        arg = CacheArgs()
        arg.params = p
        return arg

    def get_cache(self, component, **params):
        return Cache(component, **self.get_params(**params))
        
        
