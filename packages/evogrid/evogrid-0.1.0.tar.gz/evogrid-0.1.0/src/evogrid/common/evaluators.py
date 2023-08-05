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
"""Adapters for evaluator components

As Evaluator components are highly representation dependent, no default
implementation is provided.

However, you will find here a default multi-adapter for the following scheme:
(IEvaluator, IProvider) -> IProvider
"""

from zope.interface import implements
from zope.component import provideAdapter, adapts

from evogrid.caching.interfaces import ICache
from evogrid.caching.ram import RAMCache
from evogrid.interfaces import IEvaluator
from evogrid.interfaces import IProvider

class BaseEvaluator(object):
    """Abstract class to provide default implementation for ``evaluate``"""

    def compute_fitness(self, cs):
        raise NotImplementedError

    def evaluate(self, rep):
        rep.evaluation = self.compute_fitness(rep.candidate_solution)


class ProviderFromEvaluator(object):
    """Default adapter to use evaluator with providers chains

    This uses a class that wraps a generator since generators are builtin python
    objects that do not support interface implementation.
    """

    implements(IProvider)
    adapts(IEvaluator, IProvider)

    def _buildGenerator(self, evaluator, provider):
        while True:
            replicator = provider.next()
            evaluator.evaluate(replicator)
            yield replicator

    def __init__(self, evaluator, provider):
        generator = self._buildGenerator(evaluator, provider)
        self._generator = generator

    def next(self):
        return self._generator.next()

    def __iter__(self):
        return self._generator

# Register ProviderFromEvaluator as default adapter
provideAdapter(ProviderFromEvaluator)

_marker = object()

class MemoizedEvaluator(BaseEvaluator):
    """Base implementation of a memoize wrapper

    The key used is built on the ``candidate_solution`` attribute of the
    replicator being evaluated.
    """
    implements(IEvaluator)
    adapts(IEvaluator, ICache)

    def __init__(self, evaluator, cache=None):
        self._evaluator = evaluator
        if cache is None:
            cache = RAMCache(max_entries=100)
        self._cache = cache
        self._key_common = {
            'class': evaluator.__class__.__name__,
            'method': 'evaluate',
        }

    def compute_fitness(self, cs):
        key = self._key_common.copy()
        key['cs'] = cs
        result = self._cache.query(key, _marker)
        if result is _marker:
            result = self._evaluator.compute_fitness(cs)
            self._cache.set(key, result)
            return result
        else:
            return result



