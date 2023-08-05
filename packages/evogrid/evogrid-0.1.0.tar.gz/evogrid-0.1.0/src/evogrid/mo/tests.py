"""Test suite for the ``mo`` package
"""

import unittest
from zope.testing import doctest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocFileSuite('README.txt'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
