# $Id: session.py 2041 2006-02-05 19:02:14Z zzzeek $
# session.py - session management for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
# 

import Cookie
import hmac, md5, time, random, os, re, UserDict, datetime
from myghty.container import *
from myghty.util import *

__all__ = ['SignedCookie', 'Session', 'MyghtySessionArgs']

class SignedCookie(Cookie.BaseCookie):
    "extends python cookie to give digital signature support"
    def __init__(self, secret, input=None):
        self.secret = secret
        Cookie.BaseCookie.__init__(self, input)
    
    def value_decode(self, val):
        sig = val[0:32]
        value = val[32:]
    
        if hmac.new(self.secret, value).hexdigest() != sig:
            return None, val
        
        return val[32:], val
    
    def value_encode(self, val):
        return val, ("%s%s" % (hmac.new(self.secret, val).hexdigest(), val))

                
class Session(UserDict.DictMixin):
    "session object that uses container package for storage"

    def __init__(self, request, id = None, invalidate_corrupt = False, use_cookies = True, type = None, data_dir = None, key = 'myghty_session_id', timeout = None, cookie_expires=True, secret = None, log_file = None, namespace_class = None, **params):
        if type is None:
            if data_dir is None:
                self.type = 'memory'
            else:
                self.type = 'file'
        else:
            self.type = type

        if namespace_class is None:
            self.namespace_class = container_registry(self.type, 'NamespaceManager')
        else:
            self.namespace_class = namespace_class

        self.params = params
        
        self.request = request
        self.data_dir = data_dir
        self.key = key
        self.timeout = timeout
        self.use_cookies = use_cookies
        self.cookie_expires = cookie_expires
        self.log_file = log_file
        self.was_invalidated = False
        self.secret = secret
        
        self.id = id
            
        if self.use_cookies:
            try:
                cookieheader = request.headers_in['cookie']
            except KeyError:
                cookieheader = ''
                
            if secret is not None:
                try:
                    self.cookie = SignedCookie(secret, input = cookieheader)
                except Cookie.CookieError:
                    self.cookie = SignedCookie(secret, input = None)
            else:
                self.cookie = Cookie.SimpleCookie(input = cookieheader)

            if self.id is None and self.cookie.has_key(self.key):
                self.id = self.cookie[self.key].value
        
        if self.id is None:
            self._create_id()
        else:
            self.is_new = False

        try:
            self.load()
        except:
            if invalidate_corrupt:
                self.invalidate()
            else:
                raise
        
    def _create_id(self):
        self.id = md5.new(
            md5.new("%f%s%f%d" % (time.time(), id({}), random.random(), os.getpid()) ).hexdigest(), 
        ).hexdigest()
        self.is_new = True
        if self.use_cookies:
            self.cookie[self.key] = self.id
            self.cookie[self.key]['path'] = '/'
            if self.cookie_expires is not True:
                if self.cookie_expires is False:
                    expires = datetime.datetime.fromtimestamp( 0x7FFFFFFF )
                elif isinstance(self.cookie_expires, datetime.timedelta):
                    expires = datetime.datetime.today() + self.cookie_expires
                elif isinstance(self.cookie_expires, datetime.datetime):
                    expires = self.cookie_expires
                else:
                    raise ValueError("Invalid argument for cookie_expires: %s" % repr(self.cookie_expires))
                self.cookie[self.key]['expires'] = expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT" )
            
            self.request.headers_out.add('set-cookie', self.cookie[self.key].output(header=''))
            

    created = property(lambda self: self.dict['_creation_time'])

    def delete(self):
        """deletes the persistent storage for this session, but remains valid. """
        self.namespace.acquire_write_lock()
        try:
            for k in self.namespace.keys():
                if not re.match(r'_creation_time|_accessed_time', k):
                    del self.namespace[k]
                    
            self.namespace['_accessed_time'] = time.time()
        finally:
            self.namespace.release_write_lock()
        
            
    def __getitem__(self, key):
        return self.dict.__getitem__(key)
    def __setitem__(self, key, value):
        self.dict.__setitem__(key, value)
    def __delitem__(self, key):
        del self.dict[key]
    def keys(self):
        return self.dict.keys()
    def __contains__(self, key):
        return self.dict.has_key(key)
    def has_key(self, key):
        return self.dict.has_key(key)
    def __iter__(self):
        return iter(self.dict.keys())
    def iteritems(self):
        return self.dict.iteritems()
        
    def invalidate(self):
        "invalidates this session, creates a new session id, returns to the is_new state"
        namespace = self.namespace
        namespace.acquire_write_lock()
        try:
            namespace.remove()
        finally:
            namespace.release_write_lock()
            
        self.was_invalidated = True
        self._create_id()
        self.load()

                    
    def load(self):
        "loads the data from this session from persistent storage"

        self.namespace = self.namespace_class(NamespaceContext(log_file = self.log_file), self.id, data_dir = self.data_dir, digest_filenames = False, **self.params)

        namespace = self.namespace
        
        namespace.acquire_write_lock()
        try:
        
            self.debug("session loading keys")
            self.dict = {}
            now = time.time()
            
            if not namespace.has_key('_creation_time'):
                namespace['_creation_time'] = now
            try:
                self.accessed = namespace['_accessed_time']
                namespace['_accessed_time'] = now
            except KeyError:
                namespace['_accessed_time'] = self.accessed = now
    
            if self.timeout is not None and now - self.accessed > self.timeout:
                self.invalidate()
            else:
                for k in namespace.keys():
                    self.dict[k] = namespace[k]
                    
        finally:
            namespace.release_write_lock()

        
        
    def save(self):
        "saves the data for this session to persistent storage"
        
        self.namespace.acquire_write_lock()
        try:
            self.debug("session saving keys")
            todel = []
            for k in self.namespace.keys():
                if not self.dict.has_key(k):
                    todel.append(k)
            
            for k in todel:
                del self.namespace[k]
                    
            for k in self.dict.keys():
                self.namespace[k] = self.dict[k]
                
            self.namespace['_accessed_time'] = time.time()
        finally:
            self.namespace.release_write_lock()
    

    def lock(self):
        """locks this session against other processes/threads.  this is 
        automatic when load/save is called.
        
        ***use with caution*** and always with a corresponding 'unlock'
        inside a "finally:" block,
        as a stray lock typically cannot be unlocked
        without shutting down the whole application.
        """
        self.namespace.acquire_write_lock()
    

    def unlock(self):
        """unlocks this session against other processes/threads.  this is 
        automatic when load/save is called.

        ***use with caution*** and always within a "finally:" block,
        as a stray lock typically cannot be unlocked
        without shutting down the whole application.
        
        """
        self.namespace.release_write_lock()
    

    def debug(self, message):
        if self.log_file is not None:
            self.log_file.write(message)
            
class MyghtySessionArgs(PrefixArgs):
    
    def __init__(self, data_dir = None, **params):
        PrefixArgs.__init__(self, 'session_')
        
        self.set_prefix_params(**params)
        
        if not self.params.has_key('data_dir') and data_dir is not None:
            self.params['data_dir'] = os.path.join(data_dir, 'sessions')
                                        
    def get_session(self, request, **params):
        return Session(request, **self.get_params(**params)) 

    def clone(self, **params):
        p = self.get_params(**params)
        arg = MyghtySessionArgs()
        arg.params = p
        return arg
                

        
        
        
        
