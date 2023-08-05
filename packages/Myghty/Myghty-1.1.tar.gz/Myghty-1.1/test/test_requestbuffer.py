# test/test_encoding.py
"""Test that stuff in myghty.requestbuffer
"""

import unittest, os, sys, codecs, StringIO, cStringIO, cPickle, warnings
import testbase
from myghty import importer, util
from myghty.requestbuffer import \
     UnicodeRequestBuffer, StrRequestBuffer, MismatchedPop

def _is_ascii_superset(encoding):
    ASCII_CHARS = ''.join(map(chr, range(128)))
    try:
        return ASCII_CHARS.decode(encoding) == ASCII_CHARS.decode('ascii')
    except UnicodeDecodeError:
        return False

if not _is_ascii_superset(sys.getdefaultencoding()):
    warnings.warn("System default encoding is not a subset of ASCII. "
                  "Many of these tests will fail.",
                  UserWarning)

REPLACEMENT_CHARACTER = u'\ufffd'

class TestBuffer:
    """A StringIO which supports only a limited set of file operations.
    """
    def __init__(self):
        self.buf = StringIO.StringIO()

    def write(self, text):
        self.buf.write(text)

    def __str__(self):
        return self.buf.getvalue()

def test_filter(text):
    return "f(%s)" % text

class _RequestBufferTests(object):
    
    def setUp(self):
        self.outputBuffer = TestBuffer()

    output = property(lambda self: str(self.outputBuffer))

    def testBuffering(self):
        buf = self.getRequestBuffer()
        buf.write("a")
        self.failUnlessEqual(self.output, "a")
        buf.push_buffer()
        buf.write("b")
        self.failUnlessEqual(self.output, "a")
        buf.push_buffer()
        buf.write("c")
        self.failUnlessEqual(self.output, "a")
        buf.pop_buffer()
        self.failUnlessEqual(self.output, "a")
        buf.pop_buffer()
        self.failUnlessEqual(self.output, "abc")

    def testBufferNoFlush(self):
        buf = self.getRequestBuffer()
        buf.write("a")
        self.failUnlessEqual(self.output, "a")
        buf.push_buffer()
        buf.write("b")
        buf.pop_buffer(discard=True)
        self.failUnlessEqual(self.output, "a")

    def testFilter(self):
        buf = self.getRequestBuffer()
        buf.push_filter(test_filter)
        buf.write("a")
        buf.write("b")
        self.failUnlessEqual(self.output, "f(a)f(b)")
        buf.push_buffer()
        buf.write("c")
        buf.write("d")
        buf.pop_buffer()
        self.failUnlessEqual(self.output, "f(a)f(b)f(cd)")
        buf.pop_filter()
        buf.write("e")
        self.failUnlessEqual(self.output, "f(a)f(b)f(cd)e")
        
    def testCaptureBuffer(self):
        buf = self.getRequestBuffer()
        buf.push_buffer()
        buf.write('a')
        self.failUnlessEqual(self.output, '')

        cbuf = util.StringIO()
        buf.push_capture_buffer(cbuf)
        buf.write('b')
        self.failUnlessEqual(cbuf.getvalue(), "b")
        buf.flush()
        self.failUnlessEqual(self.output, '')
        
        buf.push_capture_buffer()
        buf.write("c")
        cbuf2 = buf.pop_capture_buffer()
        self.failUnlessEqual(cbuf2.getvalue(), "c")

        self.failUnlessEqual(cbuf, buf.pop_capture_buffer())
        self.failUnlessEqual(cbuf.getvalue(), "b")
        self.failUnlessEqual(self.output, '')
        buf.pop_buffer()
        self.failUnlessEqual(self.output, 'a')

    def testFlush(self):
        buf = self.getRequestBuffer()
        buf.push_buffer()
        buf.write("howdy")
        self.failUnlessEqual(self.output, "")
        buf.flush()
        self.failUnlessEqual(self.output, "howdy")

    def testMismatchedPop(self):
        buf = self.getRequestBuffer()
        self.failUnlessRaises(MismatchedPop, buf.pop_buffer)
        buf.push_buffer()
        self.failUnlessRaises(MismatchedPop, buf.pop_filter)
        buf.pop_buffer()

    def testSaveAndRestoreState(self):
        buf = self.getRequestBuffer()
        buf.push_filter(test_filter)
        state = buf.get_state()
        buf.push_buffer()
        buf.write('b')
        self.failUnlessEqual(self.output, '')
        buf.pop_to_state(state)
        self.failUnlessEqual(self.output, 'f(b)')
        buf.write('a')
        self.failUnlessEqual(self.output, 'f(b)f(a)')
        
