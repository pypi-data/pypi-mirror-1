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
"""Sharing aware pools
"""

from zope.component import adapts
from zope.interface import implements, implementer

from evogrid.caching.interfaces import ICache
from evogrid.caching.ram import RAMCache
from evogrid.common.comparators import SimpleComparator
from evogrid.interfaces import IPool, IComparator
from evogrid.sharing.interfaces import ISharingAwareComparator, IDistance

_marker = object()

@implementer(IDistance)
def one_dim_distance(a, b):
    """Default dummy distance measure between two numericals

    Can get overridden by the constructor.
    """
    return abs(b - a)

class SharingAwareComparator(object):
    """Base adapter to use a pool as sharing context to build a
    SharingAwareComparator instance

    Can also adapt an existing comparator (instead of the default
    SimpleComparator instance).

    No memoization by default, this comparator can use RAM or
    memcached based memoization for better efficiency for the ``distance``
    method.
    """
    implements(ISharingAwareComparator)
    adapts(IPool, IComparator)

    def __init__(self, pool, comparator=None, distance=None, cache=None):
        """Build a sharing aware comparator

        Take a pool as sharing context
        """
        self._pool = pool

        if distance is None:
            distance = one_dim_distance
        if cache is not None:
            distance = MemoizedDistance(distance, cache)
        self._distance = distance

        if comparator is None:
            comparator = SimpleComparator()
        self._comparator = comparator

    def distance(self, rep1, rep2):
        """Compute the distance between two replicators
        """
        return self._distance(rep1.candidate_solution, rep2.candidate_solution)

    def share_evaluation(self, rep, context=None):
        """Simple shared evaluation

        Compute the average distance and multiply it by the original
        evaluation.
        """
        if context is None:
            context = self._pool
        if len(context) <= 1:
            return rep.evaluation
        sum = 0.0
        for rep2 in context:
            sum += self.distance(rep, rep2)
        return rep.evaluation * sum / (len(context) - 1)

    def _share(self, replicators):
        """Build copies of replicators with shared evaluations"""
        context = set(self._pool) - set(replicators)
        # simulate a temporary sharing context without the replicators
        # whose evaluations are to be shared: this is especially usefull for
        # replacers that want to compare replicators in a neutral way
        for rep in replicators:
            shared = rep.replicate()
            shared.evaluation = self.share_evaluation(rep, context=context)
            # embed the original replicator to be able to retrieve it later on
            shared._original_replicator = rep
            yield shared

    def cmp(self, rep1, rep2):
        """Compare copies of rep1 and rep2 whose evaluations got shared"""
        shared1, shared2 = self._share((rep1, rep2))
        return self._comparator.cmp(shared1, shared2)

    def max(self, replicators):
        """Apply the `max` method to shared copies of replicators"""
        max_shared = self._comparator.max(self._share(replicators))
        return max_shared._original_replicator


class MemoizedDistance(object):
    """Base implementation of a memoize wrapper"""
    implements(IDistance)
    adapts(IDistance, ICache)

    def __init__(self, distance, cache=None):
        self._distance = distance
        if cache is None:
            cache = RAMCache(max_entries=100)
        self._cache = cache
        self._key_common = {'function': distance.__name__}

    def __call__(self, x1, x2):
        key = self._key_common.copy()
        # sort the arguments to optimize the cache usage (distanced are
        # symmetric)
        key['args'] = tuple(sorted((x1, x2)))
        result = self._cache.query(key, _marker)
        if result is _marker:
            result = self._distance(x1, x2)
            self._cache.set(key, result)
        return result

