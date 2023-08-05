import testbase
import myghty.interp as interp
import myghty.component as component
import myghty.csource as csource
import myghty.resolver as resolver
import myghty.request as request
import myghty.exception as exception
import myghty.cache as cache
import unittest, sys, string, StringIO
import posixpath as unixpath

class ResolverStub:
    def __init__(self, result):
        self.result = result
        
    def resolve(self, uri, **params):
        return self.result


class ComponentRunner(testbase.MyghtyTest):
    
    def assert_exec(self, csource, args, output, interpreter = None):
        if interpreter is None:
            interpreter = interp.Interpreter()
        comp = interpreter.load_component(csource)
        buf = StringIO.StringIO()
        interpreter.execute(comp, request_args = args, out_buffer = buf)
        self.failUnlessEqual(buf.getvalue(), output)

    def assert_component(self, component, args, output, interpreter):
        buf = StringIO.StringIO()
        interpreter.execute(component, request_args = args, out_buffer = buf)
        self.assert_(buf.getvalue() == output)
        
class InheritTest(testbase.MyghtyTest):
    def setUp(self):
        self.create_file(self.components, 'autohandler', 'im an autohandler') 
    
    def tearDown(self):
        self.remove_file(self.components, 'autohandler')
            
    def testrecursiveparent(self):
        """test that a root autohandler component wont let itself be a parent of itself"""

        acs = csource.FileComponentSource("fooid", "main", "autohandler", unixpath.join(self.components, "autohandler"))
        
        i = interp.Interpreter(resolver = ResolverStub(resolver.Resolution(acs, None)))
        comp = i.load_component(acs)
        
        self.assert_(comp is not comp.parent_component, "test failed, returned recursive parent")
        self.assert_(comp.parent_component is None, "test failed, returned a parent component")

class AttrTest(ComponentRunner):
    def setUp(self):
        self.create_file(self.htdocs, "compa.myt", 
"""<%attr>
foo = 'fooval'
</%attr>
% m.call_next()""")
        self.create_file(self.htdocs, "compb.myt", 
"""<%flags>
inherit = '/compa.myt'
</%flags>\
<%attr>
bar = 'barval'
</%attr>
% m.call_next()""")
        self.create_file(self.htdocs, "compc.myt", 
"""<%flags>
inherit = '/compb.myt'
</%flags>\
<% m.base_component.attributes['bar'] %>
<% m.base_component.attributes['foo'] %>""")

    def testattrinherit(self):
        interpreter = interp.Interpreter(data_dir=self.cache, component_root=self.htdocs)
        self.assert_component('compc.myt', {}, "barval\nfooval", interpreter = interpreter)
        
    def tearDown(self):
        self.remove_file(self.htdocs, 'compa.myt')
        self.remove_file(self.htdocs, 'compb.myt')
        self.remove_file(self.htdocs, 'compc.myt')

class CacheTest(ComponentRunner):
    def setUp(self):
        self.create_file(self.htdocs, "memorytest.myt", """
<%flags>
    use_cache=True
    cache_type='memory'
</%flags>
im the memory test.
""")
        self.create_file(self.htdocs, "filetest.myt", """
<%flags>
    use_cache=True
    cache_type='file'
</%flags>
im the file test.
""")

    def testmemory(self):
        acs = csource.FileComponentSource("memid", "main", "memorytest.myt", unixpath.join(self.htdocs, "memorytest.myt"))
        interpreter = interp.Interpreter()
        self.assert_exec(acs, {}, "\nim the memory test.\n", interpreter = interpreter)
        self.assert_exec(acs, {}, "\nim the memory test.\n", interpreter = interpreter)
        comp = interpreter.code_cache['memid']
        self.assert_(interpreter.make_request(comp).get_cache(comp, type='memory')['_self'][0].getvalue() == "\nim the memory test.\n")

    def testfile(self):
        acs = csource.FileComponentSource("fileid", "main", "filetest.myt", unixpath.join(self.htdocs, "filetest.myt"))
        interpreter = interp.Interpreter(data_dir=self.cache)
        self.assert_exec(acs, {}, "\nim the file test.\n", interpreter = interpreter)
        self.assert_exec(acs, {}, "\nim the file test.\n", interpreter = interpreter)
        comp = interpreter.code_cache['fileid']
        self.assert_(interpreter.make_request(comp).get_cache(comp, type='file')['_self'][0].getvalue() == "\nim the file test.\n")
        
    def tearDown(self):
        self.remove_file(self.htdocs, 'memorytest.myt')
        self.remove_file(self.htdocs, 'filetest.myt')

################################################################
        
