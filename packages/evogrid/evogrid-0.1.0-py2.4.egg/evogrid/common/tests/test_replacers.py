import unittest

from zope.interface.verify import verifyClass

from evogrid.common.replacers import GenerationalReplacer
from evogrid.common.replacers import TournamentReplacer
from evogrid.common.tests.test_selectors import FakeEvaluatedReplicator

from evogrid.interfaces import IReplacer

class ReplacerTestCase(unittest.TestCase):

    def setUp(self):
        self.pool = set(FakeEvaluatedReplicator(i) for i in range(5))

    def test_generational_replacement_interface(self):
        self.assert_(verifyClass(IReplacer, GenerationalReplacer))

    def test_generational_replacement(self):
        pool = self.pool
        former_replicators = set(pool)
        provider = (FakeEvaluatedReplicator(0) for _ in xrange(1000))
        replacer = GenerationalReplacer()
        replacer.replace(provider, pool)
        self.assertEquals(len(pool), 5)
        for rep in pool:
            self.assert_(rep not in former_replicators)
            self.assertEquals(rep.evaluation, 0)

    def test_generational_replacement_number(self):
        pool = self.pool
        former_replicators = set(pool)
        provider = (FakeEvaluatedReplicator(0) for _ in xrange(1000))
        replacer = GenerationalReplacer(number=2)
        replacer.replace(provider, pool)
        self.assertEquals(len(pool), 2)
        for rep in pool:
            self.assert_(rep not in former_replicators)
            self.assertEquals(rep.evaluation, 0)

    def test_tournament_replacement_interface(self):
        self.assert_(verifyClass(IReplacer, TournamentReplacer))

    def test_tournament_replacement_1(self):
        pool = self.pool
        former_replicators = set(pool)
        replacer = TournamentReplacer()

        # Replacing with bad replicators should not affect the pool as they are
        # not good enough to win tournaments
        provider = (FakeEvaluatedReplicator(-1) for _ in xrange(1000))
        replacer.replace(provider, pool)
        for rep in former_replicators:
            self.assert_(rep in pool)

    def test_tournament_replacement_2(self):
        pool = self.pool
        former_replicators = set(pool)
        replacer = TournamentReplacer()

        # Replacing with good replicators should put them back into the pool
        provider = (FakeEvaluatedReplicator(10) for _ in xrange(1000))
        replacer.replace(provider, pool)
        self.assert_(10 in [rep.evaluation for rep in pool])

    def test_tournament_replacement_number_1(self):
        # using the number argument
        pool = self.pool
        former_replicators = set(pool)
        replacer = TournamentReplacer(number=1)

        # Replacing with bad replicators should not affect the pool as they are
        # not good enough to win tournaments
        provider = (FakeEvaluatedReplicator(-1) for _ in xrange(1000))
        replacer.replace(provider, pool)
        for rep in former_replicators:
            self.assert_(rep in pool)
        replacer.number = 10
        replacer.replace(provider, pool)
        for rep in former_replicators:
            self.assert_(rep in pool)

    def test_tournament_replacement_number_2(self):
        # using the number argument
        pool = self.pool
        former_replicators = set(pool)
        replacer = TournamentReplacer(number=1)

        # Replacing with good replicators should put them back into the pool
        provider = (FakeEvaluatedReplicator(10) for _ in xrange(1000))
        replacer.replace(provider, pool)
        self.assertEquals(len([rep for rep in pool if rep.evaluation==10]), 1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(ReplacerTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


