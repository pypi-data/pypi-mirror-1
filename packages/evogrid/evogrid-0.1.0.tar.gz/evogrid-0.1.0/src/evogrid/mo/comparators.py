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
"""Comparator implementations for Multi Objective optimization"""

from evogrid.common.comparators import SimpleComparator
from evogrid.interfaces import IPool
from evogrid.mo.interfaces import IMultiObjectiveComparator
from evogrid.sharing.comparators import SharingAwareComparator
from evogrid.sharing.interfaces import ISharingAwareComparator
from math import sqrt
from zope.component import adapts
from zope.interface import implements

#
# Comparators based on the dominance
#

class BaseParetoComparator(SimpleComparator):
    """Abstract class to factorize code between Pareto comparators

    The Pareto comparators takes a sequence of comparison functions of length
    the length of the evaluations vectors to compare. If that list is not
    provided, you should at least provide the ``vector_len`` integer value so
    that it will be able to build it's own internal list of comparison
    functions based on the ``cmp`` builtin.

    The optional ``mask`` argument makes it possible to ignore some criterion
    by passing a tuple of boolean flags of length ``vector_len``.
    """

    def __init__(self, cmp_funcs=None, vector_len=None, mask=None):
        if vector_len is None and cmp_funcs is None:
            raise ValueError('ParetoComparator need at least vector_len or '
                             'cmp_funcs at init time')
        cmp_funcs = cmp_funcs or [cmp] * vector_len
        if mask:
            def ignore(r1, r2): return 0
            cmp_funcs = (flag and func or ignore
                         for func, flag in zip(cmp_funcs, mask))
        self._cmp_funcs = tuple(cmp_funcs)

    def cmp(self, r1, r2):
        raise NotImplementedError

    # max is inherited from SimpleComparator


class WeakParetoComparator(BaseParetoComparator):
    """Comparator that implements the weak Pareto-dominance relation

    A vector v1 weakly pareto-dominates a vector v2 if none of the v2
    coordinates is strictly greater than those in v1 and at least one the v1 is
    stricly greater than its v2 counterpart.
    """
    implements(IMultiObjectiveComparator)

    # this should remain read only
    _weak_pareto_map = {
        (True,  True):   0,
        (True,  False):  1,
        (False, True):  -1,
        (False, False):  0,
    }

    def cmp(self, r1, r2):
        r1_has_dominance, r2_has_dominance = False, False
        for func, c1, c2 in zip(self._cmp_funcs, r1.evaluation, r2.evaluation):
            res =  func(c1, c2)
            if res == 1:
                r1_has_dominance = True
            elif res == -1:
                r2_has_dominance = True
        return self._weak_pareto_map[(r1_has_dominance, r2_has_dominance)]

    # max is inherited from SimpleComparator


class StrongParetoComparator(BaseParetoComparator):
    """Comparator that implements the strong Pareto-dominance relation

    A vector v1 strongly pareto-dominates a vector v2 if all the v1 coordinates
    are stricly greater than their v2 counterpart.
    """
    implements(IMultiObjectiveComparator)

    # this should remain read only
    _strong_pareto_map = {
        (True,  False):  1,
        (False, True):  -1,
        (False, False):  0,
    }

    def cmp(self, r1, r2):
        r1_always_dominant, r2_always_dominant = True, True
        for func, c1, c2 in zip(self._cmp_funcs, r1.evaluation, r2.evaluation):
            res =  func(c1, c2)
            if res == 1:
                r2_always_dominant = False
            elif res == -1:
                r1_always_dominant = False
            else:
                r1_always_dominant = False
                r2_always_dominant = False
        return self._strong_pareto_map[(r1_always_dominant, r2_always_dominant)]

    # max is inherited from SimpleComparator


class RelaxedParetoComparator(BaseParetoComparator):
    """More permissive Pareto comparator"""
    implements(IMultiObjectiveComparator)
    # TODO:


#
# Lagrangian based comparators
#

class WeightedSumComparator(SimpleComparator):
    """Compare weighted sums of evaluation vectors"""
    implements(IMultiObjectiveComparator)

    def __init__(self, weights, custom_cmp=None):
        self._weights = weights
        self._cmp = custom_cmp or cmp

    def _weighted_sum(self, r):
        sum = 0
        for w, c in zip(self._weights, r.evaluation):
            sum += w * c
        return sum

    def cmp(self, r1, r2):
        return self._cmp(self._weighted_sum(r1), self._weighted_sum(r2))

    # max is inherited from SimpleComparator


#
# Fitness Sharing aware comparator adapter
#

class FitnessSharingAwareComparator(SharingAwareComparator):
    """Share according to some distance in fitness space """
    implements(IMultiObjectiveComparator, ISharingAwareComparator)
    adapts(IPool, IMultiObjectiveComparator)
    # XXX: this is a broken implementation that does not work on vectors

    def _distance(self, a, b):
        """Default euclidian distance measure between two vectors

        Can get overridden by the constructor.
        """
        squares = 0
        for ai, bi in zip(a, b):
            squares += (bi - ai) ** 2
        return sqrt(squares)

    def distance(self, rep1, rep2):
        """Compute the distance between two replicators' fitnesses"""
        return self._distance(rep1.evaluation, rep2.evaluation)


