import unittest

from zope.interface.verify import verifyClass, verifyObject

from evogrid.common.comparators import (
    SimpleComparator,
# TODO:
#    ParetoComparator,
)

from evogrid.interfaces import IComparator

#
# Fake test helpers and test fixture
#

class FakeEvaluatedReplicator:
    def __init__(self, ev=0):
        self.evaluation = ev
    def __repr__(self):
        # this is just to make error messages easier to read when tests fail
        return "<%s object with evaluation=%r>" % (
            self.__class__.__name__, self.evaluation)


#
# Test cases
#

class ComparatorTestCase(unittest.TestCase):

    def test_interfaces(self):
        self.assert_(verifyClass(IComparator, SimpleComparator))

    def test_SimpleComparator(self):
        simple_comparator = SimpleComparator()
        self.assert_(verifyObject(IComparator, simple_comparator))
        rep1, rep2 = FakeEvaluatedReplicator(1), FakeEvaluatedReplicator(2)
        self.assertEquals(simple_comparator.cmp(rep1, rep2), -1)
        self.assertEquals(simple_comparator.cmp(rep1, rep1),  0)
        self.assertEquals(simple_comparator.cmp(rep2, rep2),  0)
        self.assertEquals(simple_comparator.cmp(rep2, rep1),  1)

#
# Comparators' test suite
#

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(ComparatorTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