class StrRequestBufferTests(_RequestBufferTests, unittest.TestCase):
    
    def getRequestBuffer(self):
        return StrRequestBuffer(self.outputBuffer)

    def testWriteUnicodeFails(self):
        buf = self.getRequestBuffer()
        self.failUnlessRaises(UnicodeEncodeError,
                              buf.write, REPLACEMENT_CHARACTER)

    def testBinarySafe(self):
        buf = self.getRequestBuffer()
        all_chars = ''.join(map(chr, range(256)))
        buf.write(all_chars)
        self.failUnlessEqual(self.output, all_chars)
        
    def testWriteUnicodeOkay(self):
        buf = self.getRequestBuffer()
        buf.write(u'abc')
        self.failUnlessEqual(self.output, 'abc')
        
    def testFilterUnicodeOutput(self):
        def filt(text):
            if text == 'a':
                return REPLACEMENT_CHARACTER
            else:
                return unicode(text) * 2
        buf = self.getRequestBuffer()
        buf.push_filter(filt)
        self.failUnlessRaises(UnicodeEncodeError, buf.write, "a")
        buf.write('b')
        self.failUnlessEqual(self.output, "bb")
        
    def testChangeOutputEncodingFails(self):
        buf = self.getRequestBuffer()
        self.failUnless(buf.encoding is None)
        self.failUnlessRaises(AttributeError, setattr, buf, 'encoding', 'ascii')
    def testChangeEncodingErrorsFails(self):
        buf = self.getRequestBuffer()
        self.failUnless(buf.errors is None)
        self.failUnlessRaises(AttributeError, setattr, buf, 'errors', 'strict')


    
