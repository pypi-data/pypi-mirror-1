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
"""Classical selector implementations and adapters

Selectors take a IPool component as source and (sometimes probabilistically)
select the best out of them.

Selectors are representation independent w.r.t. the `candidate_solution` of the
replicators they select. They only care about their `evaluation`.

Default ISelector implementations should not change the pool object. It can be
useful however to remove the selected replicators out of the pool. Selectors
with such a behaviors implements the IRemoverSelector interface. A standard
adapter is registered by default in the in the selectors module that turns any
ISelector implementation into the corresponding IRemoverSelector.

Selectors choose evaluated replicators among pool of replicators. An evaluated
replicator has an `evaluation` attribute. Only selectors are able to tell
whether an evaluation is good or not.

Evaluations are often a single numerical attribute but they can also be more
complex such as a vector of numerical attributes. This can be useful for
multimodal optimization.

Selectors can easily get adapted to IProvider thanks to the ProviderFromSelector
adapter that is registered by default.
"""

import random

from zope import interface
from zope import component

from evogrid.common.comparators import SimpleComparator

from evogrid.interfaces import (IPool,
                                IProvider,
                                IComparator,
                                ISelector,
                                IRemoverSelector,
                                ICopierSelector,
                               )

#
# Abstract/base class
#

class BaseSelector(object):
    """Abstract class to hold a generic constructor for all selectors
    """

    def __init__(self, comparator=None):
        """Make it a potential IComparator adapter"""
        if comparator is None:
            comparator = SimpleComparator()
        self._cmp = comparator.cmp
        self._max = comparator.max

#
# Implementations of ISelector
#

class RandomSelector(BaseSelector):
    """Pick some replicators randomly ignoring their evaluation

    raise ValueError when the pool is empty
    """
    interface.implements(ISelector)
    component.adapts(IComparator)

    def select_from(self, pool):
        # Use `sample` instead of `choice` to work against non sequence pools
        [rep] = random.sample(pool, 1)
        return rep


class EliteSelector(BaseSelector):
    """Pick the base replicator of the pool

    raise ValueError when the pool is empty
    """
    interface.implements(ISelector)
    component.adapts(IComparator)

    def select_from(self, pool):
        if not len(pool):
            raise ValueError('Empty pool')
        return self._max(pool)


class TournamentSelector(BaseSelector):
    """Organise a tournament between `n` random members of the pool and select
    the winner

    raise ValueError when `n` is larger than the pool size
    """
    interface.implements(ISelector)
    component.adapts(IComparator)

    def __init__(self, comparator=None, n=2):
        BaseSelector.__init__(self, comparator)
        self._n = n

    def select_from(self, pool):
        participants = random.sample(pool, self._n)
        return self._max(participants)

# TODO: add here an implementation of the RouletteWheel selector where size of
# wheel sections are related to the rank of the replicators in the pool

#
# ISelector -> IRemoverSelector adapter
#

class RemoverSelector(object):
    """Adapter that transforms a base ISelector into it's IRemoverSelector
    counterpart

    Example: lets build a TournamentSelector that removes the selected
    replicator::

      >>> from zope.interface.verify import verifyObject
      >>> remover_tournament = RemoverSelector(TournamentSelector())
      >>> verifyObject(IRemoverSelector, remover_tournament)
      True

    As this class is register as an adapter by default you can also use it
    implicitely through it's interface::

      >>> remover_tournament2 = IRemoverSelector(TournamentSelector())
      >>> verifyObject(IRemoverSelector, remover_tournament2)
      True
    """
    interface.implements(IRemoverSelector)
    component.adapts(ISelector)

    def __init__(self, selector):
        self._selector = selector

    def select_from(self, pool):
        rep = self._selector.select_from(pool)
        pool.remove(rep)
        return rep

# Register the adapter
component.provideAdapter(RemoverSelector)


#
# ISelector -> ICopierSelector adapter
#

class CopierSelector(object):
    """Adapter that transforms a base ISelector into it's ICopierSelector
    counterpart

    Example: lets build a TournamentSelector that returns a copy of the selected
    replicator::

      >>> from zope.interface.verify import verifyObject
      >>> copier_tournament = CopierSelector(TournamentSelector())
      >>> verifyObject(ICopierSelector, copier_tournament)
      True

    As this class is register as an adapter by default you can also use it
    implicitely through it's interface::

      >>> copier_tournament2 = ICopierSelector(TournamentSelector())
      >>> verifyObject(ICopierSelector, copier_tournament2)
      True
    """
    interface.implements(ICopierSelector)
    component.adapts(ISelector)

    def __init__(self, selector):
        self._selector = selector

    def select_from(self, pool):
        rep = self._selector.select_from(pool)
        return rep.replicate()


# Register the adapter
component.provideAdapter(CopierSelector)


class ProviderFromSelectorAndPool(object):
    """Multi-adapter that transforms a selector and a pool into a provider::

       >>> from zope.interface.verify import verifyObject
       >>> fakepool = set()
       >>> tournament = TournamentSelector()
       >>> provider = ProviderFromSelectorAndPool(tournament, fakepool)
       >>> verifyObject(IProvider, provider)
       True
    """
    interface.implements(IProvider)
    component.adapts(ISelector, IPool)

    def __init__(self, selector, pool):
        self._selector = selector
        self._pool = pool

    def next(self):
        try:
            return self._selector.select_from(self._pool)
        except ValueError, e:
            raise StopIteration(str(e))

    def __iter__(self):
        return self


# Register the adapter
component.provideAdapter(ProviderFromSelectorAndPool)