class MoreMemoryCacheTests(ComponentRunner):

    cache_type = 'memory'
    
    def setUp(self):
        # Basically we just need a component...
        self.create_file(self.htdocs, "cachetest.myt", "im the cache tester.")
        self.interp = interp.Interpreter(data_dir=self.cache)
        acs = csource.FileComponentSource("id", "main", "cachetest.myt",
                                          unixpath.join(self.htdocs,
                                                        "cachetest.myt"))
        self.comp = self.interp.load_component(acs)

    def tearDown(self):
        self.remove_file(self.htdocs, 'cachetest.myt')

    def get_cache(self):
        """Get a fresh Cache object for the component
        """
        return cache.Cache(component=self.comp, type=self.cache_type,
                           data_dir=self.cache)

    def cache_keys(self):
        """List the keys in our components cache.

        This lists the keys in the underlying NamespaceManager, not just
        those keys which are cached in the Cache object.
        """
        cache = self.get_cache()
        nm = cache.get_container(None).get_namespace_manager()
        # We introduced a bogus None key with the above get_container,
        # so filter it out...
        nm.acquire_read_lock()
        try:
            return [ x for x in nm.keys() if x is not None ]
        finally:
            nm.release_read_lock()

    def testClear(self):
        """Test that cache.clear() really works.

        We test that all entries in the underlying NamespaceManager actually
        get cleared.
        """
        cache = self.get_cache()
        cache.get_value('key1', createfunc=lambda: 'value1')
        self.failUnlessEqual(cache.dict.keys(), ['key1'])
        self.failUnlessEqual(self.cache_keys(), ['key1'])

        cache = self.get_cache()
        self.failUnlessEqual(cache.dict.keys(), [])
        self.failUnlessEqual(self.cache_keys(), ['key1'])

        cache.clear()
        self.failUnlessEqual(self.cache_keys(), [])

class MoreFileCacheTests(MoreMemoryCacheTests):
    cache_type = 'file'

class MoreDbmCacheTests(MoreMemoryCacheTests):
    cache_type = 'dbm'

class MoreMemcachedCacheTests(MoreMemoryCacheTests):
    cache_type = 'ext:memcached'

    def testClear(self):
        # FIXME:
        self.fail("MemcachedNamespaceManager.do_remove() is currently broken."
                  "  (It is a no-op.)")
    
    
################################################################

class myclass(component.ModuleComponent):
    def do_run_component(self, m, **params):
        m.write('hello world')

class ClassComponentTest(ComponentRunner):
    def testrun(self):

        acs = csource.ModuleComponentSource(arg = myclass)
        self.assert_exec(acs, {}, "hello world")

class FunctionComponentTest(ComponentRunner):
    def testmarg(self):
        def mymethod(m):
            m.write("hello world")
            
        acs = csource.ModuleComponentSource(arg = mymethod)
        self.assert_exec(acs, {}, "hello world")

    def testnoarg(self):
        def mymethod():
            request.instance().write("hello world")
            
        acs = csource.ModuleComponentSource(arg = mymethod)
        self.assert_exec(acs, {}, "hello world")

    def testmandarg(self):
        def mymethod(m, ARGS):
            m.write("hello world, args: " + repr(ARGS))
        
        acs = csource.ModuleComponentSource(arg = mymethod)
        self.assert_exec(acs, {'foo': 'bar'}, "hello world, args: " + repr({'foo': 'bar'}))

    def testcustomargs(self):
        def mymethod(x, y, z = 7):
            request.instance().write("hello world, args: %s %s %s" % (repr(x), repr(y), repr(z)))
        
        acs = csource.ModuleComponentSource(arg = mymethod)
        args = dict(x = 5, y = 2)
        self.assert_exec(acs, args, "hello world, args: 5 2 7")


class MethodComponentTest(ComponentRunner):
    def class_set_up(self):
        self.create_file(self.lib, 'mymodule3.py', 
"""
import myghty.component as component

def dostuff(m):
    m.write("this is dostuff")

def index(m):
    m.write("this is index")

class foo:
    def __init__(self):
        self.x = 7
    def __call__(self, m):
        m.write("this is foo __call__")
        
    def dofoo(self, m):
        m.write("this is foo dofoo(), x is " + str(self.x) )
        
bar = foo()

""")

        self.mymod2 = __import__('mymodule3')

    def class_tear_down(self):
        self.remove_file(self.lib, 'mymodule3.py')

    def testmodfunc(self):
        dostuff = self.mymod2.dostuff
        acs = csource.ModuleComponentSource(arg= dostuff)
        self.assert_exec(acs, {}, "this is dostuff")

    def testmodmethod(self):
        bar = self.mymod2.bar
        acs = csource.ModuleComponentSource(arg = bar.dofoo)
        self.assert_exec(acs, {}, "this is foo dofoo(), x is 7")

    def testmodcallable(self):
        acs = csource.ModuleComponentSource(arg = self.mymod2.bar)
        self.assert_exec(acs, {}, "this is foo __call__")
        
if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2, descriptions=False)
    unittest.main(testRunner=runner)
                
