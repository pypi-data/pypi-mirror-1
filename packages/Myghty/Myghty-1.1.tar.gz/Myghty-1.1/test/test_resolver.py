import testbase
import myghty.resolver as resolver
import myghty.exception as exception
import unittest, sys, string

class FileResolveTest(testbase.MyghtyTest):
    def class_set_up(self):
        
        self.resolver = resolver.Resolver(
            component_root = [{'htdocs': self.htdocs}, {'comp': self.components}],
            use_static_source = True
        )
        
        self.create_file(self.htdocs, 'hello.myt', "hello component")
        self.create_file(self.components, 'searchup.myt', "searchup component")
        self.create_directory(self.htdocs, './foo/lala')
        self.create_file(self.htdocs, './foo/searchup2.myt', "<html> foo</html>")
        self.create_file(self.htdocs, './foo/lala/hi.myt', "im hi.myt")
        self.create_file(self.components, 'dhandler', "im a dhandler")

    def class_tear_down(self):
        self.remove_file(self.components, "dhandler")
        self.remove_file(self.components, "searchup.myt")
        self.remove_file(self.htdocs, './foo/searchup2.myt')
        self.remove_file(self.htdocs, './foo/lala/hi.myt')
        self.remove_file(self.htdocs, 'hello.myt')
        
    def testcomponent(self):
        "locates a component in the root directory"
        resolution = self.resolver.resolve('/hello.myt', search_upwards = False, raise_error = True)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None and csource.path == '/hello.myt' and csource.dir_name == '/', "hello.myt not located")

    def testdircomponent(self):
        "locates a component in a subdirectory"
        resolution = self.resolver.resolve('/foo/lala/hi.myt', search_upwards = False, raise_error = True)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None and csource.path == '/foo/lala/hi.myt' and csource.dir_name == '/foo/lala' and csource.name=='hi.myt', "hi.myt not properly located")
    
    def testcomponentnoslash(self):
        "locates a component with no directory information in the URI"
        resolution = self.resolver.resolve('hello.myt', search_upwards = False, raise_error = True)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None, "hello.myt not located")
        self.assert_(csource.path == '/hello.myt' and csource.dir_name == '/', "hello.myt has wrong path info, path %s dir_name %s" % (csource.path, csource.dir_name))

    def testcache(self):
        "locates a component twice with caching on, checks that the second resolution succeeded"
        resolution = self.resolver.resolve('/hello.myt', search_upwards = False, raise_error = True)
        csource = resolution.csource
        dumpresolution(resolution)
        resolution = self.resolver.resolve('/hello.myt', search_upwards = False, raise_error = True)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None and csource.path == '/hello.myt' and csource.dir_name == '/', "hello.myt not located")

    
    def testupwardsnonexistentdir(self):
        "locates a component searching upwards, with the initial directory nonexistent"
        resolution = self.resolver.resolve('/foo/bar/searchup.myt', search_upwards = True, raise_error = True)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None and csource.path == '/searchup.myt' and csource.dir_name == '/', "search upwards test #1 failed")
        
    def testupwardsrealdir(self):
        "locates a component searching upwards, with a real initial directory"
        resolution = self.resolver.resolve('/foo/lala/searchup2.myt', search_upwards = True, raise_error = True)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None and csource.path == '/foo/searchup2.myt' and csource.dir_name == '/foo', "search upwards test #2 failed, " + csource.path + " " + csource.dir_name)

    def testnotfound(self):
        "tries to locate a component that doesnt exist"
        resolution = self.resolver.resolve('/foo/hi.myt', search_upwards = False, raise_error = False)
        self.assert_(resolution is None, "not found test failed")
        
    def testupwardsnotfound(self):
        "tries to locate a component searching upwards that does not exist"
        resolution = self.resolver.resolve('/foo/autohandler', search_upwards = True, raise_error = False)
        self.assert_(resolution is None, "not found upwards test failed")

    def testupwardsnoslash(self):
        "locates a component upwards, where the uri has no directory information"
        resolution = self.resolver.resolve('autohandler', search_upwards = True, raise_error = False)
        self.assert_(resolution is None, "not found upwards test with no slashes failed")


    def testdhandler(self):
        "locates a dhandler"
        resolution = self.resolver.resolve('/foo/bar/lala/foo.myt', enable_dhandler = True, raise_error = False)
        dumpresolution(resolution)
        self.assert_(resolution is not None, "dhandler test failed")
        csource = resolution.csource
        self.assert_(csource.path == '/dhandler' and csource.dir_name == '/', "dhandler test failed")
        self.assert_(resolution.dhandler_path == 'foo/bar/lala/foo.myt', "dhandler_path is %s" % resolution.dhandler_path)

    def testdhandlernoslash(self):
        "attempts to locate a dhandler with an initial uri that has no directory information, and no dhandler"
        self.remove_file(self.components, "dhandler")
        resolution = self.resolver.resolve('hoho.myt', enable_dhandler = True, raise_error = False)
        self.assert_(resolution is None, "dhandler test with no slashes failed")
        
    def testdir(self):
        "attempts to locate a component with a uri that resolves to a real directory"
        try:
            resolution = self.resolver.resolve('/foo/lala/', search_upwards = False, raise_error = True)
            self.assert_(False, "didnt detect directory")
        # we sort of liked when this was PathIsDirectory
        except exception.ComponentNotFound, e:
            #print e.message()
            self.assert_(True)
        

