"""test/test_testbase.py

Tests for stuff in test/testbase.py.
"""

import re, sys, unittest
import testbase
from myghty.component import Component

class ComponentTesterTests(testbase.ComponentTester):
    """Test cases for ComponentTester
    """
    
    srcFiles = { 'htdocs/foo.myt': 'foo',
                 'lib/barmod.py': 'def f(m): m.write("bar")',
                 }
    config = dict(module_components=[{'bar': 'barmod:f'}])
    
    def testFoo(self):
        self.runComponent("foo.myt")
        self.failUnlessEqual(self.output, 'foo')

    def testBar(self):
        self.runComponent("bar")
        self.failUnlessEqual(self.output, 'bar')

    def testRunInlineComponent(self):
        self.runComponent(
            """# comment
            howdy
            """)
        self.failUnlessEqual(self.tidyoutput, 'howdy')

    def testRunInlineModuleComponent(self):
        def comp(m):
            m.write("output")
        self.runComponent(comp)
        self.failUnlessEqual(self.output, 'output')

    def testMakeModule(self):
        testmod = self.makeModule("def f(m): m.write('boo')")
        self.runComponent(testmod.f)
        self.failUnlessEqual(self.output, "boo")

    def testMakeMemoryComponent(self):
        comp = self.makeMemoryComponent(
            '''
            <%flags>
                trim = "both"
            </%flags>
            from memory
            ''')
        self.failUnless(isinstance(comp, Component))
        self.runComponent(comp)
        self.failUnlessEqual(self.output, "from memory")


class TestUnwrapErrors(testbase.ComponentTester):
    """Test advice added to unittest.TestResult.addError()

    Exceptions which are wrapped in a myghty.Error should be
    unwrapped before the error is reported.
    """
    def x_test(self):
        self.runComponent("""% message = 'Boo'
                             % raise RuntimeError, message""")
        print self.output

    def test(self):
        mytest = unittest.defaultTestLoader.loadTestsFromName(
            '%s.TestUnwrapErrors.x_test' % __name__)
        result = unittest.TestResult()
        mytest.run(result)
        
        self.failUnlessEqual(len(result.errors), 1)
        failed, message = result.errors[0]
        last_line = message.rstrip().split('\n')[-1]
        self.failUnlessEqual("RuntimeError: Boo", last_line)
        
if __name__ == '__main__':
    unittest.main()
