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
"""Variators for numpy array encoded replicators

Some of the following variators are deterministic Lamarckian optimizers
whereas other are just blind Darwinian varitors (mutators and crossing over
style combinators).
"""

from zope.interface import implements
from zope.component import adapts
from evogrid.interfaces import IEvaluator, IVariator
from numpy import array
from numpy.random import uniform, normal
from scipy.optimize import (
    fmin,
    fmin_bfgs,
    fmin_cg,
    fmin_powell,
)

#
# Darwinian operators
#

class GaussianMutator(object):
    """Apply centered gaussian noise to the replicator"""
    implements(IVariator)

    number_to_combine = 1

    def __init__(self, scale=1., scales=None):
        self.scale = scale
        self.scales = scales

    def combine(self, *reps):
        rep = reps[0]
        scales = self.scales
        if scales is not None:
            delta = array([scale and normal(scale=scale) or 0.
                           for scale in scales])
        else:
            delta = normal(scale=self.scale, size=len(rep.candidate_solution))
        rep.candidate_solution += delta
        return (rep,)


class DomainAwareGaussianMutator(object):
    """Apply centered gaussian noise to the replicator

    The scale here is not a absolute value but multiplied to the size
    of the domain for each variable.
    """
    implements(IVariator)

    number_to_combine = 1

    def __init__(self, scale=.001, scales=None):
        self.scale = scale
        self.scales = scales

    def combine(self, *reps):
        rep = reps[0]
        scales = self.scales
        if scales is None:
            scales = array([self.scale] * len(rep.candidate_solution))

        domain = rep.domain
        sizes = domain.max - domain.min
        scales = scales * sizes

        delta = array([normal(scale=scale) for scale in scales])
        rep.candidate_solution += delta
        return (rep,)


class BlendingCrossover(object):
    """Return two new replicators by linearly combining the parents"""
    implements(IVariator)

    number_to_combine = 2

    def __init__(self, beta_min=0.1, beta_max=1.5):
        self.beta_min = beta_min
        self.beta_max = beta_max

    def combine(self, *replicators):
        rep1, rep2 = replicators
        cs1, cs2 = rep1.candidate_solution, rep2.candidate_solution
        beta = uniform(self.beta_min, self.beta_max, len(cs1))
        rep1.candidate_solution = beta * cs1 + (1 - beta) * cs2
        rep2.candidate_solution = beta * cs2 + (1 - beta) * cs1
        return replicators


#
# Lamarckian operators
#

class BaseLocalSearchVariator(object):
    """Wraps one of scipy.optimize search algorithm into a variator"""
    implements(IVariator)
    adapts(IEvaluator)

    maxiter = 10
    func = None
    optimizer = None

    #
    # IVariator attribute
    #

    number_to_combine = 1

    def __init__(self, evaluator, maxiter=10, **kw):
        self.maxiter = maxiter
        self.func = evaluator.compute_fitness
        self._kw = kw

    def combine(self, *replicators):
        rep = replicators[0]
        optimized = self.optimizer(self.func, rep.candidate_solution,
                                   maxiter=self.maxiter, disp=0, **self._kw)
        rep.candidate_solution = optimized
        return (rep,)

#
# Local Search components
#

class SimplexVariator(BaseLocalSearchVariator):
    optimizer = staticmethod(fmin)


class BfgsVariator(BaseLocalSearchVariator):
    optimizer = staticmethod(fmin_bfgs)


class CgVariator(BaseLocalSearchVariator):
    optimizer = staticmethod(fmin_cg)


class PowellVariator(BaseLocalSearchVariator):
    optimizer = staticmethod(fmin_powell)

