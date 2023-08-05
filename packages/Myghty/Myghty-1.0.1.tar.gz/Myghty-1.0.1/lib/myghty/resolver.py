# $Id: resolver.py 2024 2006-01-12 04:16:15Z zzzeek $
# resolver.py - file path resolution functions for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
# Original Perl code and documentation copyright (c) 1998-2003 by Jonathan Swartz. 
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#


import types, re, os, string, stat, sys, imp
import posixpath as unixpath
import myghty.util as util
from myghty import exception
import myghty.csource as csource
import myghty.importer as importer
import time, copy

__all__ = ['Resolver', 'ResolverRule', 'ResolveFile', 'AdjustedResolveFile', 'ResolveModule', 'Group', 'Conditional', 'ConditionalGroup', 
        'NotFound', 'PathTranslate', 'ResolveDhandler', 'ResolveUpwards', 'URICache', 'ResolvePathModule']

class Resolution(object):
    """represents a resolved uri, including the component source object, 
    a list of resolution detail messages, and an 
    optional regexp match object."""
    def __init__(self, csource, resolution_detail, match = None, can_cache = True, **params):
        self.csource = csource
        self.detail = resolution_detail
        self.match = match
        self.can_cache = can_cache
        for key, value in params.iteritems():
            setattr(self, key, value)

class ResolverRule(object):
    """base class for a single rule that attempts to resolve a uri into a Resolution 
    object.  acts inside a chain of ResolverRules where when a uri cannot be resolved,
    the next rule in the chain is called in a continuation pattern."""
    
    def init_resolver(self, resolver, remaining_rules, **params):
        if hasattr(self, 'resolver'): raise exception.ConfigurationError("resolver rule %s already initialized with a Resolver" % repr(self))
        self.resolver = resolver
        self.do_init_resolver(resolver, remaining_rules, **params)
        
    def do_init_resolver(self, resolver, remaining_rules, **params):
        """ called when the resolver first receives the new rule.
        objects usually will want to do most of their initialization
        at this stage. """
        pass
 
    def do(self, uri, remaining, resolution_detail, **params):
        """ performs resolution or translation on the given path.  
        "remaining" is an Iterator referencing an element in the full 
        list of ResolverRule objects.  the method either returns a 
        Resolution object, or passes control to the next
        ResolverRule in the iterator."""
        raise NotImplementedError()

    def modifies_uri(self):
        """ returns True if the rule makes a modification to the URI.  
        if so, the URICache rule wont allow this rule to be cached as a single
        rule, since it becomes ineffective.  As part of a cached chain is still
        OK."""
        return False

class ResolveFile(ResolverRule):
    """performs file based resolution. looks up files within one or
    more component roots."""
    
    name = 'resolvefile'
    
    def __init__(self, *component_roots, **params):
        self._adjust = params.get('adjust', None) or params.get('component_root_adjust', None)
        
        if len(component_roots):
            self.component_root = component_roots
        else:
            self.component_root = None
    
    def do_init_resolver(self, resolver, remaining_rules, component_root = None, **params):
        if self.component_root is None:
            self.component_root = component_root

        if self.component_root is None: return

        if self._adjust is None:
            self._adjust = params.get('component_root_adjust', None)
        
        if not isinstance(self.component_root, types.ListType) and not isinstance(self.component_root, types.TupleType):
            self.component_root = [{'main':self.component_root}]
        
        self.component_root = util.OrderedDict(self.component_root)

    def do(self, uri, remaining, resolution_detail, **params):
        if self.component_root is None: return remaining.next().do(uri, remaining, resolution_detail, **params)
        
        if resolution_detail is not None: resolution_detail.append("resolvefile:")
        
        if self._adjust is not None:
            path = self._adjust(uri)
            if resolution_detail is not None: resolution_detail.append("adjust: %s -> %s" % (uri, path))
        else:
            path = uri
            
        # internal path, trim off leading '/'
        if path and path[0] == '/':
            path = path[1:]
        
        for key, root in self.component_root.iteritems():
            srcfile = unixpath.join(root, path)
            
            if resolution_detail is not None: resolution_detail.append(srcfile)
            
            if os.access(srcfile, os.F_OK):
                break
        else:
            return remaining.next().do(uri, remaining, resolution_detail, **params)
            
        st = os.stat(srcfile)
        (mode, modtime) = (st[stat.ST_MODE], st[stat.ST_MTIME])
        
        if stat.S_ISDIR(mode):
            if resolution_detail is not None: 
                resolution_detail.append("isdirectory: " + uri)
            return remaining.next().do(uri, remaining, resolution_detail, **params)
        
        # the resolved uri, insure theres a leading '/'
        if not uri or uri[0] != '/':
            uri = '/' + uri
            
        return Resolution(
                csource.FileComponentSource(
                    file_path = srcfile,
                    last_modified = modtime,
                    path = uri,
                    path_id = key,
                    id = "%s|%s" % (key, path), 
                ), 
                resolution_detail
            )

        

