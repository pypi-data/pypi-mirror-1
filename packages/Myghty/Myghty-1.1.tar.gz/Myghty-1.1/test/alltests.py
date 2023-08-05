import unittest, os
import testbase

def suite():
    modules_to_test = tuple(
        [ name
          for name, ext in map(os.path.splitext,
                               os.listdir(os.path.dirname(__file__)))
          if ext == '.py' and name.startswith('test_') ])
           
    alltests = unittest.TestSuite()
    for module in map(__import__, modules_to_test):
        alltests.addTest(unittest.findTestCases(module))
    return alltests

if __name__ == '__main__':
    testbase.runTests(suite())