class UnicodeRequestBufferTests(_RequestBufferTests, unittest.TestCase):

    def setUp(self):
        self.outputBuffer = TestBuffer()

    output = property(lambda self: str(self.outputBuffer))

    def getRequestBuffer(self, encoding='ascii', errors='strict'):
        return UnicodeRequestBuffer(self.outputBuffer, encoding, errors)
    
    def testBufferMixedEncoding(self):
        buf = self.getRequestBuffer('latin1')
        buf.push_buffer()
        buf.write("a")
        buf.write(u'b')
        buf.write(unicode("\xc2\xa0", 'utf8'))
        self.failUnlessEqual(self.output, '')
        buf.pop_buffer()
        self.failUnlessEqual(self.output, 'ab\xa0')

    def testBufferMixedEncodingNoFlush(self):
        buf = self.getRequestBuffer('latin1')
        buf.push_buffer()
        buf.write("a")
        buf.write(u'b')
        buf.write(unicode("\xc2\xa0", 'utf_8'))
        self.failUnlessEqual(self.output, '')
        buf.pop_buffer(discard=True)
        self.failUnlessEqual(self.output, '')

    def testFilterUnicodeOutput(self):
        def filt(text):
            return u'\u20ac'

        buf = self.getRequestBuffer('iso-8859-15')
        buf.push_filter(filt)
        buf.write("a")
        self.failUnlessEqual(self.output, "\xa4")
        
    def testRecoding(self):
        buf = self.getRequestBuffer('utf_8')
        buf.write(unicode('\xa0', 'latin1'))
        self.failUnlessEqual(self.output, '\xc2\xa0')

    def testRecodingError(self):
        buf = self.getRequestBuffer('utf_8')
        buf.push_capture_buffer(buffer=cStringIO.StringIO())
        # Can't recode &nbsp; to ascii
        self.failUnlessRaises(UnicodeError,
                              buf.write, unicode('\xa0', 'latin1'))
        buf.write('a')
        cbuf = buf.pop_capture_buffer()
        self.failUnlessEqual(cbuf.getvalue(), 'a')
        self.failUnlessEqual(self.output, '')

    def testBufferIsEncodingTransparent(self):
        buf = self.getRequestBuffer('utf_8')
        buf.push_buffer()               # This buffer does not encode to ascii
        buf.write(unicode("\xa0", 'latin1'))
        self.failUnlessEqual(self.output, '')
        buf.flush()
        self.failUnlessEqual(self.output, '\xc2\xa0')

    def testUnicodeWrites(self):
        buf = self.getRequestBuffer('iso-8859-15')
        EURO_SIGN = u'\u20ac'
        buf.write(EURO_SIGN)
        self.failUnlessEqual(self.output, '\xa4')

        # There's no euro symbol in latin1
        buf = self.getRequestBuffer('iso-8859-1')
        self.failUnlessRaises(UnicodeEncodeError,
                              buf.write, EURO_SIGN)

    def testChangeOutputEncoding(self):
        nbsp = unicode('\xa0', 'latin1')
        
        buf = self.getRequestBuffer('latin1')
        self.failUnlessEqual(buf.encoding, 'latin1')
        buf.write(nbsp)
        self.failUnlessEqual(self.output, '\xa0')

        buf.set_encoding('utf-8')
        self.failUnlessEqual(buf.encoding, 'utf-8')
        buf.write(nbsp)
        self.failUnlessEqual(self.output, '\xa0\xc2\xa0')

    def testChangeOutputEncodingBufferFlushing(self):
        buf = self.getRequestBuffer('latin1')
        buf.push_buffer()
        buf.write(unicode('\xa0', 'latin1'))
        self.failUnlessEqual(self.output, '')

        cbuf = util.StringIO()
        buf.push_capture_buffer(cbuf)
        buf.push_buffer()
        buf.write('foo')
        
        buf.set_encoding('utf-8')
        self.failUnlessEqual(buf.encoding, 'utf-8')

        # Test that nothing is flushed.
        self.failUnlessEqual(cbuf.getvalue(), '')
        self.failUnlessEqual(self.output, '')

        buf.pop_buffer()
        buf.pop_capture_buffer()
        
        buf.write(unicode(' \xa0', 'latin1'))
        buf.pop_buffer()
        self.failUnlessEqual(self.output, '\xc2\xa0 \xc2\xa0')

    def testReplaceErrors(self):
        buf = self.getRequestBuffer(errors='replace')
        buf.push_filter(test_filter)
        state = buf.get_state()
        buf.push_buffer()
        buf.write(REPLACEMENT_CHARACTER)
        self.failUnlessEqual(self.output, '')
        buf.pop_to_state(state)
        self.failUnlessEqual(self.output, 'f(?)')
        buf.write(u'a')
        self.failUnlessEqual(self.output, 'f(?)f(a)')
        
    def testFlushWithErrors(self):
        buf = self.getRequestBuffer()
        buf.push_buffer()
        buf.write(unicode('\xa4', 'latin1'))
        self.failUnlessRaises(UnicodeEncodeError, buf.pop_buffer)
        self.failUnlessEqual(self.output, '')
    
    
################################################################

class TestIsAsciiSuperset(unittest.TestCase):
    def test(self):
        self.failUnless(_is_ascii_superset('latin1'))
        self.failUnless(_is_ascii_superset('ascii'))
        self.failUnless(_is_ascii_superset('utf8'))
        self.failIf(_is_ascii_superset('utf7'))
        

        
if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2, descriptions=False)
    unittest.main(testRunner=runner)
