import unittest
from zope.interface.verify import verifyClass
from numpy import array, square
from math import sqrt

from evogrid.interfaces import IVariator
from evogrid.common.replicators import Replicator
from evogrid.numeric.dejong import DeJongEvaluator
from evogrid.numeric.variators import (
    SimplexVariator,
    BfgsVariator,
    CgVariator,
    PowellVariator,
)

variator_klasses = (
    SimplexVariator,
    BfgsVariator,
    CgVariator,
    PowellVariator,
)


def make_test_case(klass):
    class BaseVariatorTestCase(unittest.TestCase):
        klass = None

        def setUp(self):
            self.evaluator = DeJongEvaluator(4)
            self.variator = self.klass(self.evaluator)
            cs0 = array([-1., -1.])
            self.rep = Replicator(cs=cs0)
            self.ev0 = self.evaluator.compute_fitness(cs0)

        def test_interface(self):
            self.assert_(verifyClass(IVariator, self.klass))

        def test_default_maxiter(self):
            rep = self.rep

            self.assertEquals(self.variator.maxiter, 10)

            result = self.variator.combine(rep)
            expected = (rep,)
            self.assertEquals(result, expected)

            ev = self.evaluator.compute_fitness(rep.candidate_solution)
            self.assert_(ev < self.ev0, 'fitness was not minimized')

        def test_maxiter_none(self):
            rep = self.rep
            self.variator = self.klass(self.evaluator, maxiter=None)

            maxiter = self.variator.maxiter
            self.assert_(maxiter is None)

            # wait till convergence
            result = self.variator.combine(rep)
            expected = (rep,)
            self.assertEquals(result, expected)

            ev = self.evaluator.compute_fitness(rep.candidate_solution)
            self.assert_(ev < self.ev0, 'fitness was not minimized')

            # check that we are close to (1, 1)
            cs = rep.candidate_solution
            d = sqrt(square(cs - array([1., 1.])).sum())
            self.assert_(d < 0.001, 'algorithm stopped at %r' % cs)

    name = klass.__name__ + 'TestCase'
    return type(name, (BaseVariatorTestCase,), {'klass': klass})


def test_suite():
    suite = unittest.TestSuite()
    for variator_klass in variator_klasses:
        suite.addTests(unittest.makeSuite(make_test_case(variator_klass)))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

