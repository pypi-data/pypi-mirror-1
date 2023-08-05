# encoding: ascii
# component_recoding.py
"""Test handling of components of mixed character encodings.

Also test unicode output from components.
"""
import re, unittest
import testbase
from myghty import escapes

class ComponentRecodingTests(testbase.ComponentTester):
    config = dict(output_encoding="utf_8")
    
    srcFiles = { 'simple.myt':
                 '''# -*- coding: iso-8859-15 -*-
                 <%flags>trim = "both"</%flags>

                 Howdy\xa0there
                 '''
                 }

    def testSimple(self):
        self.runComponent('/simple.myt')
        self.failUnlessEqual(self.output, 'Howdy\xc2\xa0there')

    def testFilter(self):
        """Test that output gets it output all in one whack
        """
        self.runComponent('''# -*- coding: latin1 -*-
            <%flags>
                trim = "both"
            </%flags>
            <%filter>
                return "f(%s)" % f
            </%filter>
            Pre<& /simple.myt &>Post
            ''')
        self.failUnlessEqual(self.output, 'f(PreHowdy\xc2\xa0therePost)')

    def testAutoFlush(self):
        self.runComponent('''
            <%flags>
                autoflush = True
            </%flags>
            Pre
            % m.write(m.request_impl.out_buffer.getvalue())
            Post
            ''')
        self.failUnlessEqual(self.tidyoutput, 'Pre Pre Post')

    def testEncodingError(self):
        self.failUnlessRaisesWrappedError(
            UnicodeEncodeError, self.runComponent, '/simple.myt',
            config={'output_encoding': 'ascii'})
        self.failUnlessEqual(self.output, '')

        self.runComponent('/simple.myt',
                          config={'output_encoding': 'ascii',
                                  'encoding_errors': 'xmlcharrefreplace'})
        self.failUnlessEqual(self.output, 'Howdy&#160;there')

    def testDecodingError(self):
        comp = '''# encoding: ascii
            %m.write("\\xa0")
            '''
        self.failUnlessRaisesWrappedError(UnicodeDecodeError,
                                          self.runComponent, comp)
        self.failUnlessEqual(self.output, '')

    def testValidCharset(self):
        self.failUnlessRaisesWrappedError(
            UnicodeDecodeError,
            self.runComponent,
            '''# encoding: ascii
            % m.write("\\xa0")
            ''',
            config=dict(output_encoding="ascii"))
    

    def testSetOutputEncoding(self):
        self.runComponent("""% m.write(u'\\xa0')
                             % m.set_output_encoding('utf8')
                             % m.write(u'\\xa0')
                             % m.set_output_encoding('ascii', 'replace')
                             % m.write(u'\\xa0')
                             """,
                          config=dict(output_encoding='latin1',
                                      auto_flush=True))
        self.failUnlessEqual(self.output, "\xa0\xc2\xa0?")
            
################################################################
#
# Test various sorts of encoding/decoding errors
#
################################################################



class EncodingErrorsTests(testbase.ComponentTester):
    config = dict(output_encoding="latin1")

    srcFiles = { 'htdocs/badencoding.myt':
                 '''# encoding: ascii
                 % m.write("\\xa0")
                 '''
                 }

    def testDecodeError(self):
        self.failUnlessRaisesWrappedError(
            UnicodeDecodeError,
            self.runComponent, "/badencoding.myt")
        self.failUnlessEqual(self.output, '')

    def testBadSyntax(self):
        # The compiled component contains non-ascii characters,
        # thought the encoding is declared to be ASCII.
        # The Python compiler generates a SyntaxError.
        self.failUnlessRaises(
            SyntaxError,
            self.loadComponent,
            '''# encoding: ascii
            \xa0
            ''')

    srcFiles['badchar.myt'] = (
        '# encoding: ascii\n'
        '% m.write(u"howdy\u20ac")\n') # EURO SIGN - not encodable to latin1

    def testEncodeError(self):
        self.failUnlessRaisesWrappedError(
            UnicodeEncodeError,
            self.runComponent, "/badchar.myt")
        self.failUnlessEqual(self.output, '')

    def testEncodeErrorIgnore(self):
        self.runComponent("/badchar.myt",
                          config={'encoding_errors': 'ignore'})
        self.failUnlessEqual(self.tidyoutput, 'howdy')

    def testEncodeErrorReplace(self):
        self.runComponent("/badchar.myt",
                          config={'encoding_errors': 'replace'})
        self.failUnlessEqual(self.tidyoutput, 'howdy?')

    def testEncodeErrorXmlCharrefReplace(self):
        self.runComponent("/badchar.myt",
                          config={'encoding_errors': 'xmlcharrefreplace'})
        self.failUnlessEqual(self.tidyoutput, 'howdy&#%d;' % 0x20ac)

    def testEncodeErrorHtmlEntityReplace(self):
        self.runComponent("/badchar.myt",
                          config={'encoding_errors': 'htmlentityreplace'})
        self.failUnlessEqual(self.tidyoutput, 'howdy&euro;')

