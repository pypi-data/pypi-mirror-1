# python import
import unittest

# tools import
from sphinx.webtools.tests import test_pickler_tools, test_search_tools

def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_pickler_tools.suite())
    suite.addTest(test_search_tools.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
