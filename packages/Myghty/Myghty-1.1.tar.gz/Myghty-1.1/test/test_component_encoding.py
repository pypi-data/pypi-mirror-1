# test/component_encoding.py
"""Test that component's encodings are determined correctly.
"""
import unittest, os, shutil, sys, warnings, random, StringIO, time, codecs, re

import testbase
from myghty.interp import Interpreter
from myghty.resolver import NotFound
from myghty import importer, exception

some_encodings = """ascii
                    big5 big5hkscs
                    cp037 cp424 cp437 cp500 cp737 cp775 cp850
                    cp852 cp855 cp856 cp857 cp860 cp861 cp862
                    cp863 cp864 cp865 cp866 cp869 cp874 cp875
                    cp932 cp949 cp950 cp1006 cp1026 cp1140 cp1250
                    cp1251 cp1252 cp1253 cp1254 cp1255 cp1256 cp1257 cp1258
                    euc_jp euc_jis_2004 euc_jisx0213 euc_kr
                    gb2312 gbk gb18030 hz
                    iso2022_jp iso2022_jp_1 iso2022_jp_2 iso2022_jp_2004
                    iso2022_jp_3 iso2022_jp_ext
                    iso2022_kr
                    latin_1
                    iso8859_2 iso8859_3 iso8859_4 iso8859_5 iso8859_6
                    iso8859_7 iso8859_8 iso8859_9 iso8859_10 iso8859_13
                    iso8859_14 iso8859_15
                    johab
                    koi8_r koi8_u
                    mac_cyrillic mac_greek mac_iceland
                    mac_latin2 mac_roman mac_turkish
                    ptcp154
                    shift_jis shift_jis_2004 shift_jisx0213
                    utf_16 utf_16_be utf_16_le utf_7""".split()

def isAsciiSuperset(encoding):
    ascii_chars = ''.join(map(chr, range(0x80)))
    try:
        return ascii_chars.decode(encoding) == ascii_chars.decode('ascii')
    except (ValueError, LookupError):
        return False

some_encodings = [ enc for enc in some_encodings
                   if isAsciiSuperset(enc) and enc != sys.getdefaultencoding()
                   ]
random.shuffle(some_encodings)

def random_encoding():
    enc = some_encodings.pop()
    some_encodings.insert(0, enc)
    return enc

def parse_magic_comment(text):
    m = re.match(r'(?:#.*\n)?#.*coding[:=][ \t]*([-\w.]+)', text)
    if m:
        return m.group(1)
    return None
        
def resetwarnings():
    warnings.resetwarnings()
    try:
        import myghty.compiler
        del myghty.compiler.__warningregistry__
    except AttributeError:
        pass

        
class FileComponentEncodingTests(testbase.ComponentTester):
        
    def getComponent(self, head=""):
        return self.makeFileBasedComponent(head + "\nbody\n")

        
    def getCompiled(self, head=""):
        """Get the python source for the compiled component.
        """
        return self._getCompiledFromComp(self.getComponent(head))

    def _getCompiledFromComp(self, comp):
        return file(comp.component_source.module.__file__).read()
        
    def failUnlessComponentEncodingEqual(self, comp, encoding):
        #self.failUnlessEqual(comp.component_source.module._ENCODING,
        #                     Encoding(encoding))
        compiled = self._getCompiledFromComp(comp)
        enc = parse_magic_comment(compiled) or sys.getdefaultencoding()
        self.failUnlessEqual(enc, encoding)
        self.failUnlessEqual(codecs.lookup(enc), codecs.lookup(encoding))


    def testSystemDefaultEncoding(self):
        """Test that component get system default encoding when appropriate.
        """
        comp = self.getComponent()
        self.failUnlessComponentEncodingEqual(comp, sys.getdefaultencoding())

    def testExplicitEncoding(self):
        """Test that component gets encoding from magic comment.
        """
        enc = random_encoding()
        comp = self.getComponent(head = "# encoding: %s\n" % enc)
        self.failUnlessComponentEncodingEqual(comp, enc)

    def testEncodingFromBOM(self):
        """Test that UTF-8 BOM results in utf-8 encoding
        """
        comp = self.getComponent(head = codecs.BOM_UTF8)
        self.failUnlessComponentEncodingEqual(comp, 'utf_8')

    def testBadEncodingFromBOM(self):
        """Test that UTF-8 BOM results in utf-8 encoding
        """
        expected = (SyntaxError,        # For bad module source
                    exception.Syntax,   # For bad file component source
                    exception.ConfigurationError # XXX: Bad module root?
                    )
        self.failUnlessRaises(expected,
                              self.getComponent,
                              head = codecs.BOM_UTF8 + "# encoding: ascii\n"
                              )

    def testEncodingFromFlagsEncoding(self):
        """Test that ``<%flags> encoding`` still works.
        """
        warnings.filterwarnings("ignore",
                                category=DeprecationWarning,
                                module=r'myghty\.compiler')
        enc = random_encoding()
        comp = self.getComponent("<%%flags> encoding = %s </%%flags>\n"
                                 % repr(enc))
        self.failUnlessComponentEncodingEqual(comp, enc)

    def x_testFlagsEncodingWarning(self):
        """Test that ``<%flags> encoding`` results in a warning.
        """
        resetwarnings()
        warnings.filterwarnings("error",
                                category=DeprecationWarning,
                                module=r'myghty\.compiler')
        self.failUnlessRaises(DeprecationWarning,
                              self.getComponent,
                              "<%flags> encoding='ascii' </%flags>\n")
        
    def testMagicCommentAndFlagsEncodingIsError(self):
        """Specifying a magic comment and an encoding flag is an error.

        Test that specifying a magic comment and a ``<%flags> encoding``
        is an error.
        """
        warnings.filterwarnings("ignore",
                                category=DeprecationWarning,
                                module=r'myghty\.compiler')
        self.failUnlessRaises(exception.Syntax,
                              self.getComponent,
                              head="# encoding: latin1\n"
                              "<%flags> encoding='ascii' </%flags>\n")

    def testMagicCommentInCompiledComponent(self):
        """Test that the magic comment get generated in compiled code.
        """
        encoding = random_encoding()
        compiled = self.getCompiled("# -*- encoding: %s -*-\n" % encoding)
        self.failUnlessEqual(parse_magic_comment(compiled), encoding)

    def testNoMagicCommentInCompiledComponent(self):
        """Test that the magic comment doesn't get generated if there's
        no magic comment in the source file.
        """
        compiled = self.getCompiled()
        self.failUnlessEqual(parse_magic_comment(compiled), None)


class MemoryComponentEncodingTests(FileComponentEncodingTests):

    def getComponent(self, head=""):
        return self.makeMemoryComponent(head + "\nbody\n")

    def _getCompiledFromComp(self, comp):
        buf = StringIO.StringIO()
        comp.component_source.get_object_code(self.interpreter.compiler.get(),
                                              buf)
        return buf.getvalue()

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2, descriptions=False)
    unittest.main(testRunner=runner)
