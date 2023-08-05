===================
Components overview
===================

:Author: Olivier Grisel <olivier.grisel@ensta.org>
:Description: General overview of interfaces used in the EvoGrid system

The EvoGrid design heavily relies upon the `Zope Component Architecture`_
(interfaces, components and adapters) to allow better code modularization
and reuse.
::

  >>> from zope import interface, component
  >>> from zope.interface.verify import verifyClass, verifyObject

The aim of using Zope's machinery is to be able to easily plug 3rd party
components without changing a line of the original code. The following
introduces the main component types of the EvoGrid system through their
interfaces by showing a sample implementation of the 5-OneMax problem.

.. sectnum::    :depth: 2
.. contents::   :depth: 2

..
    >>> from evogrid.interfaces import (
    ...     IReplicator,
    ...     IProvider,
    ...     IEvaluator,
    ...     IPool,
    ...     ISelector,
    ...     IVariator,
    ...     IReplacer,
    ...     ICheckpointer,
    ...     IEvolver,
    ... )

IReplicator
===========

Replicators are the building blocks of EvoGrid. They hold the candidate solution
to some problem whose solving involves some Machine Learning algorithms.

Let us create ``rep1`` and ``rep2``, both sample solutions to the 5-OneMax
problem::

    >>> from copy import deepcopy
    >>> class FiveIntRangeReplicator(object):
    ...
    ...     interface.implements(IReplicator)
    ...
    ...     candidate_solution = None
    ...     evaluation = None
    ...
    ...     def __init__(self, cs=(0, 0, 0, 0, 0)):
    ...         self.candidate_solution = cs
    ...
    ...     def replicate(self):
    ...         return deepcopy(self)
    ...
    ...     def __eq__(self, other):
    ...         return self.candidate_solution == other.candidate_solution
    ...
    ...     def __repr__(self):
    ...         return '<replicator with cs=%s>' % str(self.candidate_solution)
    ...
    >>> verifyClass(IReplicator, FiveIntRangeReplicator)
    True
    >>> rep1 = FiveIntRangeReplicator((0, 0, 1, 0, 1))
    >>> rep2 = FiveIntRangeReplicator((1, 0, 0, 0, 0))

The ``evaluation`` attribute which is set to ``None`` by default will be introduced
in the IEvaluator_ section.

The ``__repr__`` method is optional but helps make that documentation more
readeable.

What makes a replicator so interesting is its ability to replicate into another
replicator::

    >>> rep1prime = rep1.replicate()
    >>> rep1prime
    <replicator with cs=(0, 0, 1, 0, 1)>
    >>> verifyObject(IReplicator, rep1prime)
    True

The replicatee holds the same candidate solution, but is nevertheless
independent of its parent::

    >>> rep1prime.candidate_solution == rep1.candidate_solution
    True
    >>> rep1prime == rep1
    True
    >>> rep1prime is rep1
    False

IProvider
=========

Usually, we don't build our replicators manually but rather use dedicated
components. Those components typically implement the IProvider
interface. A replicator provider is just a standard source of replicators
with a generator interface (ie: the ``next`` and ``__iter__`` methods).

For instance the following class implements IProvider to randomly
generate Replicators whose ``candidate_solution`` attribute are potential
solutions to the 5-OneMax problem::

    >>> import random; random.seed(0) # reproducible tests
    >>> class RandomFiveIntReplicatorSource:
    ...     interface.implements(IProvider)
    ...     def next(self):
    ...         cs = tuple(random.randint(0, 1) for _ in range(5))
    ...         return FiveIntRangeReplicator(cs)
    ...     def __iter__(self):
    ...         return self
    ...
    >>> verifyClass(IProvider, RandomFiveIntReplicatorSource)
    True
    >>> random_generator = RandomFiveIntReplicatorSource()
    >>> rep3 = random_generator.next()
    >>> rep3
    <replicator with cs=(1, 1, 0, 0, 1)>
    >>> verifyObject(IReplicator, random_generator.next())
    True

