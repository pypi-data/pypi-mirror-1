#!/usr/bin/env python
"""Tests are preferably written as doctests (runnable documentation) that
explain the API and the component architecture through pedagogical scenarii
"""

import unittest

from evogrid.common import tests as common_tests
from evogrid.numeric import tests as numeric_tests
from evogrid.mo import tests as mo_tests
from evogrid.sharing import tests as sharing_tests
from evogrid.caching import tests as caching_tests

def test_suite():
    """Avoid the zope.testing testrunner run the tests twice"""
    return unittest.TestSuite()

def evogrid_test_suite():
    """Global test suite for the project"""
    suite = unittest.TestSuite()
    suite.addTests(common_tests.test_suite())
    suite.addTests(numeric_tests.test_suite())
    suite.addTests(sharing_tests.test_suite())
    suite.addTests(caching_tests.test_suite())
    suite.addTests(mo_tests.test_suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='evogrid_test_suite')
