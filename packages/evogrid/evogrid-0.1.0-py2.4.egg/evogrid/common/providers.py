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
"""Tools to combine providers together

A provider implements a generator interface that gives IReplicator
implementations
"""

import random

from zope.interface import implements

from evogrid.interfaces import IMergingProvider

class RandomProvider(object):
    """Randomly provide a replicator from weighted list of providers"""
    implements(IMergingProvider)

    def __init__(self, providers, weights=None):
        # weights and providers are both properties whose update will update the
        # internal _scaled_providers datastructure. To avoid calling it twice,
        # we first set the inner _weights and then use the providers property to
        # update the datastructure
        self._weights = weights
        self.providers = providers

    def _updateWeightedProviders(self, providers, weights=None):
        if weights is None:
            weights = [1] * len(providers)
        assert (len(weights) == len(providers),
                'lengths of weights and providers not equals')
        self._scaled_providers = []
        sum  = 0.0
        for provider, weight in zip(providers, weights):
            sum += weight
            self._scaled_providers.append((provider, sum))
        self._total_weight = sum

    def _setProviders(self, providers):
        self._providers = providers
        self._updateWeightedProviders(providers, self.weights)

    def _getProviders(self):
        return self._providers

    providers = property(_getProviders, _setProviders)

    def _setWeights(self, weights):
        self._weights = weights
        self._updateWeightedProviders(self.providers, weights)

    def _getWeights(self):
        return self._weights

    weights = property(_getWeights, _setWeights)

    def next(self):
        cursor = random.uniform(0, self._total_weight)
        for provider, position in self._scaled_providers:
            if cursor < position:
                break
        return provider.next()

    def __iter__(self):
        return self


