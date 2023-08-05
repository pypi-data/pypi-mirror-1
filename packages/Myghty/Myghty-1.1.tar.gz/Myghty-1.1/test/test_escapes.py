import codecs, re, sys, unittest, warnings
from myghty import escapes

LATIN1_CHARS = ''.join(map(chr, range(256))).decode('latin1')

class EscapeTests(object):
    def escape(self, text):
        raise NotImplementedError

    def unescape(self, text):
        raise NotImplementedError

    TEST_CHARS = LATIN1_CHARS

    def testEscapedChars(self):
        escaped =  ''.join([char for char in self.TEST_CHARS
                            if self.escape(char) != char])
        should_escape = ''.join(re.findall(self.should_escape_re,
                                           self.TEST_CHARS))

        if escaped != should_escape:
            missing = ''.join([char for char in should_escape
                               if char not in escaped])
            shouldnt = ''.join([char for char in escaped
                                if char not in should_escape])
            self.failUnless(missing or shouldnt)
            if missing:
                self.fail("Should have escaped: %s" % repr(missing))
            if shouldnt:
                self.fail("Should not have escaped: %s" % repr(shouldnt))

    def testTakesUnicode(self):
        frappe = self.escape(u'frapp\u00C9')
        self.failUnless(isinstance(frappe, basestring))
        self.failUnlessEqual(frappe[:5], "frapp")

    def testTakesStr(self):
        hello = self.escape('hello')
        self.failUnless(isinstance(hello, basestring))
        self.failUnlessEqual(hello, "hello")

    def testStrMustBeAscii(self):
        if codecs.lookup(sys.getdefaultencoding()) != codecs.lookup('ascii'):
            warnings.warn("Skipping testStrMustBeAscii")
            return
        self.failUnlessRaises(UnicodeError, self.escape, '\xa0')

    def testUnescape(self):
        escaped = self.escape(self.TEST_CHARS)
        try:
            unescaped = self.unescape(escaped)
        except NotImplementedError:
            return
        unicode(unescaped)
        self.failUnlessEqual(unescaped, self.TEST_CHARS)
        
class html_escape_tests(EscapeTests, unittest.TestCase):
    escape = staticmethod(escapes.html_escape)
    should_escape_re = r'["&<>]'
    def testStrMustBeAscii(self): pass  # Is this right?

class xml_escape_tests(EscapeTests, unittest.TestCase):
    escape = staticmethod(escapes.xml_escape)
    should_escape_re = '["&\'<>]'
    def testStrMustBeAscii(self): pass  # Is this right?

class url_escape_tests(EscapeTests, unittest.TestCase):
    escape = staticmethod(escapes.url_escape)
    unescape = staticmethod(escapes.url_unescape)
    should_escape_re = r'[^-.\w]'

    def testPlus(self):
        self.failUnlessEqual(self.unescape('+'), ' ')
        self.failUnlessEqual(self.unescape('%2b'), '+')
        self.failUnlessEqual(self.escape(' '), '+')
        self.failUnlessEqual(self.escape('+'), '%2B')
        

class html_entities_escape_tests(EscapeTests, unittest.TestCase):
    escape = staticmethod(escapes.html_entities_escape)
    unescape = staticmethod(escapes.html_entities_unescape)

    should_escape_re = '["&<>\xa0-\xff]'

class htmlentityreplace_errors_tests(unittest.TestCase):
    def testEuro(self):
        self.failUnlessEqual(
            u'The cost was \u20ac12.'.encode('latin1', 'htmlentityreplace'),
            'The cost was &euro;12.'
            )
        
    def testNumeric(self):
        self.failUnlessEqual(u'\x81'.encode('ascii', 'htmlentityreplace'),
                             '&#x81;')

if __name__ == '__main__':
    unittest.main()
