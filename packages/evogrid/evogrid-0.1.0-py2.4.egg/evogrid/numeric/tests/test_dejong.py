import unittest
from zope.interface.verify import verifyClass
from numpy import array
from scipy.optimize import fmin_cg

from evogrid.numeric.dejong import test_functions
from evogrid.numeric.interfaces import (
    ITestFunction,
    INDimTestFunction,
)

def make_test_case(f):

    class BaseDeJongTestCase(unittest.TestCase):

        def _get_bounds(self, default_amplitude=2000.):
            bounds = self._get_function().bounds
            if bounds:
                return bounds
            else:
                return (-default_amplitude/2., default_amplitude/2.)

        def test_interface(self):
            self.assert_(verifyClass(ITestFunction, self._get_function()))

        def test_minimim_value(self):
            f = self._get_function()
            expected = f.minimum_value
            result = f(f.minimum)
            msg = "Expected %s(%s)=%r, got %r" % (
                f.__name__, f.minimum, expected, result)
            self.assert_(abs(expected - result) <= 0.0001, msg)

        def test_minimum(self):
            lb, ub = self._get_bounds(default_amplitude=20.)
            f = self._get_function()

            # helper function to check that a vector respects the bounds
            def check_bounds(x):
                do_raise = False
                for i in range(len(x)):
                    xi = x[i]
                    if xi < lb:
                        x[i] = lb
                        do_raise = True
                    elif xi > ub:
                        x[i] = ub
                        do_raise = True
                if do_raise:
                    raise RuntimeError(x)

            # perform a grid of local minimizations
            step_number = 5
            step = float(ub - lb) / step_number
            x = lb
            results = {}
            for i in xrange(step_number):
                x += step
                y = lb
                for j in xrange(step_number):
                    y += step
                    x0 = array([x, y], dtype='g')
                    try:
                        xopt = fmin_cg(f, x0, disp=0, maxiter=10,
                                       callback=check_bounds)
                    except RuntimeError, e:
                        # out of bounds, stop here
                        xopt = e.args[0]
                    results[f(xopt)] = xopt

            # computing the global minimum of the grid of local search
            fopt = min(results.iterkeys())
            xopt = results[fopt]

            # checking that the expected minimum of the function is lower than
            # the one we just found through the grid of local searchs
            f_expected = f(f.minimum)
            name = f.__name__
            error_msg = "%s(%r)=%r is smaller than expected %s(%r)=%r" % (
                name, xopt, fopt, name, f.minimum, f_expected)
            self.assert_((fopt - f_expected) > -0.0001, error_msg)

    class NDimBaseDeJongTestCase(BaseDeJongTestCase):

        def test_ndim_evaluation(self):
            min, max = self._get_bounds()
            f = self._get_function()

            for dim in xrange(3, 100, 5):
                f(array([min] * dim))
                f(array([max] * dim))
                f(array([(max + min) / 2] * dim))


    name = f.__name__.capitalize() + "DeJongTestCase"

    if INDimTestFunction.implementedBy(f):
        bases = (NDimBaseDeJongTestCase,)
    else:
        bases = (BaseDeJongTestCase,)

    return type(name, bases, {'_get_function': lambda self:f})


def test_suite():
    suite = unittest.TestSuite()
    for f in test_functions:
        # XXX: find missing min
        if f.minimum is None:
            print "skipped tests for %s" % f.__name__
            continue
        suite.addTests(unittest.makeSuite(make_test_case(f)))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

