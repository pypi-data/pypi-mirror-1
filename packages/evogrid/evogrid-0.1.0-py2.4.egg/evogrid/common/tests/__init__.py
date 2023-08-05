"""Test suite for the `common` package"""

import unittest

import test_doctests
import test_comparators
import test_pools
import test_replacers
import test_selectors
import test_variators

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(test_doctests.test_suite())
    suite.addTests(test_comparators.test_suite())
    suite.addTests(test_pools.test_suite())
    suite.addTests(test_replacers.test_suite())
    suite.addTests(test_selectors.test_suite())
    suite.addTests(test_variators.test_suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
