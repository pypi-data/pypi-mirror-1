from zope.testing import doctest
import os.path
import unittest

from evogrid.testing import OPTIONS

FILES = (
    os.path.join('..', 'README.txt'),
    'test_checkpointers.txt',
    'test_elite_archive.txt',
    'test_evolvers.txt',
    'test_replicators.txt',
)

def test_suite():
    suite = unittest.TestSuite()
    for filename in FILES:
        suite.addTests(doctest.DocFileSuite(filename, optionflags=OPTIONS))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

