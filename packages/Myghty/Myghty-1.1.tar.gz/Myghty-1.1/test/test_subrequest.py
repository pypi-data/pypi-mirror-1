# subrequest.py
"""Test subrequests
"""
import StringIO, unittest
from myghty import interp, request
import testbase

class SubrequestTests(testbase.ComponentTester):
    srcFiles = { 'subreq.myt': 'Howdy'
                 }

    def testCapture(self):
        self.runComponent('''
            <%flags> trim = "both" </%flags>
            <%python>
                import StringIO
                buf = StringIO.StringIO()
                subreq = m.create_subrequest("/subreq.myt", out_buffer=buf,
                                             request_args={})
                subreq.execute()
            </%python>
            Subrequest said: "<% buf.getvalue() %>"
            ''')
        self.failUnlessEqual(self.output, 'Subrequest said: "Howdy"')

    def testNoCapture(self):
        self.runComponent('''
            <%flags> trim = "both" </%flags>
            Subrequest said: "<% m.subexec("subreq.myt") or '' %>"
            ''')
        self.failUnlessEqual(self.output, 'Subrequest said: "Howdy"')

    def testSubreq(self):
        self.runComponent("/subreq.myt")
        self.failUnlessEqual(self.output, 'Howdy')

    def testNoFlushOnAbort(self):
        self.runComponent('''
            <%flags> trim = "both" </%flags>
            % m.subexec("subreq.myt")
            % m.abort()
            ''')
        self.failUnlessEqual(self.output, '')

    def testAutoFlush(self):
        self.runComponent('''#
            <%flags>
                autoflush = True
            </%flags>
            % m.subexec("subreq.myt")
            % m.abort()
            ''')
        self.failUnlessEqual(self.output, 'Howdy')
            
    def testDefaultOutputEncoding(self):
        encoding, subreq_encoding = self.runComponent('''
            <%flags> trim = "both" </%flags>
            <%python>
                import StringIO
                buf = StringIO.StringIO()
                subreq = m.create_subrequest("/subreq.myt", out_buffer=buf,
                                             request_args={})
                return ( (m.output_encoding, m.encoding_errors),
                         (subreq.output_encoding, subreq.encoding_errors) )
            </%python>
            ''',
            config={'output_encoding': 'iso-8859-15',
                    'encoding_errors': 'ignore'})
        self.failUnlessEqual(subreq_encoding,
                             (request.DEFAULT_OUTPUT_ENCODING,
                              request.DEFAULT_ENCODING_ERRORS))
        self.failIfEqual(encoding,
                         (request.DEFAULT_OUTPUT_ENCODING,
                          request.DEFAULT_ENCODING_ERRORS))

if __name__ == '__main__':
    unittest.main()
