=======
Sharing
=======

:Author: Olivier Grisel <olivier.grisel@ensta.org>
:Description: Introduction to the sharing implementation in EvoGrid

.. sectnum::    :depth: 2
.. contents::   :depth: 2

What is sharing and why is it useful?
=====================================

"Sharing" is a common EC strategy to avoid early convergence to local optima on
deceptive problems and thus enhance the explanatory power of an EC-based search.

Sharing is biologically inspired after the concept of `ecological niches`_: when
individuals of an ecosystem share the same resources to survive (eg food),
groups of individuals tend to split themselves into subgroups to find several
hotspots instead of remaining similar and exhausting the source food they find.

In order to better explain what the problem is, let us take an example. Suppose
the search space is the range of integers ``range(30)`` (from ``0`` to ``29``). The
goal of this sample optimization problem is to find the value ``x in range(30)``
such that ``fitness(x)`` is maximum, where ``fitness`` is defined as follows::

  >>> from math import cos, sin, pi
  >>> def fitness(x):
  ...     return abs(40*cos(0.4*(x-5)/pi)+40*sin(0.5*(x-5)/pi))

This function is deceptive: a gradient search that would start in ``range(0, 21)``
would end up at the local maximum at ``x=11`` with ``fitness(11)=61.5`` whereas
the global maximum lies at ``x=29`` with ``fitness(29)=64.9``. Only gradients
searches that starts in ``range(22, 30)`` would be able to find it.

In order to make this clear, let's plot the fitness landscape::

  >>> def plot(func):
  ...     for i in range(30):
  ...         print '%02d' % i, '#' * int(func(i))
  ...
  >>> plot(fitness)
  00 ###
  01 ###########
  02 ##################
  03 ##########################
  04 #################################
  05 ########################################
  06 ##############################################
  07 ###################################################
  08 #######################################################
  09 ##########################################################
  10 ############################################################
  11 #############################################################
  12 #############################################################
  13 ###########################################################
  14 ########################################################
  15 ###################################################
  16 ##############################################
  17 #######################################
  18 ###############################
  19 #######################
  20 ##############
  21 ####
  22 #####
  23 ###############
  24 #########################
  25 ##################################
  26 ###########################################
  27 ###################################################
  28 ##########################################################
  29 ################################################################

Thus a randomly starting grandient search strategy as around twice as more
chances to get stuck at ``x=11`` than to find ``x=29``.

Let us build a simple evolutionary algorithm to solve this problem. Replicators
are simple object that stores the ``x`` value as candidate solution::

  >>> from evogrid.common.replicators import Replicator

The evaluator just applies the fitness function to replicators' candidate
solutions::

  >>> from zope.interface import implements
  >>> from evogrid.interfaces import IEvaluator
  >>> class Evaluator:
  ...     implements(IEvaluator)
  ...     def evaluate(self, rep):
  ...         rep.evaluation = fitness(rep.candidate_solution)
  >>> evaluator = Evaluator()

Let us check the values of the two optima::

  >>> rep11 = Replicator(cs=11)
  >>> evaluator.evaluate(rep11)
  >>> rep11.evaluation
  61.535462868213457

  >>> rep29 = Replicator(cs=29)
  >>> evaluator.evaluate(rep29)
  >>> rep29.evaluation
  64.946186039309566

Let us build a simple pool (ordered to make the tests reproducible)::

  >>> from evogrid.common.pools import OrderedPool
  >>> pool = OrderedPool()
  >>> pool
  OrderedPool([])

We will now initialize it randomly, with 4 replicators::

  >>> import random; random.seed(0) # reproducible tests
  >>> for i in random.sample(range(30), 4):
  ...    rep = Replicator(cs=i)
  ...    evaluator.evaluate(rep)
  ...    pool.add(rep)
  >>> pool
  OrderedPool([Replicator(cs=25, ev=34.783165260596739),
   Replicator(cs=22, ev=5.4864467971737767),
   Replicator(cs=12, ev=61.037356626492723),
   Replicator(cs=7, ev=51.22855381065461)])