################################################################
#
# Tests that filters get either ASCII strs or unicodes.
# and that they can return any type acceptable to m.write()
#
################################################################

class FilterTests(testbase.ComponentTester):

    config = dict(output_encoding="latin1")
    
    filter_myt = '''# encoding: latin1
        <%args> greeting = "howdy" </%args>
        <%flags> trim = "both" </%flags>
        <%filter> return "f(%s)" % repr(f) </%filter>
        <% greeting %>
        '''

    def testFilterGetsUnicodeEvenIfInputIsAscii(self):
        self.runComponent(self.filter_myt)
        self.failUnlessEqual(self.output, "f(u'howdy')")

    def testFilterGetsUnicode(self):
        # write a non-ascii string, filter should get a unicode
        self.runComponent(self.filter_myt, greeting=u'foo\u20ac')
        self.failUnlessEqual(self.output, "f(u'foo\u20ac')")


class UnicodeOutputFilterTests(FilterTests):
    filter_myt='''# encoding: latin1
        <%args> greeting = "howdy" </%args>
        <%flags> trim = "both" </%flags>
        <%filter> return u"f(%s)" % repr(f) </%filter>
        <% greeting %>
        '''
    
class ObjectOutputFilterTests(FilterTests):
    filter_myt='''# encoding: latin1
        <%args> greeting = "howdy" </%args>
        <%flags> trim = "both" </%flags>
        <%filter>
            class Retval:
                def __init__(self, val):
                    self.val = val
                def __unicode__(self):
                    return unicode(self.val)
            return Retval("f(%s)" % repr(f))
        </%filter>
        <% greeting %>
        '''


class ObjectOutputFilterTests2(FilterTests):
    filter_myt='''# encoding: latin1
        <%args> greeting = "howdy" </%args>
        <%flags> trim = "both" </%flags>
        <%filter>
            class Retval:
                def __init__(self, val):
                    self.val = val
                def __str__(self):
                    return str(self.val)
            return Retval("f(%s)" % repr(f))
        </%filter>
        <% greeting %>
        '''
    
################################################################
#
# Test capture buffers get the right values (either strs
# or unicodes.)
#
################################################################

class TestBuffer(object):
    def __init__(self):
        self.buf = []
    def write(self, text):
        self.buf.append(text)

class CaptureBufferTests(testbase.ComponentTester):

    config = dict(output_encoding='latin1')

    srcFiles = {
        'ascii.myt':   'hello',
        'unicode.myt': r'%m.write(u"\u20ac")',

        'latin1.myt': '''# encoding: latin1
                         hi\xa0there
                         ''',
        }

    def testCapture(self, bufencoding=None):
        buf = TestBuffer()
        if bufencoding:
            buf.encoding = bufencoding
        
        def mycomp(m):
            m.execute_component("/ascii.myt", store=buf)
            m.execute_component("/latin1.myt", store=buf)
            m.execute_component("/unicode.myt", store=buf)
        comp = self.makeModuleComponent(mycomp)

        self.runComponent(comp)

        self.failUnlessEqual(self.output, "")
        expected = [u'hello', u'hi\u00a0there', u'\u20ac']
        self.failUnlessEqual(buf.buf, expected)
        self.failUnlessEqual(map(type, buf.buf), map(type, expected))

    def testCaptureIgnoresAsciiBufferEncodingAttribute(self):
        self.testCapture(bufencoding='ascii')

    def testScomp(self, comp="/ascii.myt", expect=u'hello'):
        result = self.runComponent('''# encoding: utf8
            <%args> comp </%args>
            % return m.scomp(comp)
            ''', comp=comp)
        self.failUnlessEqual(self.output, "")
        self.failUnlessEqual(result, expect)
        self.failUnlessEqual(type(result), type(expect))

    def testScompLatin1(self):
        self.testScomp(comp='/latin1.myt', expect=u'hi\xa0there')

    def testScompUnicode(self):
        self.testScomp(comp='/unicode.myt', expect=u'\u20ac')
        