IProvider implementations can also reuse some existing source of
replicators and modify them dynamically for instance by implementing a
client to some dedicated Web Service for instance (SOAP, XMLRPC, REST,
whatever, ...). If for some reason the replicator provider is unable to provide
the next object, it should raise ``StopIteration`` as standard python generators
do. This obviously won't be the case with our ``random_generator``.

Replicator providers can be chained using the zope adapters' machinery as
we will now see with evaluator components.

Note: the dummy ``__iter__`` implementations make ``IProvider`` implementation
behave like standard python iterators which make it possible to use the
functional combinators of the ``itertools`` module.

IEvaluator
==========

Evaluator components are simple objects which provide the
``compute_fitness`` and ``evaluate`` methods that take one replicator
and update its ``evaluation`` attribute according to the value of its
``candidate_solution`` attribute::

    >>> class OneMaxEvaluator:
    ...     interface.implements(IEvaluator)
    ...     def compute_fitness(self, cs):
    ...         return len([True for bit in cs if bit is 1])
    ...     def evaluate(self, replicator):
    ...         cs = replicator.candidate_solution
    ...         replicator.evaluation = self.compute_fitness(cs)
    ...
    >>> verifyClass(IEvaluator, OneMaxEvaluator)
    True
    >>> evaluator = OneMaxEvaluator()
    >>> (rep1.evaluation, rep1prime.evaluation,
    ...  rep2.evaluation, rep3.evaluation)
    (None, None, None, None)
    >>> evaluator.evaluate(rep1); evaluator.evaluate(rep1prime)
    >>> evaluator.evaluate(rep2); evaluator.evaluate(rep3)
    >>> (rep1.evaluation, rep1prime.evaluation,
    ...  rep2.evaluation, rep3.evaluation)
    (2, 2, 1, 3)

``evaluator.evaluate(rep)`` is often refered as the "fitness function" in the EC
literature.

Evaluator can get chained to replicator providers through the use of the
``ProviderFromEvaluator`` adapter which is registered by default for the
following interfaces::

    (IEvaluator, IProvider) -> IProvider

    >>> from evogrid.common.evaluators import ProviderFromEvaluator

For instance, let's adapt our new ``evaluator`` to the ``random_generator``
provider into and ``evaluated_generator`` component::

    >>> evaluated_generator = ProviderFromEvaluator(evaluator, random_generator)
    >>> verifyObject(IProvider, evaluated_generator)
    True
    >>> new_evaluated_rep = evaluated_generator.next()
    >>> new_evaluated_rep
    <replicator with cs=(1, 1, 0, 1, 1)>
    >>> new_evaluated_rep.evaluation
    4

IPool
=====

Replicators naturally live in a pool. The simplest pool is a just a slightly
extended python ``set`` that is declared to provide the IPool interface::

    >>> from evogrid.common.pools import Pool
    >>> verifyClass(IPool, Pool)
    True

However, to make the tests reproducible, we will build an ordered
pool which is based on the python ``list`` type so that lastly added
replicators appear always at list on pool iteration::

    >>> from evogrid.common.pools import OrderedPool
    >>> verifyClass(IPool, OrderedPool)
    True

Let us feed that pool manually::

    >>> pool = OrderedPool()
    >>> pool.add(rep1)
    >>> pool.add(rep1prime)
    >>> pool.add(rep2)
    >>> pool.add(rep3)
    >>> len(pool)
    4
    >>> [rep in pool for rep in (rep1, rep1prime, rep2, rep3)]
    [True, True, True, True]

We can also feed our pool with our ``evaluated_generator`` provider::

   >>> for i in range(16):
   ...     pool.add(evaluated_generator.next())
   >>> len(pool)
   20

The next sections introduces selectors which are components that will allow us
to adapt our new pool into a fancy replicator provider.

ISelector
=========

