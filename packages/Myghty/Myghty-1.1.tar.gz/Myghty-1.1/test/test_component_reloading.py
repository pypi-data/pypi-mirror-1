# test/reload.py
"""Test that components reload properly when their source is touched.
"""
import unittest, os, shutil, stat, sys, time, warnings
from StringIO import StringIO

import testbase
from myghty.interp import Interpreter
from myghty.http.WSGIHandler import WSGIHandler
from myghty.resolver import NotFound
import myghty.importer

class ModuleRunner:
    """A minimal context for executing components.
    """
    def __init__(self, **params):
        self.interpreter = Interpreter(**params)

    def executeComponent(self, comp):
        buf = StringIO()
        self.interpreter.execute(comp, out_buffer=buf)
        return buf.getvalue()

class WSGIModuleRunner:
    """An WSGI context for executing components.

    We need this to test Routes components, since they require
    a request (r) object.
    """
    
    def __init__(self, **params):
        self.app = WSGIHandler(**params).handle
        
    def executeComponent(self, comp):
        environ = {
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'PATH_INFO': comp,
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': 8000,
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'HTTP_HOST': 'localhost:8000',
            'wsgi.version': (1,0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': StringIO(),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            }

        buf = StringIO()
        def start_response(status, response_headers):
            return buf.write
            
        for s in self.app(environ, start_response):
            buf.write(s)
            
        return buf.getvalue()
    
def purge_module(module_name):
    try:
        module = sys.modules[module_name]
    except KeyError:
        return

    base, ext = os.path.splitext(module.__file__)
    for ext in '.pyc', '.pyo':
        try:
            os.unlink(base + ext)
        except OSError:
            pass

    del sys.modules[module_name]
    
class ComponentReloadTests:
    """Abstract base class of tests for component reloading."""

    module_runner_class = ModuleRunner
    
    def setUp(self):
        # Blow away cache
        shutil.rmtree(os.path.join(self.cache, 'obj'),
                      ignore_errors=True)
        # Clear importer cache
        myghty.importer.modules.clear()

        self.createComponentSource()

        params = self.resolverArgs()
        self.module_runner = self.module_runner_class(data_dir=self.cache,
                                                      **params)


    def tearDown(self):
        self.removeComponentSource()

    def srcFile(self):
        """The full path the the module source file.
        """
        raise RuntimeError, "pure virtual"

    def srcText(self, text="howdy"):
        """Get the contents of the module source.

        The module, when run, will output the value of text.
        return text
        """
        raise RuntimeError, "pure virtual"

    def resolverArgs(self):
        """Get the resolver arguments to pass to the Myghty interperter.
        """
        raise RuntimeError, "pure virtual"

    def componentPath(self):
        """Get the (URL) path to the component.
        """
        raise RuntimeError, "pure virtual"

    def createComponentSource(self, text="howdy"):
        file(self.srcFile(), "w").write(self.srcText(text))

    def changeComponentSource(self, text="changed"):
        """Covertly changes the component source without changing mtime.
        """
        srcfile = self.srcFile()
        mtime = os.stat(srcfile)[stat.ST_MTIME]
        self.createComponentSource(text)
        os.utime(srcfile, (mtime, mtime))

    def removeComponentSource(self):
        os.unlink(self.srcFile())
        base, ext = os.path.splitext(self.srcFile())
        if ext == '.py':
            for ext in '.pyc', '.pyo':
                try:
                    os.unlink(base + ext)
                except OSError:
                    pass

    def executeComponent(self):
        return self.module_runner.executeComponent(self.componentPath())

    def testComponent(self, text="howdy"):
        """Test that we can resolve and execute our component.
        """
        self.failUnlessEqual(self.executeComponent(), text)

    def testReload(self):
        """Test that component gets reloaded when it is modified.
        """
        self.testComponent()
        time.sleep(1)
        self.removeComponentSource()
        self.createComponentSource(text="changed")
        self.testComponent("changed")

    def testCompileCache(self):
        """Test that component doesn't get reloaded when it is not modified.

        (Actually, tests that component doesn't get reloaded when the source
        is modified, but the source's mtime remains unchanged.)
        """
        self.testComponent()
        time.sleep(1)
        self.changeComponentSource(text="changed")
        self.testComponent()

################################################################
#
# (The actual unittest.TestCase sub-classes begin here.)
#
################################################################


class FileComponentReloadTests(ComponentReloadTests, testbase.MyghtyTest):
    
    def srcFile(self):
        return os.path.join(self.htdocs, "comp.myt")

    def srcText(self, text="howdy"):
        return text

    def resolverArgs(self):
        return {'component_root': self.htdocs}

    def componentPath(self):
        return "/comp.myt"
    
    
class ModuleComponentReloadTests(ComponentReloadTests, testbase.MyghtyTest):
    def setUp(self):
        purge_module('module')
        ComponentReloadTests.setUp(self)
        
    def srcFile(self):
        return os.path.join(self.lib, "module.py")

    def srcText(self, text="howdy"):
        return "def comp(m): m.write('%s')" % text

    def resolverArgs(self):
        try:
            del sys.modules['module']
        except KeyError:
            pass
        return {'module_components': [{'/mycomp': 'module:comp'}]}
    
    def componentPath(self):
        return "/mycomp"

class ModuleRootComponentReloadTests(ComponentReloadTests,
                                     testbase.MyghtyTest):
    def setUp(self):
        purge_module('modroot')
        ComponentReloadTests.setUp(self)

    def srcFile(self):
        return os.path.join(self.lib, "modroot.py")

    def srcText(self, text="howdy"):
        return """
class Top:
    def comp(self, m): m.write('%s')
top = Top()
""" % text

    def resolverArgs(self):
        try:
            del sys.modules['modroot']
            pass
        except KeyError:
            pass
        return {'module_root': ['modroot']}
    
    def componentPath(self):
        return "top/comp"

class WSGIModuleRootComponentReloadTests(ModuleRootComponentReloadTests):
    """Run the module_root test in a WSGI context.

    This exercised a buglet in myghty.http.HTTPHandler.py.
    """
    module_runner_class = WSGIModuleRunner



os.environ['MYGHTY_ENV'] = 'debug'   # Otherwise RoutesResolver pukes
try:
    from routes.base import Mapper

except ImportError:
    # Routes appears not to be installed
    class RoutesComponentReloadTests(unittest.TestCase):
        def testRoutesMissing(self):
            warnings.warn("Cannot import routes.base.  Skipping Routes tests.")

else:
    # Routes seems to be installed
    from myghty.ext.routeresolver import RoutesResolver

    class RoutesComponentReloadTests(ComponentReloadTests,
                                     testbase.MyghtyTest):
        module_runner_class = WSGIModuleRunner
    
        def srcFile(self):
            return os.path.join(self.lib, "routes_controller.py")

        def srcText(self, text="howdy"):
            return """
class RoutesController:
    def index(self, m, r):
        m.write('%s')
routes = RoutesController()
""" % text

        def resolverArgs(self):
            mapper = Mapper()
            mapper.connect(':controller/:action')

            routes_resolver = RoutesResolver(
                mapper=mapper,
                controller_root = self.lib)
            
            return {'resolver_strategy': [routes_resolver, NotFound()]}
    
        def componentPath(self):
            return "/routes"

class AnonymousFunctionComponentReloadTests(testbase.ComponentTester):
    def test(self):
        def mycomp(m):
            return 1
        comp1 = self.makeModuleComponent(mycomp)

        def mycomp(m):
            return 2
        comp2 = self.makeModuleComponent(mycomp)

        print comp1.component_source.id
        self.failIfEqual(comp1, comp2, "(Currently broken, expect failure.)")
        self.failUnlessEqual(self.runComponent(comp1), 1)
        self.failUnlessEqual(self.runComponent(comp2), 2)
        
if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2, descriptions=False)
    unittest.main(testRunner=runner)
