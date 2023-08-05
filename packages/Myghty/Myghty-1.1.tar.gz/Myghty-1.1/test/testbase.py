import unittest, os, sys, StringIO, itertools, inspect, re, tempfile, time

from myghty import util, interp, exception, csource, importer
from myghty.component import Component


class MyghtyTest(unittest.TestCase):
    def __init__(self, *args, **params):
        unittest.TestCase.__init__(self, *args, **params)
        
        # make ourselves a Myghty environment
        self.root = os.path.abspath(os.path.join(os.getcwd(),
                                                 'testroot',
                                                 self.__class__.__module__,
                                                 self.__class__.__name__))
        
        # some templates
        self.htdocs = os.path.join(self.root, 'htdocs')
        
        # some more templates
        self.components = os.path.join(self.root, 'components')
        
        # data dir for cache, sessions, compiled
        self.cache = os.path.join(self.root, 'cache')
        
        # lib dir for some module components
        self.lib = os.path.join(self.root, 'lib')
        sys.path.insert(0, self.lib)
        
        for path in (self.htdocs, self.components, self.cache, self.lib):
            util.verify_directory(path)
        
        self.class_set_up()

    def class_set_up(self):
        pass

    def class_tear_down(self):
        pass
        
    def __del__(self):
        self.class_tear_down()
        
    def create_file(self, dir, name, contents):
        file = os.path.join(dir, name)
        f = open(file, 'w')
        f.write(contents)
        f.close()
        
    def create_directory(self, dir, path):
        util.verify_directory(os.path.join(dir, path))
        
    def remove_file(self, dir, name):
        if os.access(os.path.join(dir, name), os.F_OK):
            os.remove(os.path.join(dir, name))


def deindent(text):
    """De-indent docstring like text.
    """
    # Hack use inspect.getdoc() to do the de-indentation
    return inspect.getdoc(property(doc=text))
    
class ComponentTester(MyghtyTest):

    config = {}

    srcFiles = {}
    
    def __init__(self, *args, **params):
        MyghtyTest.__init__(self, *args, **params)

        # Clean up from previous runs
        now = time.time()
        for root, dirs, files in os.walk(self.root):
            try:
                for fn in [ os.path.join(root, f) for f in files ]:
                    if os.stat(fn).st_mtime < now - 60:
                        os.unlink(fn)
            except IOError:
                pass
            
    def class_set_up(self):
        MyghtyTest.class_set_up(self)
        for name, content in self.srcFiles.items():
            self.createSrcFile(name, content)

    def createSrcFile(self, filename, content):
        m = re.match(r'\A ( htdocs | lib | components ) /+', filename, re.X)
        if m:
            filename = filename[m.end():]
            srcdir = getattr(self, m.group(1))
        else:
            srcdir = self.htdocs
        self.create_file(srcdir, filename, deindent(content))

    def makeInterpreter(self):
        config = dict(component_root=self.htdocs,
                      raise_error=True,
                      data_dir=self.cache
                      )
        config.update(self.config)
        return interp.Interpreter(**config)

    def setUp(self):
        self.interpreter = self.makeInterpreter()
        self.outputBuffer = StringIO.StringIO()

    output = property(lambda self: self.outputBuffer.getvalue())

    tidyoutput = property(lambda self: re.sub(r'\s+', ' ',
                                              self.output.strip()))

    def create_anonymous_file(self, src, dir=None, suffix='.myt'):
        if dir is None:
            dir = os.path.join(self.root, 'tmp')
        util.verify_directory(dir)
        fd, path = tempfile.mkstemp(prefix='anon', suffix=suffix, dir=dir,
                                    text=True)
        os.write(fd, deindent(src))
        os.close(fd)
        return os.path.basename(path)

    def makeModule(self, src):
        # create a python module in self.lib
        name = self.create_anonymous_file(src, dir=self.lib, suffix='.py')
        return importer.module(os.path.splitext(name)[0])
        
    def makeModuleComponent(self, arg):
        # src can be a string like "module:callable", etc...
        # or it can be an actually callable, etc...
        return self.interpreter.load_module_component(arg=arg)
        
    def makeFileBasedComponent(self, src):
        name = self.create_anonymous_file(src, dir=self.htdocs)
        return self.loadComponent("/%s" % name)

    def makeMemoryComponent(self, src):
        return self.interpreter.make_component(deindent(src))

    def makeComponent(self, src):
        """Make a component of the default sort.

        The idea is that this can be specialized by subclasses to change
        the type of component that gets constructed by code like:

             self.runComponent('''# Here's source code for some component
                               foo
                               ''')
        """                       
        return self.makeFileBasedComponent(src)
    
    def loadComponent(self, component):
        if not isinstance(component, basestring):
            # Wrap callable, etc... to a module component
            return self.makeModuleComponent(component)

        if re.search(r'\s', component):
            # if string contains white-space, interpret it as the
            # source for a myghty component, rather than the path
            # to be resolved.
            return self.makeComponent(component)

        return self.interpreter.load(component)

    def runComponent(self, component, config={}, **request_args):
        request_config = dict(request_args=request_args,
                              out_buffer=self.outputBuffer
                              )
        request_config.update(config)

        if not isinstance(component, Component):
            component = self.loadComponent(component)

        return self.interpreter.execute(component, **request_config)

    def failUnlessRaisesWrappedError(self, wrapped_exception,
                                     func, *args, **kw):
        def _unwrap_error(func, args, kw):
            try:
                func(*args, **kw)
            except exception.Error, error:
                if error.wrapped is None:
                    raise
                raise error.wrapped
            except:
                self.fail("expected myghty Error, got %s"
                          % sys.exc_info()[1])
        self.failUnlessRaises(wrapped_exception, _unwrap_error, func, args, kw)


# Add advice to unittest.TestResult.addError to unwrap wrapped Errors
TestResult_addError = unittest.TestResult.addError
instancemethod = type(TestResult_addError)
def addError(self, test, err):
    if isinstance(err[1], exception.Error):
        err = getattr(err[1], 'raw_excinfo', err)
    TestResult_addError.im_func(self, test, err)
unittest.TestResult.addError = addError


def runTests(suite):
    runner = unittest.TextTestRunner(verbosity = 2, descriptions =1)
    runner.run(suite)

if __name__ == '__main__':
    unittest.main()
    