As Dawkins said, to get an (interesting) evolution we need three ingredients:

  - replication
  - selection
  - variation

We have previously seen how replicators replicate. We will now focus on
selection with the ISelector interface. Variation will come afterwards.

In ``EvoGrid``, selection is done by dedicated components that implements the
``ISelector`` interface. As selection operators are representation independent,
``evogrid`` provides implementations for the most common strategies in the
``evogrid.common.selectors`` module.

For instance, we can build a selector for our pool by randomly selecting
replicators::

    >>> random.seed(0) # make tests independent of previous sections

    >>> from evogrid.common.selectors import RandomSelector
    >>> verifyClass(ISelector, RandomSelector)
    True
    >>> random_selector = RandomSelector()
    >>> random_rep1 = random_selector.select_from(pool)
    >>> random_rep1
    <replicator with cs=(0, 1, 1, 1, 1)>

Note that the selected ``random_rep`` is still in ``pool``::

    >>> random_rep1 in pool
    True

This is the default behavior of ``ISelector`` implementations. This can be
changed by using the default adapters to the ``ICopierSelector`` and
``IRemoverSelector`` interfaces::

    >>> from evogrid.interfaces import ICopierSelector
    >>> from evogrid.interfaces import IRemoverSelector

Copier selectors return a copy of the replicator using its ``replicate``
method::

    >>> pool_len_before = len(pool)
    >>> random_rep2 = ICopierSelector(random_selector).select_from(pool)
    >>> random_rep2 in pool
    False
    >>> len(pool) == pool_len_before
    True

Remover selectors remove selected replicators out of the pool::

    >>> pool_len_before = len(pool)
    >>> random_rep3 = IRemoverSelector(random_selector).select_from(pool)
    >>> random_rep3 in pool
    False
    >>> len(pool) == pool_len_before - 1
    True

Other strategies are also available such as the Tournament strategy::

    >>> from evogrid.common.selectors import TournamentSelector
    >>> tournament_selector = ICopierSelector(TournamentSelector())

This selector randomly selects two replicators of the pool, compare their
respective evaluations and return a copy of the winner.

We can then adapt it to implement the IProvider interface thank to the
``ProviderFromEvaluator`` adaptor::

    >>> from evogrid.common.selectors import ProviderFromSelectorAndPool
    >>> verifyClass(IProvider, ProviderFromSelectorAndPool)
    True
    >>> tournament_provider = ProviderFromSelectorAndPool(tournament_selector,
    ...                                                   pool)
    >>> tournament_provider.next()
    <replicator with cs=(0, 1, 1, 1, 1)>

IVariator
=========

Variators are operators that change/combine one or more replicators to get one
or more resulting replicators in a tuple, possibly randomly::

    >>> random.seed(0) # make tests independent of previous sections


Mutators
--------

Our first variator takes one replicator and return a modified version of it.
Thus it can be considered a mutation operator::

    >>> class OneBitFlipperMutator:
    ...     interface.implements(IVariator)
    ...     number_to_combine = 1
    ...     def combine(self, *reps):
    ...         rep = reps[0]
    ...         cs = list(rep.candidate_solution)
    ...         position = random.choice(range(len(cs)))
    ...         cs[position] = int(not cs[position])
    ...         rep.candidate_solution = tuple(cs)
    ...         return (rep,)
    ...
    >>> verifyClass(IVariator, OneBitFlipperMutator)
    True

Applying our new mutator will return a slighty modified version of it::

    >>> rep1
    <replicator with cs=(0, 0, 1, 0, 1)>
    >>> flipper = OneBitFlipperMutator()
    >>> flipper.combine(rep1)
    ... # doctest: +ELLIPSIS
    (<replicator with cs=(0, 0, 1, 0, 0)>,)

Note that in our implementation, ``rep1`` itself has been modified by
``flipper``
and has now one bit difference with it replicatee ``rep1prime``::

    >>> rep1
    <replicator with cs=(0, 0, 1, 0, 0)>
    >>> rep1prime
    <replicator with cs=(0, 0, 1, 0, 1)>


