from zope.testing import doctest
import unittest
import random
from copy import deepcopy
from itertools import islice

from zope.interface.verify import verifyClass, verifyObject

import evogrid.common.selectors

from evogrid.common.selectors import (
    BaseSelector,
    EliteSelector,
    RandomSelector,
    TournamentSelector,
    ProviderFromSelectorAndPool,
)

from evogrid.interfaces import (
    IProvider,
    ISelector,
    IRemoverSelector,
    ICopierSelector,
)

#
# Fake test helpers and test fixture
#

class FakeEvaluatedReplicator:
    def __init__(self, ev=0):
        self.evaluation = ev
    def replicate(self):
        return deepcopy(self)
    def __repr__(self):
        # this is just to make error messages easier to read when tests fail
        return "<%s object with evaluation=%r>" % (
            self.__class__.__name__, self.evaluation)

class FixtureForSelectorTestCase(unittest.TestCase):

    def setUp(self):
        random.seed('seed to make the tests reproducible')
        # use a fake ordered pool to get reproducible results:
        self.pool = [FakeEvaluatedReplicator(i) for i in xrange(5)]

#
# Actual test cases
#

class SelectorTestCase(FixtureForSelectorTestCase):

    def _test_provider(self, selector, expected_evaluations,
                       nb_to_provide=None):
        # test the selector by adapting it to a provider
        pool = self.pool
        initial_pool_len = len(pool)
        provider = ProviderFromSelectorAndPool(selector, pool)

        # check the interface
        self.assert_(verifyObject(IProvider, provider))

        # base selectors are usually adapted to infinite providers  just compare
        # the first elements but we can generate more to be able to check
        # whether StopIteration occurs at the right time
        if nb_to_provide is None:
            nb_to_provide = len(expected_evaluations)
        selected = list(islice(provider, nb_to_provide))

        # check that the evaluations match
        self.assertEquals([rep.evaluation for rep in selected],
                           expected_evaluations)

        # base selectors return replicators that are still in the pool
        self.assertEquals(len(pool), initial_pool_len)
        for rep in selected:
            self.assert_(rep in pool)

    def test_BaseSelector(self):
        pool = self.pool
        known_to_be_the_max = pool[4]
        base_selector = BaseSelector()
        self.assertEquals(base_selector._max(pool), known_to_be_the_max)
        random.shuffle(pool)
        self.assertEquals(base_selector._max(pool), known_to_be_the_max)
        random.shuffle(pool)
        self.assertEquals(base_selector._max(pool), known_to_be_the_max)
        random.shuffle(pool)
        self.assertEquals(base_selector._max(pool), known_to_be_the_max)

    def test_RandomSelector(self):
        pool = self.pool
        self.assert_(verifyClass(ISelector, RandomSelector))
        random_selector = RandomSelector()

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 3)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 2)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

    def test_RandomSelector_provider(self):
        self._test_provider(RandomSelector(), [4, 3, 4, 2])

    def test_EliteSelector(self):
        pool = self.pool
        self.assert_(verifyClass(ISelector, EliteSelector))
        elite_selector = EliteSelector()

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

    def test_EliteSelector_provider(self):
        self._test_provider(EliteSelector(), [4]*42)

    def test_2OpponentsTournamentSelector(self):
        pool = self.pool
        self.assert_(verifyClass(ISelector, TournamentSelector))
        tournament_selector = TournamentSelector(n=2)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 3)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 1)
        self.assertEquals(len(pool), 5)
        self.assert_(rep in pool)

    def test_2OpponentsTournamentSelector_provider(self):
        self._test_provider(TournamentSelector(), [4, 4, 4, 4, 3, 1])

    def test_6OpponnentsTournamentSelector(self):
        pool = self.pool
        self.assert_(verifyClass(ISelector, TournamentSelector))
        tournament_selector = TournamentSelector(n=6)

        # Pool is too small to find 6 opponents-> ValueError
        self.assertRaises(ValueError, tournament_selector.select_from, pool)

    def test_6OpponentsTournamentSelector_provider(self):
        self._test_provider(TournamentSelector(n=6), [], nb_to_provide=10)

class CopierSelectorTestCase(FixtureForSelectorTestCase):

    def _test_provider(self, selector, expected_evaluations,
                       nb_to_provide=None):
        # test the selector by adapting it to a provider
        pool = self.pool
        initial_pool_len = len(pool)
        provider = ProviderFromSelectorAndPool(selector, pool)

        # check the interface
        self.assert_(verifyObject(IProvider, provider))

        # copier selectors are usually adapted to infinite providers
        # just compare the first elements but we can generate more to be able to
        # check wheter StopIteration occurs at the right time
        if nb_to_provide is None:
            nb_to_provide = len(expected_evaluations)
        selected = list(islice(provider, nb_to_provide))

        # check that the evaluations match
        self.assertEquals([rep.evaluation for rep in selected],
                           expected_evaluations)

        # copier selectors return replicators that are copies of those in the
        # pool thus no longuer in the pool them-selves
        self.assertEquals(len(pool), initial_pool_len)
        for rep in selected:
            self.assert_(rep not in pool)

    def test_RandomSelector(self):
        pool = self.pool
        random_selector = ICopierSelector(RandomSelector())
        self.assert_(verifyObject(ICopierSelector, random_selector))

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 3)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 2)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

    def test_RandomSelector_provider(self):
        self._test_provider(ICopierSelector(RandomSelector()), [4, 3, 4, 2])

    def test_EliteSelector(self):
        pool = self.pool
        elite_selector = ICopierSelector(EliteSelector())
        self.assert_(verifyObject(ICopierSelector, elite_selector))

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

    def test_EliteSelector_provider(self):
        self._test_provider(ICopierSelector(EliteSelector()), [4]*42)

    def test_2OpponentsTournamentSelector(self):
        pool = self.pool
        tournament_selector = ICopierSelector(TournamentSelector(n=2))
        self.assert_(verifyObject(ICopierSelector, tournament_selector))

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 3)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

        rep = tournament_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 1)
        self.assertEquals(len(pool), 5)
        self.assert_(rep not in pool)

    def test_2OpponentsTournamentSelector_provider(self):
        self._test_provider(ICopierSelector(TournamentSelector()),
                            [4, 4, 4, 4, 3, 1])

    def test_6OpponnentsTournamentSelector(self):
        pool = self.pool
        tournament_selector = ICopierSelector(TournamentSelector(n=6))
        self.assert_(verifyObject(ICopierSelector, tournament_selector))

        # Pool is too small to find 5 opponents-> ValueError
        self.assertRaises(ValueError, tournament_selector.select_from, pool)

    def test_6OpponentsTournamentSelector_provider(self):
        self._test_provider(ICopierSelector(TournamentSelector(n=6)), [],
                            nb_to_provide=10)