class ResolvePathModule(ResolverRule):
    """resolves a callable object or class instance inside a module, based on a traversal
    of path tokens corresponding to the module's file location, and then of the object paths
    defined within the module."""
    name = 'pathmodule'
    
    def __init__(self, *module_roots, **params):
        self._adjust = params.get('adjust', None) or params.get('module_root_adjust', None)
        self._require_publish = params.get('require_publish', None)
        self.stringtokens = params.get('path_stringtokens', None)
        self.moduletokens = params.get('path_moduletokens', None)
        
        if len(module_roots):
            self.module_root = list(module_roots)
        else:
            self.module_root = None

    def do_init_resolver(self, resolver, remaining_rules, module_root = None, **params):
        self.use_static_source = resolver.use_static_source

        if self.module_root is None:
            self.module_root = module_root
        if self.module_root is None: return

        if self._adjust is None:
            self._adjust = params.get('module_root_adjust', None)
        if self._require_publish is None:
            self._require_publish = params.get('require_publish', False)
        if self.stringtokens is None:
            self.stringtokens = params.get('path_stringtokens', [])
        if self.moduletokens is None:
            self.moduletokens = params.get('path_moduletokens', ['index'])
        
        for i in range(0, len(self.module_root)):
            value = self.module_root[i]
            if not isinstance(value, types.ModuleType):
                try:
                    st = os.stat(value)
                    if stat.S_ISREG(st[stat.ST_MODE]):
                        self.module_root[i] = importer.filemodule(value)
                except OSError:
                    try:
                        self.module_root[i] = importer.module(value)
                    except Exception, e:
                        raise exception.ConfigurationError("Path %s is not a file, directory, or importable module (%s: %s)" % (value, e.__class__.__name__, e.args[0]))
                
    def do(self, uri, remaining, resolution_detail, dhandler_path = None, **params):
        if self.module_root is None: return remaining.next().do(uri, remaining, resolution_detail, **params)
        
        if resolution_detail is not None: resolution_detail.append("resolvemodulepath:")
        
        if self._adjust is not None:
            path = self._adjust(uri)
            if resolution_detail is not None: resolution_detail.append("adjust: %s -> %s" % (uri, path))
        else:
            path = uri
        
        # internal path, trim off leading '/'
        if path and path[0] == '/':
            path = path[1:]

        if dhandler_path is not None:
            path = path + '/' + dhandler_path

        if (path == '/' or not path) and len(self.stringtokens):
            path= '/' + self.stringtokens[0]
            
        for root in self.module_root:
            if resolution_detail is not None:
                resolution_detail.append(repr(root) + "/" + path)
                
            iterator = importer.ObjectPathIterator(root, reload = not self.use_static_source)
            unit = root
            for token in path.split('/'):
                if not token:
                    continue
                if len(token) > 0 and token[0] == '_':
                    token = re.sub(r'^_+', '', token)
                try:
                    while True:
                        (unit, matched) = iterator.get_unit([token], stringtokens = self.stringtokens, moduletokens = self.moduletokens)
                        if matched == token:
                            break
                except StopIteration:
                    pass
            
            if unit is not None:
                while unit is not None and (isinstance(unit, types.ModuleType) or isinstance(unit, str)):
                    try:
                        (unit,matched) = iterator.get_unit([], stringtokens=self.stringtokens, moduletokens=self.moduletokens)
                        if unit is None:
                            break
                    except StopIteration:
                        break
                    
                if isinstance(unit, types.FunctionType) or isinstance(unit, types.MethodType) or callable(unit):
                    if self._require_publish and not getattr(unit, 'publish', False):
                        return remaining.next().do(uri, remaining, resolution_detail, **params)
                    cs = csource.ModuleComponentSource(module = iterator.module, objpath = iterator.objpath, last_modified = iterator.last_modified, arg = unit)
                    break
                else:
                    continue
        else:
            return remaining.next().do(uri, remaining, resolution_detail, **params)

        return Resolution(cs, resolution_detail)


