# encoding: latin1
# test_html_errors.py
"""Test HTML formatting of errors.
"""
import re, unittest
import testbase
from myghty.exception import Error, Syntax

class HTMLDecodingErrorBase(object):

    expected_error = Error
    wrapped_error = None
    expected_html = "euro:&euro;"
    
    def _testComponent(self, component_maker):
        try:
            self.runComponent(component_maker(self.csource))
        except Error, ex:
            if self.expected_error:
                self.failUnless(isinstance(ex, self.expected_error))
            if self.wrapped_error:
                self.failUnless(isinstance(ex.wrapped, self.wrapped_error))
        else:
            self.fail()

        if self.expected_html not in ex.htmlformat():
            print ex.htmlformat()
        self.failUnless(self.expected_html in ex.htmlformat())
        
    def testFileComponent(self):
        self._testComponent(self.makeFileBasedComponent)

    def testMemoryComponent(self):
        self._testComponent(self.makeMemoryComponent)

class PythonErrorInComponentTests(HTMLDecodingErrorBase,
                                  testbase.ComponentTester):
    csource = """# encoding: iso-8859-15
                 % m.setTYPO_output_encoding('UTF-8')
                 euro:\xa4
                 <br />encoding is: <% m.output_encoding %>
                 """

    wrapped_error = AttributeError

class PythonErrorInComponentCodeline(HTMLDecodingErrorBase,
                                  testbase.ComponentTester):
    csource = """# encoding: iso-8859-15
                 % u'euro:\xa4' + 1
                 """

    wrapped_error = TypeError
   
class SyntaxErrorInComponentTests(HTMLDecodingErrorBase,
                                  testbase.ComponentTester):
    
    csource = """# encoding: iso-8859-15
                 <%python scope='bogus'>
                 </%python>
                 euro:\xa4
                 """

    expected_error = Syntax

class ErrorInModuleComponent(HTMLDecodingErrorBase,
                             testbase.ComponentTester):
    csource = """# encoding: iso-8859-15
                 def f(m):
                     return u'euro:\xa4' + 1
                 """

    def testFileComponent(self):
        def comp_maker(csource):
            module = self.makeModule(csource)
            return module.f
        self._testComponent(comp_maker)

    def testMemoryComponent(self):
        pass


class AnonymousPythonErrorInComponentTests(HTMLDecodingErrorBase,
                                           testbase.ComponentTester):
    csource = """# encoding: iso-8859-15
                 <%python>
                 g = dict()
                 eval(compile('# encoding: iso-8859-15\\n'
                              'def f(): return u\"euro:\xa4\" + 1\\n',
                              '<memory>', 'exec', 0, True), g, g)
                 f = g['f']
                 </%python>
                 % f()
                 """

    wrapped_error = TypeError

    expected_html = "2: None"


################################################################        

import codecs, StringIO
from myghty.exception import _parse_encoding as parse_encoding

class parse_encoding_Tests(testbase.MyghtyTest):
    def testParseEncoding(self, src="", coding=None):
        f = StringIO.StringIO(src)
        try:
            self.failUnlessEqual(parse_encoding(f), coding)
        finally:
            self.failUnlessEqual(f.read(), src) # test that file is rewound
        
    def testSimple(self):
        self.testParseEncoding("# -*- coding: foo -*-\n", 'foo')
        self.testParseEncoding("# First line \n"
                               "# vim:fileencoding=bar\n",
                               'bar')
        self.testParseEncoding("# First line\n"
                               "# Second line\n"
                               "# -*- coding: foo -*-\n",
                               None)

    def testBom(self):
        self.testParseEncoding(codecs.BOM_UTF8 + "# Howdy\n",
                               'utf_8')

    def testBadBom(self):
        self.failUnlessRaises(SyntaxError,
                              self.testParseEncoding,
                              codecs.BOM_UTF8 + "# coding: ascii\n",
                              'utf_8')

        self.failUnlessRaises(SyntaxError,
                              self.testParseEncoding,
                              codecs.BOM_UTF8 + "'line1'\n# coding: ascii\n",
                              'utf_8')

    def testEsoteric(self):
        self.testParseEncoding('print """\n'
                               '# coding: foo\n'
                               '"""\n',
                               None)

        self.testParseEncoding('(\n'
                               '# coding: foo\n'
                               ')\n',
                               None)


            
if __name__ == '__main__':
    unittest.main()
