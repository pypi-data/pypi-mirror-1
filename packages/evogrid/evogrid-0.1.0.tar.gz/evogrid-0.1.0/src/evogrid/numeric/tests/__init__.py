"""Test the readme file"""

import unittest
from evogrid.numeric.tests import test_readme
from evogrid.numeric.tests import test_dejong
from evogrid.numeric.tests import test_variators

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(test_readme.test_suite())
    suite.addTests(test_dejong.test_suite())
    suite.addTests(test_variators.test_suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