class PathModuleResolveTest(testbase.MyghtyTest):
    def class_set_up(self):
        self.create_file(self.components, 'pathmodule1.py', 
"""
import myghty.component as component

def dostuff(m):
    pass

    
""")

        self.create_file(self.lib, 'pathmodule2.py', 
"""
import myghty.component as component

def lala(m):
    pass

""")

        pm2 = __import__('pathmodule2')
        
        self.create_directory(self.components, 'foo/bar')

        self.create_file(self.components, 'foo/bar/pathmodule3.py', 
"""
import myghty.component as component

def dostuff(m):
    pass

def index():
    pass

class lala:
    def __call__():
        pass
        
    def foofoo(m):
        pass
        
bar = lala()
""")

        self.create_file(self.components, 'foo/dhandler.py', 
"""
import myghty.component as component

def dostuff(m):
    pass

def index(m):
    pass
    
class lala:
    def __call__():
        pass
        
hoho = lala()
""")

        self.resolver = resolver.Resolver(
            module_root = [
                # a file path
                self.components,
            
                # an actual module
                pm2, 
                
            ],
        )            

    def class_tear_down(self):
        self.remove_file(self.components, 'pathmodule1.py')
        self.remove_file(self.components, 'pathmodule2.py')
        self.remove_file(self.components, 'foo/dhandler.py')
        self.remove_file(self.components, 'foo/bar/pathmodule3.py')

    def testpathmod1(self):
        resolution = self.resolver.resolve('/pathmodule1/dostuff', raise_error = True)
            
        dumpresolution(resolution)
        csource = resolution.csource
        self.assert_(csource is not None)

    def testpathmod2(self):
        resolution = self.resolver.resolve('/lala', raise_error = False)
        dumpresolution(resolution)
        csource = resolution.csource
        self.assert_(csource is not None)

    def testpathmod3(self):
        resolution = self.resolver.resolve('/foo/bar/pathmodule3/dostuff', raise_error = False)
        dumpresolution(resolution)
        csource = resolution.csource
        self.assert_(csource is not None)

    def testpathmod4(self):
        resolution = self.resolver.resolve('/foo/bar/pathmodule3/lala', raise_error = False)
        dumpresolution(resolution)
        csource = resolution.csource
        self.assert_(csource is not None)

    def testpathmod5(self):
        resolution = self.resolver.resolve('/foo/hoho', raise_error = False, enable_dhandler = True)
        dumpresolution(resolution)
        csource = resolution.csource
        self.assert_(csource is not None)

    def testpathmod6(self):
        resolution = self.resolver.resolve('/foo/bar/pathmodule3/', raise_error = False)
        dumpresolution(resolution)
        csource = resolution.csource
        self.assert_(csource is not None)

    def testpathmod7(self):
        resolution = self.resolver.resolve('/foo/bar/pathmodule3/bar/foofoo', raise_error = False)
        dumpresolution(resolution)
        csource = resolution.csource
        self.assert_(csource is not None)




