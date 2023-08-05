"""Test suite for the ``numeric`` package"""

import unittest
from zope.testing import doctest
import os

from evogrid.testing import OPTIONS

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocFileSuite(os.path.join('..', 'README.txt'),
                                        optionflags=OPTIONS))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
