import unittest
from copy import deepcopy
from itertools import islice

from zope.interface import implements
from zope.interface.verify import verifyObject, verifyClass
from zope.component import getMultiAdapter

from evogrid.common.evaluators import ProviderFromEvaluator
from evogrid.interfaces import (
    IReplicator,
    IProvider,
    IEvaluator,
)

class DummyReplicator:
    implements(IReplicator)
    candidate_solution = None
    evaluation = None
    def replicate(self):
        return deepcopy(self)
    def __init__(self, cs=None):
        self.candidate_solution = cs

class DummyProvider:
    implements(IProvider)
    def next(self):
        return DummyReplicator()

class DummyEvaluator:
    implements(IEvaluator)
    def evaluate(self, replicator):
        replicator.evaluation = 1


class EvaluatorAdapterTestCase(unittest.TestCase):

    def setUp(self):
        self.p = DummyProvider()
        self.e = DummyEvaluator()

    def test_interface(self):
        # verifyClass will not work cause the next method is created at init
        # time
        provider = ProviderFromEvaluator(self.e, self.p)
        self.assert_(verifyObject(IProvider, provider))

    def test_evaluatorAdapter(self):
        self.assert_(verifyClass(IProvider, ProviderFromEvaluator))
        provider = ProviderFromEvaluator(self.e, self.p)
        rep1 = provider.next()
        self.assertEquals(rep1.evaluation, 1)
        self.assert_(verifyObject(IProvider, provider))

    def test_evaluatorAdapterIter(self):
        provider = ProviderFromEvaluator(self.e, self.p)
        self.assert_(verifyObject(IProvider, provider))
        for rep in islice(provider, 3):
            self.assertEquals(rep.evaluation, 1)

    def test_evaluatorAdapterRegistration(self):
        provider = getMultiAdapter((self.e, self.p), IProvider)
        self.assert_(verifyObject(IProvider, provider))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(EvaluatorAdapterTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