Let us now improve our plotting function to track the evolution of our
replicators on the fitness landscape::

  >>> def plot_pool(func, pool):
  ...     for i in range(30):
  ...         n_rep = len([r for r in pool if r.candidate_solution == i])
  ...         print '%02d' % i, '#' * int(func(i)) + '[*]' * n_rep

So, our initial state looks like::

  >>> plot_pool(fitness, pool)
  00 ###
  01 ###########
  02 ##################
  03 ##########################
  04 #################################
  05 ########################################
  06 ##############################################
  07 ###################################################[*]
  08 #######################################################
  09 ##########################################################
  10 ############################################################
  11 #############################################################
  12 #############################################################[*]
  13 ###########################################################
  14 ########################################################
  15 ###################################################
  16 ##############################################
  17 #######################################
  18 ###############################
  19 #######################
  20 ##############
  21 ####
  22 #####[*]
  23 ###############
  24 #########################
  25 ##################################[*]
  26 ###########################################
  27 ###################################################
  28 ##########################################################
  29 ################################################################

To build our sample algorithm, we will use the following variators. First will
build an helper function that ensures the replicators stay in ``range(30)``::

  >>> def ensure_constraints(rep):
  ...    if rep.candidate_solution > 29:
  ...        rep.candidate_solution = 29
  ...    elif rep.candidate_solution < 0:
  ...        rep.candidate_solution = 0
  ...    return rep
  >>> ensure_constraints(Replicator(cs=32)).candidate_solution
  29
  >>> ensure_constraints(Replicator(cs=-6)).candidate_solution
  0

We now use it to build a simple mutator that moves replicators by maximum two
unit steps in the search space::

  >>> from evogrid.interfaces import IVariator
  >>> class Mutator:
  ...     implements(IVariator)
  ...     number_to_combine = 1
  ...     def combine(self, *reps):
  ...         rep = reps[0]
  ...         rep.candidate_solution += random.choice((-2, -1, 0, 1, 2))
  ...         return (ensure_constraints(rep),)
  >>> mutator = Mutator()
  >>> mutator.combine(Replicator(cs=12))
  (Replicator(cs=12),)
  >>> mutator.combine(Replicator(cs=12))
  (Replicator(cs=12),)
  >>> mutator.combine(Replicator(cs=12))
  (Replicator(cs=13),)

And similarly we define a sample combinator::

  >>> class Combinator:
  ...     implements(IVariator)
  ...     number_to_combine = 2
  ...     def combine(self, *reps):
  ...         rep1, rep2 = reps
  ...         cs1, cs2 = rep1.candidate_solution, rep2.candidate_solution
  ...         return (Replicator(cs=(cs1+cs2)/2),)
  >>> combinator = Combinator()
  >>> combinator.combine(Replicator(cs=5), Replicator(cs=10))
  (Replicator(cs=7),)

Will now build a simple providers chains by pluggin those components with a
standard TournamentSelector on the pool. First the selector::

  >>> from evogrid.interfaces import ICopierSelector
  >>> from evogrid.common.selectors import (TournamentSelector,
  ...                                       ProviderFromSelectorAndPool)
  >>> selector = ICopierSelector(TournamentSelector())
  >>> provider = ProviderFromSelectorAndPool(selector, pool)

Then the variators::

  >>> from evogrid.common.variators import ProviderFromVariator
  >>> m_provider = ProviderFromVariator(mutator, provider)
  >>> c_provider = ProviderFromVariator(combinator, provider)

We randomly choose between both through a probabilistical combination of both::

  >>> from evogrid.common.providers import RandomProvider
  >>> provider = RandomProvider((m_provider, c_provider))

Then the previously built evalutator::

  >>> from evogrid.common.evaluators import ProviderFromEvaluator
  >>> provider = ProviderFromEvaluator(evaluator, provider)