################################################################
#
# Test closures
#
################################################################


class ClosureTests(testbase.ComponentTester):

    config = dict(output_encoding='utf8')

    def testClosure(self):
        self.runComponent('''# encoding: latin1
            <%closure show_foo>
                <% foo %>
            </%closure>
            % foo = "foo1"
            <& show_foo &>
            % foo = "\xa0foo2".decode("latin1")
            <& show_foo &>
            ''')
        self.failUnlessEqual(self.tidyoutput, "foo1 \xc2\xa0foo2")

    def testClosureWithContent(self):
        self.runComponent('''# encoding: ascii
            <%closure double>
            % for i in 1, 2:
                <% m.content(i=i) %>
            % # end
            </%closure>
            <&| double &>
                cow<% u"\u20ac" %><% m.content_args["i"] %>
            </&>
            ''')
        self.failUnlessEqual(self.tidyoutput,
                             "cow\xe2\x82\xac1 cow\xe2\x82\xac2")

################################################################
#
# Output escaping.
#
################################################################

class OutputEscapingTest(testbase.ComponentTester):
    config = dict(escapes={'H': escapes.html_entities_escape})

    def do_test(self, escape, expected):
        self.runComponent('''
            <%% u"\\u20ac" | %(escape)s %%>
            <%% "\'" | %(escape)s %%>
            ''' % dict(escape=escape),
            config={'encoding_errors': 'backslashreplace'})
        
        self.failUnlessEqual(self.tidyoutput, expected)

    def test_h(self):
        self.do_test('h', r"\u20ac '")
    def test_u(self):
        self.do_test('u', r"%E2%82%AC %27")
    def test_x(self):
        #self.do_test('x', r"\u20ac &apos;")
        self.do_test('x', r"\u20ac &#39;")
    def test_H(self):
        self.do_test('H', r"&euro; '")

################################################################
#
# Test aborting
#
################################################################

class AbortTest(testbase.ComponentTester):
    def testAbort(self):
        self.runComponent(r'''
            <%flags> autoflush = True </%flags>

            <%def subcomp>
              <%flags> autoflush = False </%flags>
              output
            % m.flush_buffer()
              a mistake
            % m.abort()
            </%def>

            head
            <& subcomp &>
            tail
            ''')
        self.failUnlessEqual(self.tidyoutput, 'head output')

    def testFail(self):
        class MyAbort(Exception): pass
        
        from myghty.request import DefaultRequestImpl
        class MyRequestImpl(DefaultRequestImpl):
            def send_abort(self, code, reason):
                assert code == 404
                assert reason == "not found"
                raise MyAbort(code, reason)
        
        request_impl=MyRequestImpl(out_buffer=self.outputBuffer)

        self.failUnlessRaises(
            MyAbort,
            self.runComponent,
            '''
            head
            % m.flush_buffer()
            body
            % m.abort(404, "not found")
            tail
            ''',
            config=dict(request_impl=request_impl))
        
        self.failUnlessEqual(self.tidyoutput, "head")

################################################################
#
# Test m.send_redirect()
#
################################################################

