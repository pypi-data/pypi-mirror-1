import os, types, string

from myghty.resolver import ResolverRule
import myghty.csource as csource
import myghty.component as comp
from myghty.resolver import Resolution
import myghty.importer as importer

import routes
from routes.base import *

class RoutesComponentSource(csource.ModuleComponentSource):
    def __init__(self, objpath, module):
    	self.objpath = objpath
    	self.module = module
    	
    	arg = module
    	for t in objpath:
            arg = getattr(arg, t)
        
        name = "method:" + string.join(objpath, '_')
	    
        self.has_method = True
        last_modified = importer.mod_time(module)
        
        csource.ComponentSource.__init__(self, "module|%s:%s" % (module.__name__, name), last_modified = last_modified)
        
        self.module = module
        self.objpath = objpath
        self.name = name
        self.class_ = RoutesComponent
        self.callable_ = arg
    
    def reload(self, module):
        self.module = module        

        arg = module
        for t in self.objpath:
            arg = getattr(arg, t)
        self.callable_ = arg
	
    def can_compile(self):
        return False

class RoutesComponent(comp.FunctionComponent):
    def do_run_component(self, **params):
        m = params['m']
        r = params['r']
       
        # do stuff with routes config
        config = routes.request_config()
        config.redirect = m.send_redirect
        config.host = r.headers_in['host'].split(':')[0]
        if r.environ.get('HTTPS'):
            config.protocol = 'https'
        else:
            config.protocol = 'http'
 
        # update params with routes resolution args
        if hasattr(m, 'resolution'):
            params.update(m.resolution.override_args)
        
        # if we are linked to a method off of an object instance,
        # see if the object instance has a do_run_component method and run it
        if self.component_source.has_method:
            target = self.component_source.callable_.im_self
            if hasattr(target, 'do_run_component'):
                getattr(target, 'do_run_component')(**params)
                
        return comp.FunctionComponent.do_run_component(self, **params)
    
class RoutesResolver(ResolverRule):
    name = 'routeresolver'
    
    def _find_controllers(self, dirname, prefix=''):
        controllers = []
        for fname in os.listdir(dirname):
            filename = dirname + '/' + fname
            if os.path.isfile(filename) and fname.endswith('_controller.py') and not fname.startswith('application_'):
                controllers.append(prefix + fname)
            elif os.path.isdir(filename):
                controllers.extend(self._find_controllers(filename, prefix=fname+'/'))
        return controllers
    
    def _get_controllers(self):
        clist = {}
        controllers = self._find_controllers(self.controller_root)
        for con in controllers:
            key = con[:-14] # Remove _controller.py
            clist[key] = self.controller_root + '/' + con
        return clist
    
    def __init__(self, mapper=None, controller_root=None, **params):
        self.mapper = mapper
        self.controller_root = controller_root
    
    def do_init_resolver(self, resolver, remaining_rules, **params):
        self.clist = self._get_controllers()
        self.mapper.create_regs(self.clist.keys())
    
    def do(self, uri, remaining, resolution_detail, **params):
        if resolution_detail is not None: resolution_detail.append("resolverouteresolver:" + uri)

        if os.environ['MYGHTY_ENV'] == 'development':
            self.clist = self._get_controllers()
            self.mapper.create_regs(self.clist.keys())
        
        match = self.mapper.match(uri)
        
        if match:
            controller = match['controller']
            action = match['action']
            if action.startswith('_'):
                return remaining.next().do(uri, remaining, resolution_detail, **params)
            
            # Load up the request local singleton config
            config = routes.request_config()
            config.mapper = self.mapper
            config.mapper_dict = match.copy()

            # Remove the action/controller, rest of the args pass to the function
            del match['action']
            del match['controller']

            filename = self.clist[controller]
            classname = controller.split('/')[-1].lower()
            module = importer.filemodule(filename)
            resolution_detail.append("\nController:%s, Action:%s" % (controller, action))
            cs = RoutesComponentSource(
                module=module,
                objpath=[classname, action],
                )
            #raise repr(cs.__dict__)
            return Resolution(cs, resolution_detail, override_args = match)
        else:
            return remaining.next().do(uri, remaining, resolution_detail, **params)
