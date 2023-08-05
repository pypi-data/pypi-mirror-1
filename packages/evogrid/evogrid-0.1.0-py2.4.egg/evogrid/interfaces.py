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
"""Main component types for building Evolutionary Systems"""

from zope.interface import Interface, Attribute

#
# Replicators
#

class IReplicator(Interface):
    """A simple replicator

    A replicator is the base component of an evolutionary system::
     - it can get selected (or not) to get replicated according to some
       external critereas through a Selector
     - it can get combined with other replicators through a Variator
     - it encodes a candidate solution to some problem that can get evaluated
       through a computing unit
    """

    candidate_solution = Attribute(
        'Canditate solution to some learning problem')

    evaluation = Attribute(
        'Store the result of the last evaluation')

    def __eq__(other):
        """Test whether self and other have equal candidate_solution"""

    def replicate():
        """Perfect replication

        usually: `return copy.deepcopy(self)`
        """

class IDomainedReplicator(Interface):
    """A replicator with a domain attribute

    DomainedReplicator should always ensure their candidate_solution belong to
    their domain.
    """

    domain = Attribute('Domain for the candidate solution')


class IDomain(Interface):
    """Determine the domain of variation of a candidate_solution"""

    def __contains__(cs):
        """Tell whether or not candidate solution belongs to the domain"""

    def ensure_belong(cs):
        """Return the nearest candidate solution that belong to the domain"""


#
# Replicator source and storage
#

class IProvider(Interface):
    """Replicator provider that can be used as a generator/iterator"""

    def next():
        """Give one new replicator, to be used as a generator

        raise StopIteration when no more Replicators can be provided
        """

    def __iter__():
        """Iterate over provided replicators

        usually return `self` as `next` is already implemented. This make it
        possible to use IProvider implementations with the `itertools`
        combinators
        """

class IChainedProvider(IProvider):
    """Provider that uses an upstream source of replicators"""

    provider = Attribute("Upstream provider")

class IMergingProvider(IProvider):
    """Provider that uses several upstream sources of replicators"""

    providers = Attribute("Upstream sequence of providers")


class IPool(Interface):
    """Store replicators

    An IPool instance implements most of the standard python container types
    behaviors.
    """

    def add(replicator):
        """Add a new Replicator to the pool"""

    def pop():
        """Get one Replicator out of the pool and return it

        raise ValueError if pool is empty
        """

    def remove(replicator):
        """Get `replicator` out of the pool

        raise ValueError if replicator is not in pool

        ``replicator`` should be found by physical equality ('is' not '==').
        """

    def clear():
        """Empty the pool"""

    def __len__():
        """Number of Replicators inside the pool"""

    def __iter__():
        """Make it trivial to adapt a pool to a provider through the use of the
        `iter` builtin
        """

    def __contains__(replicator):
        """Python style containment

        Containment test should rely on physical equality ('is' not '==').
        """

#
# Quality evaluation
#

class IEvaluator(Interface):
    """Measure the fitness of replicators"""

    def compute_fitness(candidate_solution):
        """Return the score of a candidate solution"""

    def evaluate(replicator):
        """Update the ``evaluation`` of a replicator and return None"""


class IComparator(Interface):
    """Compare the quality of two replicators
    """

    def cmp(replicator1, replicator2):
        """Compare two replicators according to their evaluations and return::

            * -1 if evaluation1 < evaluation2
            *  1 if evaluation1 > evaluation2
            *  0 if evaluation1 == evaluation2
        """

    def max(replicators):
        """Return the replicator with maximum evaluation from a collection"""


#
# Selection and replacement
#

class ISelector(Interface):
    """A selector chooses replicators among a pool.

    ISelector implementation should not change the pool state by default.
    """
    def select_from(pool):
        """Select on replicator from `pool`

        `pool` is an IPool of evaluated replicators
        """


class IRemoverSelector(ISelector):
    """Same as ISelector but removes the selected replicator out of the pool
    """


class ICopierSelector(ISelector):
    """Same as ISelector but return a copy of the selected replicator
    so that modification done on the selected won't affect other components
    using the same replicator.
    """


class IReplacer(Interface):
    """A replacer selects replicators and push them back to the pool
    """

    number = Attribute("Number of replicators to pull out of the provider. "
                       "If set to 0, len(pool) will be used instead.")

    def replace(provider, pool):
        """Add some of the `replicators` back to the pool

        This is usually done by comparing existing replicators to the new ones.
        If `number` is not 0, try to replace `number` replicators pulled from
        the `provider` back to the pool. Otherwise, pull len(pool).
        """


#
# Operations on Replicators
#

class IVariator(Interface):
    """Combine one or more replicators to create one or more new replicators
    """
    number_to_combine = Attribute("Number of replicators to combine (>=1)")

    def combine(firstReplicator, *replicators):
        """Combine `number_to_combine` replicators into a tuple of replicators

        Original (input) replicators might get changed by the `combine`
        operation.
        """


#
# Computation control
#

class ICheckpointer(Interface):
    """Control the evolutionary process
    """

    def reset():
        """Reset internal state to prepare a new evolutionary process"""

    def should_stop():
        """Tell whether the stopping criterion is met or not"""

class ICounter(Interface):
    """Simple counter interface that is useful for some checkpointer
    implementations
    """
    count = Attribute('Access the current counter state')

    def increment(step=1):
        """Increment the internal counter by `step`"""

class IEvolver(Interface):
    """Management of the evolution of a pool of replicators
    """
    pool = Attribute("The pool of replicators managed by the evolver")

    archive = Attribute("Pool that gathers replicators the best evolved "
                        "replicators")

    provider = Attribute("A provider that can be used as alternative source "
                         "of replicators")

    def initialize_pool(provider, size=100):
        """Initialize the pool and archives with replicators from the provider

        Each replicator is evaluated before getting inserted.
        """

    def step():
        """Trigger one atomic step of evolution

        Usually this is a replacement operation such as a generational
        replacement or a single replicator replacement in case of stready-state
        evolution.

        Return False if the if the evolution should stop and True otherwise.
        """

    def run():
        """Launch the main loop till some checkpointer tells to stop"""

    def reset():
        """Reset the internal state (eg a checkpointer) to prepare a new run"""