def adjust_path(adjust, path):
    for a in adjust:
        path = re.sub(a[0], a[1], path)
    return path

class AdjustedResolveFile(ResolveFile):
    """a ResolveFile rule that adds a pre-path-concatenation adjustment step, so the uri can
    be translated before determining the file path.  unlike path_translate, this translated
    uri is only used to determine a filesystem path, and is not propigated anywhere else."""
    def __init__(self, adjust, *component_roots):
        ResolveFile.__init__(self, adjust = lambda p: adjust_path(adjust, p), *component_roots)

class AdjustedResolvePathModule(ResolvePathModule):
    """a ResolvePathModule rule that adds a pre-path-concatenation adjustment step, so the uri can
    be translated before determining the file path.  unlike path_translate, this translated
    uri is only used to determine a filesystem path, and is not propigated anywhere else."""
    def __init__(self, adjust, *module_roots):
        ResolvePathModule.__init__(self, adjust = lambda p: adjust_path(adjust, p), *module_roots)
        
class ResolveModule(ResolverRule):
    """resolves a Module Component based on information in a given list of dictionaries,
    containing regular expressions for keys which are matched against the URI. The value 
    for each key references either a class, a callable object or function, or a string in 
    the form "<module>:<path.to.callable>"."""
    
    name = 'resolvemodule'
    
    def __init__(self, *module_components):
        if len(module_components):
            self.module_components = module_components
        else:
            self.module_components = None
        self.csource_cache = {}
        
    def do_init_resolver(self, resolver, remaining_rules, module_components = None, **params):
        self.use_static_source = resolver.use_static_source
        if self.module_components is None:
            self.module_components = module_components

        if self.module_components is None: return
        
        self.module_components = util.OrderedDict(self.module_components)
        for key, value in self.module_components.iteritems():
            if not isinstance(value, types.DictType):
                value = {'component':value}
                self.module_components[key] = value

    def do(self, uri, remaining, resolution_detail, context = None, **params):
        if self.module_components is None: return remaining.next().do(uri, remaining, resolution_detail, **params)

        if resolution_detail is not None: resolution_detail.append("resolvemodule: " + uri)
        
        for reg in self.module_components.keys():
            match = re.match(reg, uri)
            if match:
                info = self.module_components[reg]
                compsource = csource.ModuleComponentSource(arg = info['component'], use_static_source = self.use_static_source, arg_cache=self.csource_cache)
                return Resolution(
                    compsource,
                    resolution_detail,
                    match,
                    args = info
                    )
        else:
            return remaining.next().do(uri, remaining, resolution_detail, **params)
                

class Group(ResolverRule):
    """creates a subgroup of resolver strategies."""
    def __init__(self, rules = []):
        self.rules = rules

    def do_init_resolver(self, resolver, remaining_rules, **params):
        for i in range(0, len(self.rules)):
            self.rules[i].init_resolver(resolver, self.rules[i + 1:], **params)
                                 
    def do(self, uri, remaining, resolution_detail, **params):
        def iterator():
            for rule in self.rules:
                yield rule
            for rule in remaining:
                yield rule
        i = iterator()
        return i.next().do(uri, i, resolution_detail, **params)

    
class Conditional(ResolverRule):
    """conditionally executes a rule, only executes if the uri matches a certain regexp,
    or a passed-in context string matches one of the contexts set up for this rule."""
    
    def __init__(self, rule, regexp = None, context = None):
        self.rule = rule
        
        if context is not None:
            self.contexts = context.split(',')
        else:
            self.contexts = []
        self.regexp = regexp

    def do_init_resolver(self, resolver, remaining_rules, **params):
        self.rule.init_resolver(resolver, remaining_rules, **params)

    def _match_context(self, context):
        for c in self.contexts:
            if c == context: return True
        return False

    
    def test_condition(self, uri, resolver_context, **params):
        return (
            (resolver_context is not None and self._match_context(resolver_context))
            or
            (self.regexp is not None and re.match(self.regexp, uri))
        )

    def do(self, uri, remaining, resolution_detail, resolver_context = None, **params):
        if self.test_condition(uri, resolver_context, **params): 
            if resolution_detail is not None: 
                if self.regexp is not None:
                    resolution_detail.append("conditional: " + self.regexp)
                else:
                    resolution_detail.append("conditional: " + resolver_context)
            return self.rule.do(uri, remaining, resolution_detail, resolver_context = resolver_context, **params)
        else:
            return remaining.next().do(uri, remaining, resolution_detail, resolver_context = resolver_context, **params)