class RemoverSelectorTestCase(FixtureForSelectorTestCase):

    def _test_provider(self, selector, expected_evaluations, nb_remaining=0):
        # test the selector by adapting it to a provider
        pool = self.pool
        provider = ProviderFromSelectorAndPool(selector, pool)

        # check the interface
        self.assert_(verifyObject(IProvider, provider))

        # remover selectors are adapter to finite providers (unless the pool is
        # infinite which is not likely to occur because of the __len__ method)
        selected = list(provider)

        # check that the evaluations match
        self.assertEquals([rep.evaluation for rep in selected],
                           expected_evaluations)

        # removers selectors return replicators that are removed out of the pool
        # in some cases the iterations stops before the pool is empty
        self.assertEquals(len(pool), nb_remaining)
        for rep in selected:
            self.assert_(rep not in pool)

    def test_RandomSelector(self):
        pool = self.pool
        random_selector = IRemoverSelector(RandomSelector())
        self.assert_(verifyObject(IRemoverSelector, random_selector))

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 4)
        self.assert_(rep not in pool)

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 2)
        self.assertEquals(len(pool), 3)
        self.assert_(rep not in pool)

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 3)
        self.assertEquals(len(pool), 2)
        self.assert_(rep not in pool)

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 1)
        self.assertEquals(len(pool), 1)
        self.assert_(rep not in pool)

        rep = random_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 0)
        self.assertEquals(len(pool), 0)
        self.assert_(rep not in pool)

        # No more replicator in the pool -> ValueError
        self.assertRaises(ValueError, random_selector.select_from, pool)

    def test_RandomSelector_provider(self):
        self._test_provider(IRemoverSelector(RandomSelector()), [4, 2, 3, 1, 0])

    def test_EliteSelector(self):
        pool = self.pool
        elite_selector = IRemoverSelector(EliteSelector())
        self.assert_(verifyObject(IRemoverSelector, elite_selector))

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 4)
        self.assert_(rep not in pool)

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 3)
        self.assertEquals(len(pool), 3)
        self.assert_(rep not in pool)

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 2)
        self.assertEquals(len(pool), 2)
        self.assert_(rep not in pool)

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 1)
        self.assertEquals(len(pool), 1)
        self.assert_(rep not in pool)

        rep = elite_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 0)
        self.assertEquals(len(pool), 0)
        self.assert_(rep not in pool)

        # Pool is empty -> ValueError
        self.assertRaises(ValueError, elite_selector.select_from, pool)

    def test_EliteSelector_provider(self):
        self._test_provider(IRemoverSelector(EliteSelector()), [4, 3, 2, 1, 0])

    def test_3OpponentsTournamentSelector(self):
        pool = self.pool
        tournamenent_selector = IRemoverSelector(TournamentSelector(n=3))
        self.assert_(verifyObject(IRemoverSelector, tournamenent_selector))

        rep = tournamenent_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 4)
        self.assert_(rep not in pool)

        rep = tournamenent_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 3)
        self.assertEquals(len(pool), 3)
        self.assert_(rep not in pool)

        rep = tournamenent_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 2)
        self.assertEquals(len(pool), 2)
        self.assert_(rep not in pool)

        # Pool is too small to find 3 opponents-> ValueError
        self.assertRaises(ValueError, tournamenent_selector.select_from, pool)

    def test_3OpponentsTournamentSelector_provider(self):
        self._test_provider(IRemoverSelector(TournamentSelector(n=3)),
                            [4, 3, 2], nb_remaining=2)

    def test_5OpponnentsTournamentSelector(self):
        pool = self.pool
        tournamenent_selector = IRemoverSelector(TournamentSelector(n=5))
        self.assert_(verifyObject(IRemoverSelector, tournamenent_selector))

        rep = tournamenent_selector.select_from(pool)
        self.assertEquals(rep.evaluation, 4)
        self.assertEquals(len(pool), 4)

        # Pool is too small to find 5 opponents-> ValueError
        self.assertRaises(ValueError, tournamenent_selector.select_from, pool)

    def test_5OpponentsTournamentSelector_provider(self):
        self._test_provider(IRemoverSelector(TournamentSelector(n=5)),
                            [4], nb_remaining=4)

#
# Selectors' test suite
#

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(SelectorTestCase))
    suite.addTests(unittest.makeSuite(CopierSelectorTestCase))
    suite.addTests(unittest.makeSuite(RemoverSelectorTestCase))
    suite.addTests(doctest.DocTestSuite(evogrid.common.selectors))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

