"""Test suite for the ``caching`` package
"""

import unittest
from zope.testing import doctest

from evogrid.testing import OPTIONS

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocFileSuite('README.txt', optionflags=OPTIONS))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