class ConditionalGroup(Conditional):
    """combines a Conditional and a Group to make a conditionally-executing Group."""
    
    def __init__(self, regexp = None, context = None, rules = []):
        Conditional.__init__(self, Group(rules = rules), regexp, context)



    
class NotFound(ResolverRule):
    """returns not found.  place at the bottom of Group and Match chains to have them terminate."""
    name = 'notfound'
    
    def __init__(self, silent = False):
        """silent = True indicates that a resulting TopLevelNotFound exception should be 'silent', i.e.
        not logged.  this is used when a 404 error is being propigated to another application layer."""
        self.silent = silent
        
    def do(self, uri, remaining, resolution_detail, **params):
        if resolution_detail is not None: resolution_detail.append("notfound")
        raise exception.ComponentNotFound("cant locate component %s" % uri, resolution_detail, silent = self.silent)
        
class PathTranslate(ResolverRule):
    """ performs path translation rules on the given uri and sends control off to the
    next rule."""
    
    name = 'pathtranslate'
    
    def __init__(self, *translations):
        
        if len(translations):
            self.path_translate = translations
        else:
            self.path_translate = None

    def modifies_uri(self):return True
        
    def do_init_resolver(self, resolver, remaining_rules, path_translate = None, **params):
        if self.path_translate is None:
            self.path_translate = path_translate
        if self.path_translate is not None and not callable(self.path_translate):
            pt = self.path_translate
            def trans(url):
                for rule in pt:
                    url = re.sub(rule[0], rule[1], url)
                return url
            self.path_translate = trans
    def do(self, uri, remaining, resolution_detail, **params):
        if self.path_translate is None:
            return remaining.next().do(uri, remaining, resolution_detail, **params)

        olduri = uri
        uri = self.path_translate(uri)
            
        if resolution_detail is not None: 
            resolution_detail.append("translate: %s -> %s" % (olduri, uri))
            
        return remaining.next().do(uri, remaining, resolution_detail, **params)

class URICache(ResolverRule):
    """caches the result of either a given nested rule, or the remaining rules in its chain, 
    based on the incoming URI."""
    
    name = 'uricache'
    
    def __init__(self, source_cache_size = None, rule = None):
        
        """
        rule is a single ResolverRule (or Group) whos results will be cached on a 
        per-uri basis.  if rule is None, then the result of remaining rules in the current chain
        will be cached based on the incoming URI.  This rule cannot be a PathTranslation
        rule or other uri-modifying rule, since the translated uri is not stored.
        
        source_cache_size is the size of the LRUCache to create.
        if source_cache_size is None, it will use the Resolver's source cache, 
        sharing it with any other URICaches that also use the Resolver's source cache.
        
        When using the Resolver's source cache, if the Resolver has use_static_source 
        disabled, then caching is disabled in this URICache.
        """
        self.source_cache_size = source_cache_size
        self.rule = rule
        
    def do_init_resolver(self, resolver, remaining_rules, **params):
        if self.rule is not None:
            if self.rule.modifies_uri():
                raise exception.ConfigurationError("can't cache single rule %s - it is a URI-modifying rule" % str(self.rule))
            self.rule.init_resolver(resolver, remaining_rules, **params)
                
        if self.source_cache_size is None:
            self.source_cache = resolver.source_cache
        else:
            self.source_cache = util.LRUCache(self.source_cache_size)
        

    def do(self, uri, remaining, resolution_detail, **params):
        if self.source_cache is None:
            if self.rule is not None:
                return self.rule.do(uri, remaining, resolution_detail, **params)
            else:
                return remaining.next().do(uri, remaining, resolution_detail, **params)
        
        # create a key that has a stringified version of the parameters plus the URI.
        # parameters are expected to be pretty much true/false, strings, and maybe lists of strings.
        key = repr(params) + "|" + uri
        
        try:
            # try to pull results from the cache
            cached = self.source_cache[key]
            
            # update detail with the cached detail
            if resolution_detail is not None: 
                resolution_detail += cached['detail']
        
            if cached.has_key('exception'):
                # single rule, which was run with an empty chain - so StopIteration
                # corresponds to just continuing on the rest of the chain.
                if self.rule is not None and isinstance(cached['exception'], StopIteration):
                    return remaining.next().do(uri, remaining, resolution_detail, **params)
                else:
                    # else it was a single rule that raised ComponentNotFound, or
                    # it was the remainder of the rule chain, so raise exception
                    raise cached['exception']
            else:
                # got a cached result - return it
                resolution = copy.copy(cached['resolution'])
                resolution.detail = resolution_detail
                return resolution
        except KeyError:
            # ok, nothing in the cache, so run the rule or rules and cache the result
            
            cached_detail = []
            cached_detail.append("cached: " + str(time.time()))

            cached = None
            
            can_cache = True
            
            try:        
                try:
                    if self.rule is not None:
                        # single rule - run it in an empty chain
                        resolution = self.rule.do(uri, iter([]), cached_detail, **params)
                    else:
                        # remaining rules - run the rest of the chain
                        resolution = remaining.next().do(uri, remaining, cached_detail, **params)
            
                    can_cache = resolution.can_cache
                    cached = {'resolution': resolution, 'detail': cached_detail}
                    
                    if resolution_detail is not None: resolution_detail += cached_detail
                    return resolution
                    
                except StopIteration, si: 
                    # normal end of chain reached
                    cached = {'exception': si, 'detail': cached_detail}
                    if self.rule is not None:
                        # single rule - continue on with the rest of the chain
                        if resolution_detail is not None: resolution_detail += cached_detail
                        return remaining.next().do(uri, remaining, resolution_detail, **params)
                    else:
                        # remaining chain - raise the StopIteration
                        if resolution_detail is not None: resolution_detail += cached_detail
                        raise si

                except exception.ComponentNotFound, cf: 
                    # a rule wants to force not found
                    cached = {'exception': cf, 'detail': cached_detail}
                    if resolution_detail is not None: resolution_detail += cached_detail
                    raise cf
            finally:
                # cache the result
                if can_cache is True:
                    self.source_cache[key] = cached
            
