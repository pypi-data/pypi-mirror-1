# $Id: args.py 2013 2005-12-31 03:19:39Z zzzeek $
# args.py - component argument descriptor classes for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#


__all__ = ['ComponentArg', 'RequestArg', 'SubRequestArg', 'LocalArg', 'DynamicArg']

import myghty.exception as exception

class ComponentArg:
    def __init__(self, name, required = True, default = None, linenumber = None):
        self.name = name

        if default is None:
            self.required = required
        elif not default:
            self.default = None
            self.required = True
        else:
            self.default = default
            self.required = False
            
        self.linenumber = linenumber

    def do_get_arg(self, request, **params):
        raise NotImplementedError()

    def __repr__(self):
        return "%s(%s, required = %s)" % (
            self.__class__.__name__,
            repr(self.name),
            repr(self.required),
        )
        
    def get_arg(self, request, dictionary, **params):
        try:
            dictionary[self.name] = self.do_get_arg(request, **params)
        except KeyError:
            if self.required:            
                raise exception.MissingArgument("required %s argument %s not found" % (self.__class__.type, self.name))

class RequestArg(ComponentArg):
    type = "request"
    def do_get_arg(self, request, **params):
        return request.root_request_args[self.name]
        
class SubRequestArg(ComponentArg):
    type = "subrequest"
    def do_get_arg(self, request, **params):
        return request.request_args[self.name]
        
class LocalArg(ComponentArg):
    type = "component"
    def do_get_arg(self, request, **params):
        return params[self.name]
        
class DynamicArg(ComponentArg):
    type = "dynamic"
    def do_get_arg(self, request, **params):
        def find(request, params):
            yield params
            while request is not None:
                yield request.request_args
                request = request.parent_request
    
        for d in find(request, params):
            if d.has_key(self.name):
                return d[self.name]
        raise KeyError(self.name)