Combinators
-----------

EC systems such as Genetic Programing systems often use higher level variators
that are able to combine several replicators in order to build new ones that
reuse part of the structure of their parents. Let us build such a crossing-over
operator for our 5-OneMax problem::

    >>> class BitWiseCrossOver:
    ...     interface.implements(IVariator)
    ...     number_to_combine = 2
    ...     def combine(self, *reps):
    ...          r1, r2 = reps
    ...          cs1, cs2  = [r.candidate_solution for r in reps]
    ...          cx = random.choice(range(len(cs1)))
    ...          r1.candidate_solution = cs1[:cx] + cs2[cx:]
    ...          r2.candidate_solution = cs2[:cx] + cs1[cx:]
    ...          return r1, r2
    ...
    >>> (rep2, rep3)
    (<replicator with cs=(1, 0, 0, 0, 0)>, <replicator with cs=(1, 1, 0, 0, 1)>)
    >>> cross_over = BitWiseCrossOver()
    >>> IVariator.providedBy(cross_over)
    True
    >>> cross_over.combine(rep2, rep3)
    ... # doctest: +ELLIPSIS
    (<replicator with cs=(1, 0, 0, 0, 1)>, <replicator with cs=(1, 1, 0, 0, 0)>)


Lamarckian evolution
--------------------

In the previous examples our variation operators have no idea of what a good
replicator means. This is the standard EC/darwinian approach where variation
operators are blind/dumb. Only the selection operators know what is a good
operators. EvoGrid however does not put any constraint on the design of
variators and it is up to the programmer to decide whether or not her variators
are made aware of what a good replicator is.

Variators can thus be used to embed local search algorithms that tries to
enhance parts of the candidate solution in a lamarckian perspective, eg::

    >>> class OneBitEnhancer:
    ...     interface.implements(IVariator)
    ...     number_to_combine = 1
    ...     def combine(self, *reps):
    ...         rep = reps[0]
    ...         cs = list(rep.candidate_solution)
    ...         if 0 in cs:
    ...             cs[cs.index(0)] = 1
    ...         rep.candidate_solution = tuple(cs)
    ...         return (rep,)
    ...
    >>> enhancer = OneBitEnhancer()
    >>> IVariator.providedBy(enhancer)
    True
    >>> rep4 = FiveIntRangeReplicator((1, 0, 0, 1, 0))
    >>> enhancer.combine(rep4)
    ... # doctest: +ELLIPSIS
    (<replicator with cs=(1, 1, 0, 1, 0)>,)


Chaining variators with providers
---------------------------------

Variators can easily be made part of a providers chain by using the
``evogrid.common.variators.ProviderFromVariator`` adapter which  is registered by
default. This is a multi-adapter that takes two args: a variator and a
provider::

    >>> from evogrid.common.variators import ProviderFromVariator
    >>> chained_variator = ProviderFromVariator(flipper, tournament_provider)
    >>> verifyObject(IProvider, chained_variator)
    True
    >>> chained_variator.next()
    <replicator with cs=(0, 1, 0, 1, 1)>

We can then chain all our variators by calling the adapters iteratively::

    >>> chained_variator = ProviderFromVariator(cross_over, chained_variator)
    >>> chained_variator = ProviderFromVariator(enhancer, chained_variator)

The final ``chained_variator`` component is a serial combination of the previous
components::

    pool -> tournament_selector -> flipper -> cross_over -> enhancer

As variators generally change the ``candidate_solution`` of replicators, we
usually plug an evaluator on the output so as to build an evaluated replicator
provider::

    >>> evaluated_provider = ProviderFromEvaluator(evaluator, chained_variator)
    >>> verifyObject(IProvider, evaluated_provider)
    True
    >>> rep = evaluated_provider.next()
    >>> rep
    <replicator with cs=(1, 0, 1, 1, 0)>
    >>> rep.evaluation
    3