class ResolveDhandler(ResolverRule):
    """collects all the resolver rules below it and runs them for the requested uri, and if not found
    re-runs them again for the "dhandler" filename, pruning off path tokens until the root is reached."""
    
    name = 'resolvedhandler'
    
    def __init__(self, dhandler_name = 'dhandler'):
        self.dhandler_name = dhandler_name

    
    def do(self, uri, remaining, resolution_detail, enable_dhandler = False, declined_components = None, **params):
        if not enable_dhandler:
            return remaining.next().do(uri, remaining, resolution_detail, enable_dhandler = False, declined_components = declined_components, **params)
            

        list = [elem for elem in remaining]

        searchuri = uri
        parentdir = None
        raisecfound = False
        dhandler_path = None
        
        while True:
            iterator = iter(list)       
            try:
                if parentdir is not None:
                    dhandler_path = uri[len(parentdir):]
                resolution = iterator.next().do(searchuri, iterator, resolution_detail, dhandler_path = dhandler_path, **params)
                if resolution:
                    if declined_components and declined_components.has_key(resolution.csource.id):
                        if resolution_detail is not None: resolution_detail.append("declined")
                    else:
                        resolution.dhandler_path = dhandler_path
                        
                        return resolution
                
            # keep track on which type of exception the chain raises when it reaches the end
            # this is usually based on if a NotFound element is at the end of the chain
            except StopIteration: pass
            except exception.ComponentNotFound: raisecfound = True

            # csource not found, or found but its been declined
            # modify path to be a dhandler path, or move dhandler path up one token
            (parentdir, name) = unixpath.split(searchuri)
            if name == self.dhandler_name:
                # already looked for dhandler, and no more tokens.  not found
                if not parentdir or parentdir == '/':
                    # raise the exception that would normally have happened
                    # in the resolution chain
                    if raisecfound:
                        raise exception.ComponentNotFound("cant locate uri %s" % uri, resolution_detail)
                    else:
                        raise StopIteration

                (parentdir, token) = unixpath.split(parentdir)
            else:
                # entering "dhandler" mode, append to detail
                if resolution_detail is not None: resolution_detail.append("dhandler")

            searchuri = unixpath.join(parentdir, self.dhandler_name)

        assert(False, "enableDhandler loop failed")     

