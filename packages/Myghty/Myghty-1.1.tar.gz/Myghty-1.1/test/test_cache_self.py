# test/cache_self.py
"""Tests for m.cache_self
"""
import unittest, os, shutil, stat, sys, time, warnings

import testbase
from test_component_reloading import ComponentReloadTests, purge_module

    
class CacheSelfTests(ComponentReloadTests):
    """Abstract base class of tests for component reloading."""

    def setUp(self):
        # Blow away cache
        shutil.rmtree(os.path.join(self.cache, 'container_dbm'),
                      ignore_errors=True)
        #time.sleep(1)
        ComponentReloadTests.setUp(self)

    def reinitializeInterpreter(self):
        params = self.resolverArgs()
        self.module_runner = self.module_runner_class(data_dir=self.cache,
                                                      **params)
        
    def testComponent(self, text="howdy"):
        """Test that we can resolve and execute our component.
        """
        self.failUnlessEqual(self.executeComponent().strip(), text)

    def testCache(self):
        """Test that cache remains intact across interpreter incarnations.
        """
        self.testComponent()
        time.sleep(1)
        self.changeComponentSource(text="changed")

        # Create a new myghty interpreter
        self.reinitializeInterpreter()

        # We should still see the cached value, not the changed value
        self.testComponent()

    def testStaleCache(self):
        """Test that cache gets invalidated if the component source changes.
        """
        #os.system("ls -lR " + self.cache)
        self.testComponent()
        time.sleep(1)
        self.createComponentSource(text="changed")

        # Create a new myghty interpreter
        self.reinitializeInterpreter()
        self.testComponent("changed")

        

################################################################
#
# (The actual unittest.TestCase sub-classes begin here.)
#
################################################################


class FileComponentTests(CacheSelfTests, testbase.MyghtyTest):
    
    def srcFile(self):
        return os.path.join(self.htdocs, "comp.myt")

    def srcText(self, text="howdy"):
        return """
<%%init>
if m.cache_self():
    return
</%%init>
%s
""" % text

    def resolverArgs(self):
        return {'component_root': self.htdocs}

    def componentPath(self):
        return "/comp.myt"
    
class ModuleComponentTests(CacheSelfTests, testbase.MyghtyTest):
    def setUp(self):
        purge_module('module')
        CacheSelfTests.setUp(self)

    def reinitializeInterpreter(self):
        purge_module('module')
        CacheSelfTests.reinitializeInterpreter(self)
        
    def srcFile(self):
        return os.path.join(self.lib, "module.py")

    def srcText(self, text="howdy"):
        return """
def comp(m):
    if not m.cache_self():
        m.write('%s')""" % text

    def resolverArgs(self):
        try:
            del sys.modules['module']
        except KeyError:
            pass
        return {'module_components': [{'/mycomp': 'module:comp'}]}
    
    def componentPath(self):
        return "/mycomp"


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2, descriptions=False)
    unittest.main(testRunner=runner)
