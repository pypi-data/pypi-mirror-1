from myghty import interp
import re, sys, StringIO, unittest

def runComponent(componentSrc, **config):
    interpreter = interp.Interpreter(**config)
    comp = interpreter.make_component(componentSrc)
    buf = StringIO.StringIO()
    interpreter.execute(comp, out_buffer=buf)
    return buf.getvalue()


# A component with "stacked filters"
# Any of the output from subcomponent "a", should be passed
# through a\'s filter, and then the main components filter.
stackedFilterSrc='''
<&a&>
<%filter>
 return "filter(%s)" % f
</%filter>
<%def a>
 hello
 <%filter>
   return "a(%s)" % f
 </%filter>
</%def>
'''
# The resulting output should contain a string
# something like "filter(a(" which indicates that the
# main filter has been applied to the output of the subcomponents
# filter.
stackedFilterCheck="filter(a("


class FilterTests(unittest.TestCase):
    """Test that two stacked filters get properly called.
    """
    auto_flush = False
    
    def testStackedFilters(self):
        output = runComponent(stackedFilterSrc,
                              auto_flush=self.auto_flush)
        output = re.sub(r'\s', '', output)
        self.failUnless(stackedFilterCheck in output,
                        "output %s does not contain %s"
                        % (repr(output), repr(stackedFilterCheck)))
                                                           

class AutoFlushFilterTests(FilterTests):
    auto_flush = True

if __name__ == '__main__':
    unittest.main()
