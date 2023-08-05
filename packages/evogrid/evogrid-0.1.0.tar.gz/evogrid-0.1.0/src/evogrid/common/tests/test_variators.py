import unittest
from itertools import islice

from zope.interface import implements
from zope.interface.verify import verifyObject, verifyClass
from zope.component import getMultiAdapter

from evogrid.common.variators import ProviderFromVariator
from evogrid.interfaces import (
    IReplicator,
    IProvider,
    IVariator,
)

class DummyReplicator:
    implements(IReplicator)

class DummyReplicator2:
    implements(IReplicator)

class DummyProvider:
    implements(IProvider)
    klass = DummyReplicator
    def next(self):
        return self.klass()
    def __iter__(self):
        return self

class DummyVariator:
    implements(IVariator)
    number_to_combine = 2
    def combine(self, *replicators):
        return (replicators[0],)

class VariatorTestCase(unittest.TestCase):

    def setUp(self):
        self.p = DummyProvider()
        self.v = DummyVariator()

    def test_variatorAdapter(self):
        self.assert_(verifyClass(IProvider, ProviderFromVariator))
        provider = ProviderFromVariator(self.v, self.p)
        self.assert_(verifyObject(IProvider, provider))
        rep = provider.next()
        self.assert_(IReplicator.providedBy(rep))

    def test_variatorAdapterIter(self):
        provider = ProviderFromVariator(self.v, self.p)
        for rep in islice(provider, 3):
            self.assert_(IReplicator.providedBy(rep))

    def test_variatorAdapterChangeProvider(self):
        provider = ProviderFromVariator(self.v, self.p)
        for rep in islice(provider, 3):
            self.assert_(IReplicator.providedBy(rep))
            self.assertEquals(rep.__class__, DummyReplicator)

        # changing the upstream provider on a live instance
        p2 = DummyProvider()
        p2.klass = DummyReplicator2
        provider.provider = p2
        for rep in islice(provider, 3):
            self.assert_(IReplicator.providedBy(rep))
            self.assertEquals(rep.__class__, DummyReplicator2)



    def test_variatorAdapterRegistration(self):
        provider = getMultiAdapter((self.v, self.p), IProvider)
        self.assert_(verifyObject(IProvider, provider))
        rep = provider.next()
        self.assert_(IReplicator.providedBy(rep))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(VariatorTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

