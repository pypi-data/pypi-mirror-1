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
"""Generic IEvolver implementations
"""
from itertools import islice
from threading import Thread
from zope.interface import implements

from evogrid.common.checkpointers import GenericProviderCheckpointer
from evogrid.common.comparators import SimpleComparator
from evogrid.common.evaluators import ProviderFromEvaluator
from evogrid.common.pools import (
    Pool, UnionPool, EliteArchive, ProviderFromEliteArchive)
from evogrid.common.providers import RandomProvider
from evogrid.common.selectors import (
    TournamentSelector, ProviderFromSelectorAndPool)
from evogrid.common.replacers import TournamentReplacer
from evogrid.common.variators import ProviderFromVariator

from evogrid.interfaces import ICopierSelector, IEvolver

#
# Self contained evolvers
#

class GenericEvolver(object):
    """Simple atomic evolver

    The behavior of the evolution if determined by the arguments provided
    at init time by building an internal providers chain that is used
    at each call to the ``step`` method.

    The following representation dependent components are required:
      - variators (sequence of IVariator implementation)
      - evaluator

    An additional provider is required for pool initialization when
    calling the ``initialize_pool`` method.

    All other components are optional.
    """
    implements(IEvolver)

    def __init__(self, variators, evaluator, comparator=None, selector=None,
                 replacer=None, pool=None, checkpointer=None, archive=None,
                 provider=None, external_prob=0.1):
        # initializing public components through their private counterpart to
        # avoid the property accessors to trigger the _update_provider_chain
        # method each time
        if pool is None:
            pool = Pool()
        self._pool = pool
        self._variators = variators
        self._evaluator = evaluator
        self._provider = provider
        self._external_prob = external_prob

        comparator = comparator or SimpleComparator()
        self._comparator = comparator

        selector = selector or TournamentSelector(comparator)
        # ensure the selector provides ICopierSelector in order to be more
        # threadsafe
        if not ICopierSelector.providedBy(selector):
            selector = ICopierSelector(selector)
        self._selector = selector

        self._replacer = replacer or TournamentReplacer(
            comparator=comparator, number=1)

        # XXX:make this clearer by defining an IArchiveAwareCheckpointer
        # interface with a property based archive attribute and testing it
        # explicitely instead of using getattr
        self._checkpointer = checkpointer or GenericProviderCheckpointer(
            maxcount=1000, maxsteadyness=150, comparator=comparator,
            archive=archive)
        self._archive = getattr(checkpointer, 'archive', archive)
        if self._archive is None:
            self._archive = EliteArchive(comparator=comparator)

        # build the final provider by adapting and chaining those components
        self._update_provider_chain()

    def _update_provider_chain(self):
        """(Re)build the final provider by adapting the component

        This method should be called any time one of the subcomponent get changed
        """
        # plug the selector and pool together
        p1 = ProviderFromSelectorAndPool(self._selector, self._pool)

        if self.provider is not None:
            # plug the external provider as an alternative source replicators
            p1_prob = 1.0 - self._external_prob
            p1 = RandomProvider((p1,         self._provider),
                                (p1_prob,    self._external_prob))
            # XXX: fallback if any is empty?

        # chain the variators
        p2 = p1
        for variator in self._variators:
            p2 = ProviderFromVariator(variator, p2)

        # plug the evaluators
        p3 = ProviderFromEvaluator(self._evaluator, p2)

        # ensure the archive gets updated when the chain is used
        self._provider_chain = ProviderFromEliteArchive(self._archive, p3)

    #
    # public attributes of the IEvolver interface
    #

    def _getArchive(self):
        return self._archive

    def _setArchive(self, archive):
        self._archive = archive
        self._update_provider_chain()

    archive = property(_getArchive, _setArchive)

    def _getPool(self):
        return self._pool

    def _setPool(self, pool):
        self._pool = pool
        self._update_provider_chain()

    pool = property(_getPool, _setPool)

    def _getProvider(self):
        return self._provider

    def _setProvider(self, provider):
        self._provider = provider
        self._update_provider_chain()

    provider = property(_getProvider, _setProvider)

    #
    # methods of the IEvolver interface
    #

    def initialize_pool(self, provider, size=100):
        self.pool.clear()
        self.archive.clear()
        for rep in islice(provider, size):
            self._evaluator.evaluate(rep)
            self.pool.add(rep)
            self.archive.add(rep)

    def step(self):
        if self._checkpointer.should_stop():
            return False
        else:
            self._replacer.replace(self._provider_chain, self.pool)
            return True

    def run(self):
        self.reset()
        while self.step():
            pass

    def reset(self):
        self._checkpointer.reset()


#
# Nested evolvers
#

class SequentialEvolver(object):
    """Compound evolver to sequentially simulate parallel evolution

    If an external provider is specified, it will be set as external provider
    for all the sub evolvers.
    """
    implements(IEvolver)

    def __init__(self, evolvers, provider=None):
        self._evolvers = tuple(evolvers)
        self._running = [True] * len(self._evolvers)

        self.pool = UnionPool([ev.pool for ev in evolvers])

        # XXX: this is not a true archive: the archive object should be made a
        # common instance but evolvers' attributes should me made properties
        # first (use zope.event there)
        self.archive = UnionPool([ev.archive for ev in evolvers])

        if provider is not None:
            self.provider = provider

    #
    # public attributes for the IEvolver interface
    #

    def _get_provider(self):
        return self._provider

    def _set_provider(self, provider):
        self._provider = provider
        for ev in self._evolvers:
            ev.provider = provider

    provider = property(_get_provider, _set_provider)

    # XXX: make them properties if needed
    pool, archive = None, None

    #
    # methods for the IEvolver interface
    #

    def initialize_pool(self, provider, size=100):
        """Initialize sub pools so that the sum of the sizes is ``size``

        Try to make the sub sizes as equal as possible.
        """
        len_evolvers = len(self._evolvers)
        base_size, remaining = divmod(size, len_evolvers)

        sizes = [base_size] * len_evolvers
        for i in xrange(remaining):
            sizes[i] += 1

        for ev, size in zip(self._evolvers, sizes):
            ev.initialize_pool(provider, size)

    def step(self):
        for i, ev in enumerate(self._evolvers):
            if not self._running[i]:
                continue
            self._running[i] = ev.step()
        return True in self._running

    def run(self):
        self.reset()
        while self.step():
            pass

    def reset(self):
        self._running = [True] * len(self._evolvers)
        for ev in self._evolvers:
            ev.reset()

#
# Parallel evolvers
#

class ThreadingEvolver(SequentialEvolver):
    """Compound evolver that relies on threads to parallelize evolution"""

    def _make_job(self, i, f):
        def job():
            self._running[i] = f()
        return job

    def step(self):
        threads = [(i, Thread(target=self._make_job(i, e.step)))
                   for i, e in enumerate(self._evolvers)]
        started_threads = []
        for i, t in threads:
            if not self._running[i]:
                continue
            t.start()
            started_threads.append(t)
        for t in started_threads:
            t.join()
        return True in self._running

    def run(self):
        self.reset()
        threads = [Thread(target=e.run) for e in self._evolvers]
        for t in threads:
            t.start()
        for t in threads:
            t.join()


# TODO: fork-based networked // evolution