class RedirectTest(testbase.ComponentTester):

    srcFiles = { 'comp2.myt': """Comp2 here.""" }
    
    def testSoftRedirect(self):
        self.runComponent(r'''
            <%flags> autoflush = False </%flags>
            Leading junk (should be discarded)
            % m.send_redirect("/comp2.myt", hard=False)
            Trailing junk (should be disregarded)
            ''')
        self.failUnlessEqual(self.tidyoutput, 'Comp2 here.')

    def testHardRedirect(self):
        class MyRedirect(Exception): pass
        
        from myghty.request import DefaultRequestImpl
        class MyRequestImpl(DefaultRequestImpl):
            def send_redirect(self, path):
                assert path == '/other.html'
                raise MyRedirect(path)
        
        request_impl=MyRequestImpl(out_buffer=self.outputBuffer)

        self.failUnlessRaises(
            MyRedirect,
            self.runComponent,
            '''
            head
            % m.send_redirect("/other.html")
            tail
            ''',
            config=dict(request_impl=request_impl))
        
        self.failUnlessEqual(self.tidyoutput, "")

################################################################
#
# Test that cache_self output is stored in encoding neutral manner
#
################################################################

class CacheSelfTests(testbase.ComponentTester):

    config = dict(output_encoding='ascii')
    
    srcFiles = {'htdocs/cache_money.myt':
                '''# encoding: latin1
                <%flags> use_cache = True </%flags>
                # A random number of EUROs, with a decoding error
                % import random
                <% u"\\xa4" %><% str(random.randint(1,1000)) %>
                '''
                }

    setup_done = False
    
    def class_set_up(self):
        if not self.setup_done:
            testbase.ComponentTester.class_set_up(self)
            self.setUp()
            self.runComponent('<& cache_money.myt &>',
                              config=dict(encoding_errors='replace'))
            self.__class__.euros = int(re.search(r'\d+', self.output).group())
            self.tearDown()
            self.__class__.setup_done = True
        
    def testLenient(self):
        self.runComponent('<& cache_money.myt &>',
                          config=dict(encoding_errors='replace'))
        self.failUnlessEqual(self.tidyoutput, '?%d' % self.euros)

    def testStrict(self):
        self.failUnlessRaisesWrappedError(
            UnicodeEncodeError,
            self.runComponent, '<& cache_money.myt &>',
            config=dict(encoding_errors='strict'))
                                           
################################################################
#
# Test that trimming filter works with either unicode or str input
#
################################################################

class TrimTests(testbase.ComponentTester):

    config = dict(output_encoding='utf8')
    
    def testStrStrip(self):
        self.runComponent(
            '''# encoding: ascii
            <%flags> trim = "both" </%flags>
            foo
            ''')
        self.failUnlessEqual(self.output, 'foo')
        self.failUnlessEqual(type(self.output), str)

    def testUnicodeStrip(self):
        self.runComponent(
            '''# encoding: latin1
            <%flags> trim = "both" </%flags>
            \xa0 bar
            % m.write(u"\\u20ac")
            ''')
        self.failUnlessEqual(self.output, 'bar\n\xe2\x82\xac')

################################################################
#
# Test captured subrequest can have their own output_encoding
#
################################################################

class SubrequestTest(testbase.ComponentTester):

    config = dict(output_encoding='utf-8')

    srcFiles = {'htdocs/subreqbody.myt': r'% m.write(u"\u20ac")'}
    
    def testCanSetOutputEncoding(self):
        import StringIO
        buf = StringIO.StringIO()
        self.runComponent(
            '''# encoding: ascii
            <%args> buf </%args>
            <%init>
                subreq = m.create_subrequest("subreqbody.myt",
                                             out_buffer=buf,
                                             output_encoding="iso-8859-15")
                subreq.execute()                             
            </%init>
            ''',
            buf = buf)
        self.failUnlessEqual(buf.getvalue(), "\xa4")
        self.failUnlessEqual(self.output, '')

    def testCurrentEncoding(self):
        # If not output_encoding is specified for capture buffer, it should
        # default to the current value of m.encoding (not m.output_encoding).
        self.failUnlessRaisesWrappedError(
            UnicodeEncodeError,
            self.runComponent,
            '''# encoding: ascii
            <%init>
                import StringIO
                subreq = m.create_subrequest("subreqbody.myt",
                out_buffer=StringIO.StringIO())
                subreq.execute()                             
            </%init>
            ''')

        
    
if __name__ == '__main__':
    unittest.main()