IReplacer
=========

Replacers are similar to selectors but they put replicators back to some pool
instead. As selectors, replacers are representation independant. Some default
implementations are provided in the ``evogrid.common.replacers`` module::

    >>> from evogrid.common.replacers import TournamentReplacer
    >>> verifyClass(IReplacer, TournamentReplacer)
    True
    >>> replacer = TournamentReplacer(number=1)

Replacers have a ``replace(provider, pool)`` method that pull ``number``
replicators from the provider back to the pool. If ``number`` is left to
``None``, the it is automatically set to ``len(pool)``.

In order to measure how our replacer will affect our pool, we will use a
function that computes the average value of evaluations of replicators in the
pool::

    >>> def average_evaluation(pool):
    ...     return sum(float(rep.evaluation) for rep in pool) / len(pool)
    >>> average_evaluation(pool)
    2.9473684210526314
    >>> list(rep.evaluation for rep in pool)
    [2, 2, 1, 3, 4, 3, 3, 3, 1, 3, 2, 4, 5, 2, 2, 4, 4, 4, 4]

Let's try our replacer by replacing only one replicator by the generated
offspring::

    >>> replacer.replace(evaluated_provider, pool)
    >>> average_evaluation(pool)
    3.0
    >>> list(rep.evaluation for rep in pool)
    [2, 2, 1, 3, 4, 3, 3, 1, 3, 2, 4, 5, 2, 2, 4, 4, 4, 4, 4]

On this example, one of the replicator with a ``3`` has been replaced by the
one with score ``4`` at the end of the pool. By passing the ``number=1``
parameter to the constructor, we thus implement the class of "steady-state"
evolutionary algorithms.

By calling the same method with ``number`` set to ``0``, a whole new
generation of replicators will be generated an put back into the pool (as long
as they win the tournament at replacement time)::

    >>> replacer.number = 0
    >>> replacer.replace(evaluated_provider, pool)
    >>> average_evaluation(pool)
    3.7894736842105261
    >>> list(rep.evaluation for rep in pool)
    [2, 3, 4, 3, 1, 2, 5, 2, 4, 4, 4, 4, 5, 5, 4, 5, 5, 5, 5]

Which is already a bit better :) We can then run confidently our brand new
evolutionary algorithm till it converges to the optimal solution::

    >>> while average_evaluation(pool) < 5:
    ...    replacer.replace(evaluated_provider, pool)
    >>> list(rep.evaluation for rep in pool)
    [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]


IEvolver
========

In order to combine the previous components semi-automatically, the
``EvoGrid`` framework further provides reference implementations for the
``IEvolver`` interface.

Evolvers know how to make a pool evolve till it reaches some stopping criterion
that is defined by an embedded implementation of the ``ICheckpointer``
interface. Please refer to the ``evogrid.common.checkpointers`` module and tests
for more details on checkpointers.


Basic evolvers
--------------
::
    >>> random.seed(0) # make tests independent of previous sections


Let us first use the ``GenericEvolver`` class::

  >>> from evogrid.common.evolvers import GenericEvolver
  >>> verifyClass(IEvolver, GenericEvolver)
  True

This component requires arguments: a sequence of variators and an evaluator.
All other arguments are optional since they are representation independant::

  >>> from evogrid.common.pools import OrderedPool
  >>> variators = (flipper, cross_over)
  >>> evolver = GenericEvolver(variators, evaluator, pool=OrderedPool())

If not pool is provided, the evolver builds it's own pool and an archive that
will be used to store the best replicators it came to evolve. Both of them are
empty by default::

  >>> len(evolver.pool) == len(evolver.archive) == 0
  True