We can now combine the resulting provider with a TournamentReplacer to close the
evolutionary loop::

  >>> from evogrid.common.replacers import TournamentReplacer
  >>> replacer = TournamentReplacer(number=1)

We can now make our pool evolve in a steady-state manner till it reaches a
stable state::

  >>> for _ in range(100):
  ...    replacer.replace(provider, pool)
  >>> plot_pool(fitness, pool)
  00 ###
  01 ###########
  02 ##################
  03 ##########################
  04 #################################
  05 ########################################
  06 ##############################################
  07 ###################################################
  08 #######################################################
  09 ##########################################################
  10 ############################################################
  11 #############################################################[*][*][*][*]
  12 #############################################################
  13 ###########################################################
  14 ########################################################
  15 ###################################################
  16 ##############################################
  17 #######################################
  18 ###############################
  19 #######################
  20 ##############
  21 ####
  22 #####
  23 ###############
  24 #########################
  25 ##################################
  26 ###########################################
  27 ###################################################
  28 ##########################################################
  29 ################################################################

This example emphasizes the early convergence of the population to a single
locally optimal area of the fitness landscape. The area near ``x=29`` has been
completely neglected by the evolutionary compuation.

By sharing selective advantage of similar candidate solutions, we can give more
incentive to replicators that "explore" original and potentially interesting
areas of the fitness landscape.


How to implement Sharing-managed evolutionary process in EvoGrid?
=================================================================

In order to implement the same evolutionary chain with sharing enabled, only
the comparator step that is implicitly embedded in the selection steps needs
change through the use of a sharing aware comparator::

  >>> from evogrid.sharing.comparators import SharingAwareComparator
  >>> sharing_comparator = SharingAwareComparator(pool)
  >>> selector2 = TournamentSelector(comparator=sharing_comparator)
  >>> selector2 = ICopierSelector(selector2)
  >>> replacer2 = TournamentReplacer(comparator=sharing_comparator, number=1)

The rest of the chain is built the same way as previously::

  >>> provider = ProviderFromSelectorAndPool(selector2, pool)
  >>> m_provider = ProviderFromVariator(mutator, provider)
  >>> c_provider = ProviderFromVariator(combinator, provider)
  >>> provider = RandomProvider((m_provider, c_provider))
  >>> provider = ProviderFromEvaluator(evaluator, provider)

Before starting our new evolution, we need reset the pool is the same state it
was previously::

  >>> pool.clear()
  >>> random.seed(0) # reproducible tests
  >>> for i in random.sample(range(30), 4):
  ...    rep = Replicator(cs=i)
  ...    evaluator.evaluate(rep)
  ...    pool.add(rep)
  >>> pool
  OrderedPool([Replicator(cs=25, ev=34.783165260596739),
   Replicator(cs=22, ev=5.4864467971737767),
   Replicator(cs=12, ev=61.037356626492723),
   Replicator(cs=7, ev=51.22855381065461)])

We can now make our pool evolve again::

  >>> for _ in range(100):
  ...    replacer2.replace(provider, pool)
  >>> plot_pool(fitness, pool)
  00 ###
  01 ###########
  02 ##################
  03 ##########################
  04 #################################
  05 ########################################
  06 ##############################################
  07 ###################################################
  08 #######################################################[*]
  09 ##########################################################
  10 ############################################################[*]
  11 #############################################################
  12 #############################################################
  13 ###########################################################
  14 ########################################################
  15 ###################################################
  16 ##############################################
  17 #######################################
  18 ###############################
  19 #######################
  20 ##############
  21 ####
  22 #####
  23 ###############
  24 #########################
  25 ##################################
  26 ###########################################
  27 ###################################################
  28 ##########################################################
  29 ################################################################[*][*]

That gives a much better exploration of interesting areas of the fitness
landscape and thus a better resilience to deceptive optimization problems.

.. References:
..
.. _`ecological niches`: http://en.wikipedia.org/wiki/Ecological_niche
