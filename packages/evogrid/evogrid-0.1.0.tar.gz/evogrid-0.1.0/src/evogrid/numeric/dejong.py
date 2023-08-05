# (C) Copyright 2006 Olivier Grisel
# Author: Olivier Grisel <olivier.grisel@ensta.org>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""numpy based implementation of De Jong test functions

The following functions are often use in the literature to test the
performance of numerical optimization algorithms. Most of them were
instroduced by De Jong K.A. in:

  - De Jong K. A. 1975. Analysis of the behavioir of a class of genetic
    adaptive systems. Ph.D. Dissertation. University of Michigan, Ann Arbor.

The remaining were collected from other work and gatehered by Haupt
R. L. and Haupt S. E. in:

  - Haupt R. L. and Haupt S. E. 2004. Practical Genetic Algorithms. Wiley.

Each function takes a single ndarray instance of shape ``(N,)`` were N
is the dimension of the search space.

Most functions can accept any integer dimension. In that case, they implement
the ``INDimTestFunction`` interface. Some are restricted to dimenension 2,
in which case they implement ``I2DimTestFunction``. These two interfaces both
derive from ``ITestFunction``.

Most functions have a ``minimum`` attribute that gives the best known
(proved or not) value of x in N x N that minimizes the value of f.

In order to be able to quickly check the correctness of the function,
value of the minimum point is also given by the ``minimum_value``
attribute.

They also have a ``bounds`` attribute valued to a ``(min, max)`` tuple
or None of the search domain is not restricted.
"""

from zope.component import adapts
from zope.interface import implementer, implements

from evogrid.interfaces import IEvaluator
from evogrid.common.evaluators import BaseEvaluator
from evogrid.numeric.interfaces import (
    ITestFunction,
    I2DimTestFunction,
    INDimTestFunction,
)

from math import cos as mcos
from math import sin as msin
from math import sqrt as msqrt
from math import exp as mexp

from numpy import (
    arange,
    array,
    cos,
    pi,
    sin,
    sqrt,
    square,
)

test_functions = []

@implementer(INDimTestFunction)
def f1(x):
    return (abs(x) + cos(x)).sum()

f1.minimum = array([0, 0])
f1.minimum_value = 2
f1.bounds = None

test_functions.append(f1)

@implementer(INDimTestFunction)
def f2(x):
    return (abs(x)+ sin(x)).sum()

f2.minimum = array([0, 0])
f2.minimum_value = 0
f2.bounds = None

test_functions.append(f2)

@implementer(INDimTestFunction)
def f3(x):
    return square(x).sum()

f3.minimum = array([0, 0])
f3.minimum_value = 0
f3.bounds = None

test_functions.append(f3)

@implementer(INDimTestFunction)
def f4(x):
    return (100 * square(x[1:] - square(x[:-1])) + square(1 - x[:-1])).sum()

f4.minimum = array([1, 1])
f4.minimum_value = 0
f4.bounds = None

test_functions.append(f4)

@implementer(INDimTestFunction)
def f5(x):
    return (abs(x) - 10 * cos(sqrt(10 * abs(x)))).sum()

f5.minimum = array([0, 0])
f5.minimum_value = -20
f5.bounds = None

test_functions.append(f5)

@implementer(INDimTestFunction)
def f6(x):
    return ((square(x) + x) * cos(x)).sum()

f6.minimum = array([9.6204, 9.6204])
f6.minimum_value = -200.4475
f6.bounds = (-10., 10.)

test_functions.append(f6)

@implementer(I2DimTestFunction)
def f7(x):
    y = x[1]
    x = x[0]
    return x * msin(4. * x) + 1.1 * y * msin(2. * y)

f7.minimum = array([9.039, 8.668])
f7.minimum_value = -18.5547
f7.bounds = (0., 10.)

test_functions.append(f7)

@implementer(I2DimTestFunction)
def f8(x):
    y = x[1]
    x = x[0]
    return y * msin(4 * x) + 1.1 * x * msin(2 * y)

f8.minimum = array([9.0400048, 8.6645185])
f8.minimum_value = -18.5916
f8.bounds = (0., 10.)

test_functions.append(f8)

@implementer(INDimTestFunction)
def f9(x):
    return (arange(len(x)) * x ** 4).sum() # TODO add Nn(0, 1)

f9.minimum = array([0., 0.])
f9.minimum_value = 0
f9.bounds = None

test_functions.append(f9)

@implementer(INDimTestFunction)
def f10(x):
    return 10 * len(x) + (square(x) - 10 * cos(2 * pi * x)).sum()

f10.minimum = array([0., 0.])
f10.minimum_value = 0
f10.bounds = None

test_functions.append(f10)

@implementer(INDimTestFunction)
def f11(x):
    return 1 + (square(x)/4000.).sum() - cos(x).prod()

f11.minimum = array([0., 0.])
f11.minimum_value = 0
f11.bounds = None

test_functions.append(f11)

@implementer(I2DimTestFunction)
def f12(x):
    y = x[1]
    x = x[0]
    return 0.5 + ((msin(msqrt(x ** 2 + y ** 2)) ** 2 - 0.5)
                  / (1 + .1 * (x ** 2 + y ** 2)))

f12.minimum = array([0., 0.])
f12.minimum_value = 0.
f12.bounds = None

test_functions.append(f12)

@implementer(I2DimTestFunction)
def f13(x):
    y = x[1]
    x = x[0]
    return ((x ** 2 + y ** 2) ** 0.25
            * msin(30 * ((x + .5) ** 2 + y ** 2) ** 0.1)
            + abs(x) + abs(y))

f13.minimum = array([-0.20215, 0.])
f13.minimum_value = -0.24740
f13.bounds = None

test_functions.append(f13)

@implementer(I2DimTestFunction)
def f14(x):
    y = x[1]
    x = x[0]
    # XXX: what is J0?
    return (x ** 2 + y ** 2) + .1 * (abs(1- x) + abs(1 - y))

f14.minimum = array([0.05, 0.05])
f14.minimum_value = 0.19500
f14.bounds = None

test_functions.append(f14)

@implementer(I2DimTestFunction)
def f15(x):
    y = x[1]
    x = x[0]
    return - mexp(-.2 * msqrt(x ** 2 + y ** 2)
                  + 3 * (mcos(2 * x) + msin(2 * y)))

f15.minimum = array([0., 0.76872])
f15.minimum_value = -345.35994
f15.bounds = (-5., 5.)

test_functions.append(f15)

@implementer(I2DimTestFunction)
def f16(x):
    y = x[1]
    x = x[0]
    return (-      x  * msin(msqrt(abs(x - (y + 9))))
            - (y + 9) * msin(msqrt(abs(y + .5 * x + 9))))

f16.minimum = array([-17.006978, 2.073026])
f16.minimum_value = -25.23053
f16.bounds = (-20., 20.)

test_functions.append(f16)

#
# DeJong F to Evaluator adapter
#

class DeJongEvaluator(BaseEvaluator):
    """Adapter to build an evaluator out of a De Jong function"""
    implements(IEvaluator)
    adapts(ITestFunction)

    def __init__(self, f):
        """Either provide a the function itself or its number"""
        if isinstance(f, int):
            f = test_functions[f-1]
        self.func = f

    def compute_fitness(self, cs):
        return self.func(cs)

