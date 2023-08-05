"""Test suite for the `sharing` package
"""

import unittest
from zope.testing import doctest

from zope.interface.verify import verifyObject

from evogrid.caching.ram import RAMCache
from evogrid.common.pools import Pool
from evogrid.common.replicators import Replicator
from evogrid.common.comparators import SimpleComparator
from evogrid.sharing.comparators import SharingAwareComparator

from evogrid.sharing.interfaces import ISharingAwareComparator

class EvalutedReplicator(Replicator):
    def __init__(self, cs=None, ev=None):
        Replicator.__init__(self, cs=cs)
        self.evaluation = ev


class CustomComparator(SimpleComparator):
    def cmp(self, r1, r2):
        return - cmp(r1.evaluation, r2.evaluation)


class SharingAwareComparatorTestCase(unittest.TestCase):

    def setUp(self):
        self.pool = Pool()
        self.sharing_comparator = SharingAwareComparator(self.pool)
        self.custom_sharing_comparator = SharingAwareComparator(
            self.pool, comparator=CustomComparator())

    def test_interface(self):
        sharing_comparator = SharingAwareComparator(self.pool)
        verifyObject(ISharingAwareComparator, sharing_comparator)

    def test_default_distance(self):
        sc = self.sharing_comparator
        # integers based distances
        self.assertEquals(sc.distance(Replicator(cs=0), Replicator(cs=1)), 1)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=0)), 1)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=2)), 1)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=10)), 9)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=1)), 0)

        # float based distances
        self.assertEquals(sc.distance(Replicator(cs=.0), Replicator(cs=.1)), .1)
        self.assertEquals(sc.distance(Replicator(cs=.1), Replicator(cs=.0)), .1)
        self.assertEquals(sc.distance(Replicator(cs=.1), Replicator(cs=.2)), .1)

    def test_custom_distance(self):
        # Regular function
        def my_distance(a, b): return 2 * abs(a - b)
        sc = SharingAwareComparator(self.pool, distance=my_distance)
        self.assertEquals(sc.distance(Replicator(cs=0), Replicator(cs=1)), 2)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=0)), 2)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=2)), 2)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=10)), 18)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=1)), 0)

        # lambda function
        my_distance = lambda a, b: 2 * abs(a - b)
        sc = SharingAwareComparator(self.pool, distance=my_distance)
        self.assertEquals(sc.distance(Replicator(cs=0), Replicator(cs=1)), 2)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=0)), 2)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=2)), 2)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=10)), 18)
        self.assertEquals(sc.distance(Replicator(cs=1), Replicator(cs=1)), 0)

    def test_shared_evaluation_1(self):
        pool = self.pool
        pool.add(EvalutedReplicator(cs=0, ev=1.0))
        pool.add(EvalutedReplicator(cs=0, ev=1.0))
        pool.add(EvalutedReplicator(cs=1, ev=0.5))
        sc = self.sharing_comparator
        for rep in pool:
            self.assertEquals(sc.share_evaluation(rep), 0.5)

    def test_shared_evaluation_2(self):
        pool = self.pool
        r1 = EvalutedReplicator(cs=0, ev=1.0)
        r2 = EvalutedReplicator(cs=1, ev=0.5)
        pool.add(r1)
        pool.add(r2)
        # symmetrical sharing does not affect natural ordering
        sc = self.sharing_comparator
        shared_r1 = sc.share_evaluation(r1)
        shared_r2 = sc.share_evaluation(r2)
        self.assert_(shared_r1 > shared_r2)

        # assymmetrical sharing reverses ordering: simulates resource exhaustion
        pool.add(EvalutedReplicator(cs=0, ev=1.0))
        pool.add(EvalutedReplicator(cs=0, ev=1.0))
        pool.add(EvalutedReplicator(cs=0, ev=1.0))
        shared_r1 = sc.share_evaluation(r1)
        shared_r2 = sc.share_evaluation(r2)
        self.assert_(shared_r1 < shared_r2)

    def test_default_cmp(self):
        # simulate food exhaustion
        pool = self.pool
        r1 = EvalutedReplicator(cs=0, ev=1.0)
        r2 = EvalutedReplicator(cs=1, ev=0.5)
        pool.add(r1)
        pool.add(r2)
        sc = self.sharing_comparator
        # r1 and r2 are removed out of the sharing context to get compared thus
        # they compare as usual
        self.assertEquals(sc.cmp(r1, r2), 1)

        # add a new replicator next to r1 to devaluate him
        pool.add(EvalutedReplicator(cs=0.1, ev=1.0))

        # this is not enough, r1 is still stronger
        self.assertEquals(sc.cmp(r1, r2), 1)

        # but if we add one more replicator in r1 neighborhood, r2 gets stronger
        pool.add(EvalutedReplicator(cs=0.1, ev=1.0))
        self.assertEquals(sc.cmp(r1, r2), -1)

    def test_default_cmp_not_in_context(self):
        pool = self.pool
        r1 = EvalutedReplicator(cs=0, ev=1.0)
        r2 = EvalutedReplicator(cs=1, ev=0.5)
        pool.add(r1)
        pool.add(r2)
        sc = self.sharing_comparator
        self.assertEquals(sc.cmp(r1, r2), 1)

        # if we compare with r1bis that is not in pool we get the same result as
        # replicators are taken out of the sharing context before comparison:
        r1bis = EvalutedReplicator(cs=0, ev=1.0)
        self.assertEquals(sc.cmp(r1bis, r2), 1)

        # add if we change the sharing context, r1 and r1bis do still have the
        # same strength
        pool.add(EvalutedReplicator(cs=0.1, ev=1.0))
        pool.add(EvalutedReplicator(cs=0.1, ev=1.0))
        self.assertEquals(sc.cmp(r1, r2), -1)
        self.assertEquals(sc.cmp(r1bis, r2), -1)

    def test_custom_cmp(self):
        pool = self.pool
        # Use the CustomComparator that transforms that takes the least
        # evaluated replicator instead of the best one
        c = self.custom_sharing_comparator
        r1 = EvalutedReplicator(cs=0, ev=1.0)
        r2 = EvalutedReplicator(cs=1, ev=0.5)
        pool.add(r1)
        pool.add(r2)
        self.assertEquals(c.cmp(r1, r2), -1)

        # simulate food exhaustion:
        pool.add(EvalutedReplicator(cs=0, ev=1))
        pool.add(EvalutedReplicator(cs=0, ev=1))
        self.assertEquals(c.cmp(r1, r2), 1)

    def test_default_max(self):
        c = self.sharing_comparator
        pool = self.pool
        replicators = (
            EvalutedReplicator(cs=0, ev=5),
            EvalutedReplicator(cs=1, ev=10),
            EvalutedReplicator(cs=2, ev=4),
        )
        for rep in replicators:
            pool.add(rep)

        # all replicators are taken away of the sharing context, this is just
        # normal max
        self.assertEquals(c.max(replicators), replicators[1])

        # add more replicators to change the maximum
        pool.add(EvalutedReplicator(cs=1, ev=10))
        pool.add(EvalutedReplicator(cs=1, ev=10))
        self.assertEquals(c.max(replicators), replicators[0])

        # add more replicators to change the maximum once again
        pool.add(EvalutedReplicator(cs=0.5, ev=5))
        pool.add(EvalutedReplicator(cs=0.5, ev=5))
        self.assertEquals(c.max(replicators), replicators[2])

    def test_custom_max(self):
        # use the sharing comparator with inverted comparator logic
        c = self.custom_sharing_comparator
        pool = self.pool
        replicators = (
            EvalutedReplicator(cs=0, ev=5),
            EvalutedReplicator(cs=1, ev=10),
            EvalutedReplicator(cs=2, ev=4),
        )
        for rep in replicators:
            pool.add(rep)

        self.assertEquals(c.max(replicators), replicators[2])

        # add more replicators to change the maximum which actually is a minimum
        # is the CustomComparator case
        pool.add(EvalutedReplicator(cs=0.5, ev=5))
        pool.add(EvalutedReplicator(cs=0.5, ev=5))
        self.assertEquals(c.max(replicators), replicators[0])

        # add more replicators to change the minimum once again
        pool.add(EvalutedReplicator(cs=1, ev=10))
        pool.add(EvalutedReplicator(cs=1, ev=10))
        pool.add(EvalutedReplicator(cs=1, ev=10))
        pool.add(EvalutedReplicator(cs=1, ev=10))
        pool.add(EvalutedReplicator(cs=1, ev=10))
        pool.add(EvalutedReplicator(cs=1, ev=10))
        self.assertEquals(c.max(replicators), replicators[1])


class MemoizedSharingAwareComparatorTestCase(SharingAwareComparatorTestCase):
    # same as above using a RAMCache

    def setUp(self):
        self.pool = Pool()
        self.sharing_comparator = SharingAwareComparator(
            self.pool, cache=RAMCache())
        self.custom_sharing_comparator = SharingAwareComparator(
            self.pool, comparator=CustomComparator(), cache=RAMCache())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocFileSuite('README.txt'))
    suite.addTests(unittest.makeSuite(SharingAwareComparatorTestCase))
    suite.addTests(unittest.makeSuite(MemoizedSharingAwareComparatorTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