class ModuleResolveTest(testbase.MyghtyTest):
    def class_set_up(self):
        self.create_file(self.lib, '__init__.py', "")
        self.create_file(self.lib, 'mymodule1.py', 
"""
import myghty.component as component
  
def mod1dostuff(m):
    pass
    
class TestComp(component.ModuleComponent):
  
   def do_component_init(self, **params):
      pass               
  
   def do_run_component(self, m, ARGS, **params):
      pass
""")

        self.create_file(self.lib, 'mymodule2.py', 
"""
import myghty.component as component

def dostuff(m):
    pass

def index(m):
    pass
    
class TestComp(component.ModuleComponent):
  
   def do_component_init(self, **params):
      pass               
  
   def do_run_component(self, m, ARGS, **params):
      pass
      
class foo(object):
    def run(self, m):
        pass

lala = foo()
""")


        self.mod2 = __import__('mymodule2')

        self.resolver = resolver.Resolver(
            module_components = [
                {'/index.myt' : 'mymodule1:TestComp'}, 
                {'/foo/.*': self.mod2.TestComp},
                {'/bar/.*': "mymodule2:dostuff"},
                {'/foo2/.*': self.mod2.lala.run},
                {'/foo3/.*': "mymodule2:lala.run"},
            ],
        )
    
    def class_tear_down(self):
        self.remove_file(self.lib, '__init__.py')
        self.remove_file(self.lib, 'mymodule1.py')
        self.remove_file(self.lib, 'mymodule1.pyc')
        self.remove_file(self.lib, 'mymodule2.py')
        self.remove_file(self.lib, 'mymodule2.pyc')
        try: del sys.modules['mymodule1']
        except KeyError:pass
        try: del sys.modules['mymodule2']
        except KeyError:pass    


    def testresolvestring(self):
        resolution = self.resolver.resolve('/index.myt', search_upwards = False, raise_error = False)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None and csource.id == 'module|mymodule1:class:TestComp', "unexpected id: " + csource.id)
        self.assert_(sys.modules.has_key('mymodule1'), 'module1 module not loaded into sys.modules')

    def testresolvemod(self):
        resolution = self.resolver.resolve('/foo/lala.myt', search_upwards = False, raise_error = False)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None and csource.id == 'module|mymodule2:class:TestComp', "unexpected id: " + csource.id)
        self.assert_(sys.modules.has_key('mymodule2'), 'module2 module not loaded into sys.modules')
    
    def testresolvemodfunction(self):
        resolution = self.resolver.resolve('/bar/lala', raise_error = False)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None)
        self.assert_(sys.modules.has_key('mymodule2'), 'module2 module not loaded into sys.modules')
        
    def testresolvemodmethod(self):
        resolution = self.resolver.resolve('/foo2/lala', raise_error = False)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None)

    def testresolvemodmethodstring(self):
        resolution = self.resolver.resolve('/foo3/lala', raise_error = False)
        csource = resolution.csource
        dumpresolution(resolution)
        self.assert_(csource is not None)

        
    def testnotfound(self):
        resolution = self.resolver.resolve('/foob/lala.myt', search_upwards = True, raise_error= False)
        self.assert_(resolution is None)
            

def dumpresolution (resolution):
    # TODO: echo flags
    if False:
        print "\nID: " + resolution.csource.id
        print "resolve: " + string.join(resolution.detail, ',')
        print "match: " + repr(resolution.match)
    
if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2, descriptions=False)
    unittest.main(testRunner=runner)        
