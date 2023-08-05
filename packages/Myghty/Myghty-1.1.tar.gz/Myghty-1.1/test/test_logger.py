import sys, StringIO, unittest
from myghty import request, interp
import testbase

class LoggingRequestImpl(request.DefaultRequestImpl):
    def __init__(self, logger=sys.stderr, **params):
        request.DefaultRequestImpl.__init__(self, **params)
        self.logger = logger

class TestRequestLogging(unittest.TestCase):
    def setUp(self):
        self.logger = StringIO.StringIO()
        self.m = interp.Interpreter().make_request(
            None,
            request_impl=LoggingRequestImpl(logger=self.logger))

    logOutput = property(lambda self: self.logger.getvalue())
    
    def testLog(self):
        self.m.log('howdy')
        self.failUnlessEqual(self.logOutput, "howdy\n")

    def testLogger(self):
        self.m.logger.write('foo')
        self.failUnlessEqual(self.logOutput, "foo\n")

    def testLoggerWritelines(self):
        self.m.logger.writelines(['foo', 'bar'])
        self.failUnlessEqual(self.logOutput, "foo\nbar\n")

class TestWarningsGetLogged(testbase.ComponentTester):
    def test(self):
        log = StringIO.StringIO()
        self.runComponent('''% import warnings
                             % warnings.warn("Boo!")
                             ''',
                          config={'request_impl':
                                  LoggingRequestImpl(logger=log)})
        output = log.getvalue()
        self.failUnlessEqual(output[output.rindex('.myt'):],
                             '.myt:2: UserWarning: Boo!\n'
                             '  % warnings.warn("Boo!")\n')

class TestWarningsGetLoggedMemory(TestWarningsGetLogged):
    """Same as above, except with no compile cache.
    """
    # In this case, the keys in interpreter.reverse_lookup
    # start with 'memory:'.

    config = dict(data_dir=None)

    def testSanity(self):
        self.runComponent(' ')
        self.failUnless(filter(lambda s: s.startswith('memory:'),
                               self.interpreter.reverse_lookup.keys()))
        

if __name__ == '__main__':
    unittest.main()
