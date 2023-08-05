import myghty.interp as interp
import myghty.buffer as buffer
import myghty.exception as exception
import os, sys, gc, random, StringIO, time, thread, traceback
import testbase
import unittest


use_static_source = False

try:
    import threadframe
    has_threadframe = True
except:
    has_threadframe = False

# creates file based components with unique names, executes them, then deletes them.
# watch the memory usage to see if it creeps up.  with the 
# advent of the FileComponent __del__ method 
# cleaning its module from sys.modules, it should stay constant.  


threadcount = 0
gtime = time.time()
ccount = 240

use_files = True

def doit(i, regen):
    filename = "comp%s.myt" % i

    resolution = interpreter.resolve_component(filename)
    csource = resolution.csource
    
    if (regen > 6):
        # force a reload now and then
        csource.last_modified = time.time()
        pass
        
    comp = interpreter.load_component(csource)
    outbuf = StringIO.StringIO()
    m = interpreter.make_request(comp, out_buffer = outbuf)

    interpreter.debug("Executing.... %s id %d num elements in cache is %d  sys.modules size is %d " % (
        filename,
        id(comp),
        len(interpreter.code_cache.dict),
        len(sys.modules)
    ))
    m.execute()
    interpreter.debug("Done executing %s" % filename)

    comp = None
        


def do_test():
    global threadcount
    global gtime
    
    threadcount += 1
    # now randomly recreate files and execute the components in them
    try:
        for i in range(1,1000):
            doit(random.randint(1, ccount), random.randint(1,8))
            gtime = time.time()
            time.sleep(.000005)

    except exception.Error, e:
        print "thread id %s" % thread.get_ident()
        e.initTraceback(interpreter)
        print e.textformat()
    except Exception, e2:
        import traceback
        traceback.print_exc(file=sys.stdout)

    print "THREAD EXITING !!!! threadcount is %d" % threadcount
    threadcount -= 1


    
class TestMemUsage(testbase.MyghtyTest):
    def setUp(self):
        # now make (ccount) myghty files
        for i in range(1,ccount + 1):
            self.makefile(i)

        print "created %d files" % ccount
        
        # make an interpreter, with a really freekin small cache
        global interpreter
        if use_files:
            data_dir = self.cache
        else:
            data_dir = None

        interpreter = interp.Interpreter(delete_modules = True, component_root = self.htdocs, data_dir=data_dir, code_cache_size=5000, raise_error = True, debug_file=buffer.LinePrinter(sys.stdout), debug_threads = True, debug_elements=['codecache'], use_static_source = use_static_source)



    def makefile(self, i):
        filename = "comp%s.myt" % i
        c = """
    <%global>
        import os
    </%global>
        i am component #%s\n" % i
        
        # this kind of call breaks if sys.modules isnt populated with
        # this component's module
        os info is: <% os.getcwd() %>
    """
        self.create_file(self.htdocs, filename, c)

    def delete(self, i):    
        filename = "comp%s.myt" % i
    
        resolution = interpreter.resolve_component(filename)
        csource = resolution.csource
        if use_files:
            object_files = \
                    interpreter.get_component_object_files(csource)
    
            #print "deleting %s, %s" % (filename, repr(object_files))
            for f in object_files:
                try:
                    os.unlink(f)
                except OSError, e:
                    # (SIC): print this?  ignore this?
                    "Error deleting %s, probably never called" % f
    
        self.remove_file(self.htdocs, filename)        

    def testmemory(self):
	print "starting memory test"

        # now..threads !
        for t in range(1, 10):
            thread.start_new_thread(do_test, ())

        time.sleep(5)
        while threadcount > 0:
            time.sleep(1)    
            if time.time() - gtime > 10:
                print "deadlock !"
                if has_threadframe:
                    frames = threadframe.dict()
                    for thread_id, frame in frames.iteritems():
                        print '-' * 72
                        print '[%s] %d' % (thread_id, sys.getrefcount(frame))
                        traceback.print_stack(frame)    
                sys.exit(-1)
        # look for garbage
        gc.collect()
        print repr(gc.garbage)


    def tearDown(self):
        for i in range(1, ccount):
            self.delete(i)
        print "deleted %d files" % ccount
    
    
if __name__ == "__main__":
    testbase.runTests(unittest.findTestCases(__import__('__main__')))        
    