Let us initialise those pools with our previous
``RandomFiveIntReplicatorSource`` instance to initialize the pools before
launching the computation::

  >>> evolver.initialize_pool(random_generator, size=10)
  >>> [r.evaluation for r in evolver.pool]
  [3, 2, 4, 4, 3, 3, 3, 3, 1, 3]
  >>> [r.evaluation for r in evolver.archive]
  [4, 4]

We can now trigger one atomic step of evolution (a replacement step) which is a
steady-state replacement by default::

  >>> evolver.step()
  True
  >>> [r.evaluation for r in evolver.pool]
  [3, 2, 4, 4, 3, 3, 3, 3, 1, 3]
  >>> [r.evaluation for r in evolver.archive]
  [4, 4]

This step did not change the quality of the pool. Stepping a second time gives
the following::

  >>> evolver.step()
  True
  >>> [r.evaluation for r in evolver.pool]
  [3, 2, 4, 4, 3, 3, 3, 1, 3, 4]
  >>> [r.evaluation for r in evolver.archive]
  [4, 4, 4]

A replicator evaluated to ``3`` as been replaced to one of quality ``4`` which
has automatically been added to the elite archive.

We can also directly tell the evolver to run till it reaches some stopping
criterion (by default:maximum 500 steps from which 100 at maximum can be
triggered with no improvement in quality)::

  >>> evolver.run()
  >>> [r.evaluation for r in evolver.pool]
  [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
  >>> [r.evaluation for r in evolver.archive]
  [5]
  >>> evolver.step()
  False

Note that this could have been achieved with no pool argument but as the default
pool is not ordered, test details are not reproducibles::

  >>> evolver = GenericEvolver(variators, evaluator)
  >>> len(evolver.pool) == len(evolver.archive) == 0
  True

  >>> evolver.initialize_pool(random_generator, size=10)
  >>> len(evolver.pool)
  10

  >>> evolver.run()
  >>> [r.evaluation for r in evolver.archive]
  [5]
  >>> evolver.step()
  False


Pluggable evolvers
------------------
::
    >>> random.seed(0) # make tests independent of previous sections

An interesting thing about the ``GenericEvolver`` class is it's ability to pull
replicators from an external source of replicators that implements the
``IProvider`` interface. The following instance pulls one replicator out of two
from the ``random_generator`` instead of the it's on pool::

  >>> from itertools import islice
  >>> external_pool = OrderedPool(islice(random_generator, 10))
  >>> len(external_pool)
  10

  >>> selector =  IRemoverSelector(RandomSelector())
  >>> external_source = ProviderFromSelectorAndPool(selector, external_pool)
  >>> evolver = GenericEvolver(variators, evaluator, external_prob=0.5,
  ...                          provider=external_source)
  >>> evolver.initialize_pool(random_generator, size=10)
  >>> evolver.step()
  True
  >>> len(external_pool)
  8

  >>> evolver.step()
  True
  >>> len(external_pool)
  8

  >>> evolver.step()
  True
  >>> len(external_pool)
  6

This ability of ``GenericEvolver`` is especially interesting to plug several
evolvers together and thus allow for parallel evolution with migrations between
pools as we will see in the following section.


Nesting evolvers
----------------

The component based approach makes it quite easy to nest evolvers together
in order to perform nested evolution. For instance the ``SequentialEvolver``
class can combine sub-evolvers into a single component that also implements
the ``IEvolver`` interface so as to perform simulated parallel evolution::

  >>> from evogrid.common.evolvers import SequentialEvolver
  >>> subevolvers = [GenericEvolver(variators, evaluator, pool=OrderedPool())
  ...                for _ in xrange(3)]
  >>> evolver = SequentialEvolver(subevolvers)
  >>> evolver.pool
  UnionPool([OrderedPool([]), OrderedPool([]), OrderedPool([])])
  >>> [ev.pool for ev in subevolvers]
  [OrderedPool([]), OrderedPool([]), OrderedPool([])]

We can now initialize the pools with 9 replicators (3 replicators each)::

  >>> evolver.initialize_pool(random_generator, size=9)
  >>> evolver.pool
  UnionPool([OrderedPool([<replicator with cs=(1, 0, 0, 1, 0)>,
                          <replicator with cs=(0, 1, 0, 0, 0)>,
                          <replicator with cs=(1, 1, 0, 0, 0)>]),
             OrderedPool([<replicator with cs=(0, 0, 1, 0, 0)>,
                          <replicator with cs=(1, 0, 0, 1, 0)>,
                          <replicator with cs=(0, 1, 1, 1, 0)>]),
             OrderedPool([<replicator with cs=(1, 1, 0, 1, 1)>,
                          <replicator with cs=(0, 0, 1, 0, 0)>,
                          <replicator with cs=(0, 0, 1, 1, 0)>])])

To connect the sub evolvers together, we will update the ``provider`` attribute
of the global evolver with component that picks replicators randomly in the
aggregated pool. This will in turn update the ``provider`` attribute of each
sub evolver with the same component. Let us first build such a provider::

  >>> selector = ICopierSelector(RandomSelector())
  >>> external_provider = ProviderFromSelectorAndPool(selector, evolver.pool)
  >>> some_rep = external_provider.next()
  >>> some_rep
  <replicator with cs=(0, 0, 1, 0, 0)>

Note that ``some_rep`` is a copy of a replicator in third sub pool but does no
longer belong to the pools since is a copy::

  >>> some_rep in evolver.pool
  False
  >>> some_rep in subevolvers[2].pool
  False

Let us actually plug that provider::

  >>> evolver.provider = external_provider
  >>> [external_provider is ev.provider for ev in subevolvers]
  [True, True, True]

We can now run one step of evolution on the global evolver::

  >>> evolver.step()
  True
  >>> evolver.pool
  UnionPool([OrderedPool([<replicator with cs=(1, 0, 0, 1, 0)>,
                          <replicator with cs=(0, 1, 0, 0, 0)>,
                          <replicator with cs=(1, 1, 0, 0, 0)>]),
             OrderedPool([<replicator with cs=(1, 0, 0, 1, 0)>,
                          <replicator with cs=(0, 1, 1, 1, 0)>,
                          <replicator with cs=(0, 1, 1, 1, 0)>]),
             OrderedPool([<replicator with cs=(1, 1, 0, 1, 1)>,
                          <replicator with cs=(0, 0, 1, 0, 0)>,
                          <replicator with cs=(1, 1, 0, 1, 0)>])])

You can notice that the second and the third pools have evolved. The replacement
operation in the first pool must have failed.

Let us now directly jump to the end of the evolution by calling the ``run``
method on the global pool::

  >>> evolver.run()
  >>> evolver.step()
  False
  >>> evolver.pool
  UnionPool([OrderedPool([<replicator with cs=(1, 1, 1, 1, 1)>,
                          <replicator with cs=(1, 1, 1, 1, 1)>,
                          <replicator with cs=(1, 1, 1, 1, 1)>]),
             OrderedPool([<replicator with cs=(1, 1, 1, 1, 1)>,
                          <replicator with cs=(1, 1, 1, 1, 1)>,
                          <replicator with cs=(1, 1, 1, 1, 1)>]),
             OrderedPool([<replicator with cs=(1, 1, 1, 1, 1)>,
                          <replicator with cs=(1, 1, 1, 1, 1)>,
                          <replicator with cs=(1, 1, 1, 1, 1)>])])

This example implementation shows how to simulate a parallel
evolution by nesting evolvers with a sequential compound evolver. The
``evogrid.common.evolvers`` module also provide other `compound evolvers`_
that are able to perform true parallelization trough the use of threads
and forked networked processes and thus provide the opportunity to
achieve GRID-based evolutionary computing.

.. References:
..
.. _`Zope Component Architecture`: http://griddlenoise.blogspot.com/2005/12/zope-component-architecture-interfaces.html
.. _`compound evolvers`: evolvers.html