class ResolveUpwards(ResolverRule):
    """takes the rules below it and applies "search upwards" logic to them, where it iteratively breaks off
    path tokens behind the filename and searches upwards until the root path is reached.
    
    if require_context is True, then this rule only takes effect if "search_upwards" is sent within the resolution options.
    this indicates that the upwards resolve is context-sensitive, and therefore should not be cached based on a
    URI alone.  however, by default it allows its results to be cached since in practice its used 
    strictly for autohandlers, which are always searched upwards.
    """
    
    name = 'resolveupwards'
    
    def __init__(self, require_context = True):
        self.require_context = require_context

    def do(self, uri, remaining, resolution_detail, search_upwards = False, **params):
        if self.require_context and not search_upwards:
            return remaining.next().do(uri, remaining, resolution_detail, **params)

        if resolution_detail is not None:
            resolution_detail.append("resolveupwards")

        list = [elem for elem in remaining]

        searchuri = uri
        parentdir = None
        raisecfound = False

        while True:
            iterator = iter(list)
            resolution = None
            
            try:
                resolution = iterator.next().do(searchuri, iterator, resolution_detail, **params)
                if resolution:
                    if parentdir:
                        resolution.uri_truncated = uri[len(parentdir):]
                    return resolution
                
            # keep track on which type of exception the chain raises when it reaches the end
            # this is usually based on if a NotFound element is at the end of the chain
            except StopIteration: pass
            except exception.ComponentNotFound: raisecfound = True

            (parentdir, name) = unixpath.split(searchuri)
            if not parentdir or parentdir == '/':
                # raise the exception that would normally have happened
                # in the resolution chain
                if raisecfound:
                    raise exception.ComponentNotFound("cant locate uri %s" % uri, resolution_detail)
                else:
                    raise StopIteration

            (parentdir, token) = unixpath.split(parentdir)

            searchuri = unixpath.join(parentdir, name)

        assert(False, "UpwardsResolve loop failed")     


    
class Resolver(object):
    """resolves incoming URIs against a list of rules, and returns Resolution objects and/or
    raises ComponentNotFound exceptions."""
    
    def __init__(self, 
                resolver_strategy = None,
                request_resolver = None,
                use_static_source = False,
                source_cache_size = 1000,
                track_resolution_detail = True,
                debug_file = None,
                **params 
                ):

        if resolver_strategy is None:
            resolver_strategy = [
                PathTranslate(),
                ResolveDhandler(),
                URICache(),
                ResolveUpwards(),
                ResolvePathModule(),
                ResolveModule(),
                ResolveFile()
            ]

#        if request_resolver is not None:
#            resolver_strategy.insert()
            
        self.debug_file = debug_file
   
        self.use_static_source = use_static_source 
        if use_static_source:
            self.source_cache = util.LRUCache(source_cache_size)
        else:
            self.source_cache = None

        self.track_resolution_detail = track_resolution_detail
        
        for i in range(0, len(resolver_strategy)):
            if type(resolver_strategy[i]) == str:
                try:
                    resolver_strategy[i] = rulelookup[resolver_strategy[i]]()
                except KeyError:
                    raise exception.ConfigurationError("No such resolution rule '%s'" % resolver_strategy[i])

        for i in range(0, len(resolver_strategy)):
            resolver_strategy[i].init_resolver(self, resolver_strategy[i + 1:], **params)
            
        self.resolver_strategy = resolver_strategy
            
    def resolve(self, uri, raise_error = True, **params):
        iterator = iter(self.resolver_strategy)

        if self.track_resolution_detail:
            resolution_detail = []
        else:
            resolution_detail = None

        try:            
            try:
                return iterator.next().do(uri, iterator, resolution_detail, **params)
            except StopIteration:
                if raise_error:
                    raise exception.ComponentNotFound("Cant locate component %s" % uri, resolution_detail)
                else:
                    return None
            except exception.ComponentNotFound, cf:
                if raise_error:
                    raise cf
                else:
                    return None
        finally:
            if self.debug_file is not None and resolution_detail is not None: self.debug_file.write('"' + uri + '" ' + string.join(resolution_detail, ', '))
        

class FileResolver(Resolver):pass

rulelookup = {}

thismodule = sys.modules[__name__]
for obj in thismodule.__dict__.values():
    if (type(obj) == types.ClassType or type(obj) == types.TypeType) and issubclass(obj, ResolverRule) and hasattr(obj, 'name'):
        rulelookup[obj.name] = obj
        
