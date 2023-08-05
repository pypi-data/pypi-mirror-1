import unittest
import testbase

def suite():
    modules_to_test = ('resolver', 'component',
                       'LRUCache', 'Container', 'MemUsage',
                       'component_reloading', 'cache_self') # and so on
    alltests = unittest.TestSuite()
    for module in map(__import__, modules_to_test):
        alltests.addTest(unittest.findTestCases(module))
    return alltests

if __name__ == '__main__':
    testbase.runTests(suite())
