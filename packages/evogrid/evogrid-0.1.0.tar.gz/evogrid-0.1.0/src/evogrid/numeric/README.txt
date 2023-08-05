===================================
Numerical Optimization with EvoGrid
===================================

:Author: Olivier Grisel <olivier.grisel@ensta.org>
:Description: Components overview of the EvoGrid numeric package

This package hosts representation dependent components where candidate
solutions are assumed to be 1-dimensional arrays of numericals.

This packages requires the availability of numpy_ somewhere in your
``PYTHONPATH``. Plotting replicators further requires matplotlib_ installed  and
the local search optimizers wrap functions defined in the scipy_ library.

..  _numpy: http://numeric.scipy.org
..  _matplotlib: http://matplotlib.sourceforge.net/
..  _scipy: http://www.scipy.org/

.. sectnum::    :depth: 2
.. contents::   :depth: 2


Creating array based numeric replicators
========================================


The VectorReplicator
--------------------

Let us first introduce replicators that are specialised to host a vector
(``numpy.array`` with shape ``(n,)``) of numerical parameters as candidate
solution::

  >>> from evogrid.numeric.interfaces import IVectorReplicator
  >>> from evogrid.numeric.replicators import VectorReplicator
  >>> from zope.interface.verify import verifyClass, verifyObject
  >>> verifyClass(IVectorReplicator, VectorReplicator)
  True

The simplest numerical replicator is built from a list of floats::

  >>> rep = VectorReplicator(cs=[0.3, 0.2, 0.4])
  >>> rep
  VectorReplicator(cs=array([ 0.3,  0.2,  0.4]))

  >>> rep1 = rep.replicate()
  >>> rep1
  VectorReplicator(cs=array([ 0.3,  0.2,  0.4]))

  >>> rep1 is rep
  False

  >>> rep1.candidate_solution is rep.candidate_solution
  False

  >>> rep1.candidate_solution == rep.candidate_solution
  array([True, True, True], dtype=bool)


Using Hypercube domains
-----------------------

The ``VectorReplicator`` implements the ``IDomainedReplicator`` interface and
thus can accept a ``domain`` attribute to constrain its candidate solution::

  >>> from evogrid.interfaces import IDomainedReplicator
  >>> verifyClass(IDomainedReplicator, VectorReplicator)
  True

The domain logic is provided by the ``HyperCubeDomain`` class that implements
the ``IMinMaxDomain`` interface::

  >>> from evogrid.numeric.domains import HyperCubeDomain
  >>> from evogrid.numeric.interfaces import IMinMaxDomain
  >>> verifyClass(IMinMaxDomain, HyperCubeDomain)
  True

Let us build the hyper cube between ``[0., -1., 1.]`` and ``[10., 5., 13.]``::

  >>> dom = HyperCubeDomain([0., -1., 1.], [10., 5., 13.])
  >>> dom.min
  array([ 0., -1.,  1.])
  >>> dom.max
  array([ 10.,  5.,  13.])

The hypercube domain ensures any vector lies between a ``min`` and a ``max``
vector::

  >>> from numpy import array
  >>> array([0., 0., 2.]) in dom
  True
  >>> dom.ensure_belong(array([-2.,  12.,  2.]))
  array([ 0.,  5.,  2.])


Generating random replicators
-----------------------------

The ``evogrid.numeric.providers`` module defines a provider to randomly
generate replicators on some ``R^N`` hypercube using a uniform
distribution::

  >>> from evogrid.interfaces import IProvider
  >>> from evogrid.numeric.providers import UniformReplicatorGenerator
  >>> verifyClass(IProvider, UniformReplicatorGenerator)
  True

  >>> import numpy.random; numpy.random.seed(0)
  >>> generator = UniformReplicatorGenerator([-1., 0., 0.], [1., 2., 3.])

  >>> [generator.next() for i in xrange(3)]
  [VectorReplicator(cs=array([ 0.09762701,  1.43037873,  1.80829013]), ...),
   VectorReplicator(cs=array([ 0.08976637,  0.8473096 ,  1.93768234]), ...),
   VectorReplicator(cs=array([-0.12482558,  1.783546  ,  2.89098828]), ...)]

If min and max are not provided, no generator can get built::

  >>> UniformReplicatorGenerator()
  Traceback (most recent call last):
  ...
  ValueError: min and max must be specified

By default the ``UniformReplicatorGenerator`` creates an ``HyperCubeDomain``
instance that is given to all the generated replicators::

  >>> rep = generator.next()
  >>> rep
  VectorReplicator(cs=array([-0.23311696,  1.58345008,  1.58668476]),
                   dom=HyperCubeDomain([-1.0, 0.0, 0.0], [1.0, 2.0, 3.0]))
  >>> dom = rep.domain
  >>> verifyObject(IMinMaxDomain, dom)
  True
  >>> dom.min
  array([-1.,  0.,  0.])
  >>> dom.max
  array([ 1.,  2.,  3.])


Downgrading the numeric resolution
----------------------------------

It might be interesting in some situations (eg caching) to downgrade
the resolution of admissible candidate solutions so as to artificially
reduce the size of the search space. In order to do so it is possible
to use adapt the default domain with the ``ResolutionDowngraderDomain``
domain adapter::

  >>> from evogrid.numeric.domains import ResolutionDowngraderDomain
  >>> verifyClass(IMinMaxDomain, ResolutionDowngraderDomain)
  True

Let us adapt our previously built ``HyperCubeDomain`` domain instance to allow
10 divisions (``resolution=1``) between the ``min`` and the ``max``
values along each axis::

  >>> dom2 = ResolutionDowngraderDomain(dom)

We can now plug it in our previously built replicator ``rep``::

  >>> rep
  VectorReplicator(cs=array([-0.23311696,  1.58345008,  1.58668476]),
                   dom=HyperCubeDomain([-1.0, 0.0, 0.0], [1.0, 2.0, 3.0]))
  >>> rep.domain = dom2
  >>> rep
  VectorReplicator(cs=array([-0.2,  1.6,  1.5]),
      dom=ResolutionDowngraderDomain(HyperCubeDomain([-1.0, 0.0, 0.0],
                                                     [1.0, 2.0, 3.0]),
                                                     resolution=1))

The ``ResolutionDowngraderDomain`` adapter can adjust its strength thanks to
the ``resolution`` keyword argument (set to 1 by default)::

  >>> dom3 = ResolutionDowngraderDomain(HyperCubeDomain([-1.0, 0.0, 0.0],
  ...                                                   [1.0, 2.0, 3.0]),
  ...                                   resolution=2)

The ``resolution`` parameter represents the number of decimals for the
normalized values of the vector parameters between the lower and upper
bound of the domain.

We can then use our new domain as the default domain for generated
replicators as follows (the min and max values are guessed from the
domain)::

  >>> generator = UniformReplicatorGenerator(dom=dom3)
  >>> generator.next()
  VectorReplicator(cs=array([ 0.14,  1.86,  0.21]),
      dom=ResolutionDowngraderDomain(HyperCubeDomain([-1.0, 0.0, 0.0],
                                                     [1.0, 2.0, 3.0]),
                                     resolution=2))


Breeding numeric replicators
============================

Pure darwinian variators
------------------------

In order to breed numerical replicators, ``evogrid`` comes with two
classical darwinian operators, namely the ``GaussianMutator`` and
``BlendingCrossover`` both of which implements the ``IVariator``
interface. Let us start with the mutator::

  >>> from evogrid.interfaces import IVariator
  >>> from evogrid.numeric.variators import GaussianMutator
  >>> verifyClass(IVariator, GaussianMutator)
  True

The ``GaussianMutator`` as two operating modes: either you provide as single
(optional) float value for the ``scale`` parameter that will be used for all
dimensions or you specify an array of them::

  >>> numpy.random.seed(0) # make the tests independant of previous sections

  >>> dom4 = HyperCubeDomain([-1., 0., 0.], [1., 10., 10.])
  >>> dom4 = ResolutionDowngraderDomain(dom4, resolution=3)
  >>> rep = VectorReplicator(cs=[.2, 5.11, 3.87], dom=dom4)
  >>> rep.candidate_solution
  array([ 0.2 ,  5.11,  3.87])

  >>> gm = GaussianMutator(scale=0.2)
  >>> result = gm.combine(rep)
  >>> result == (rep,)
  True

  >>> rep.candidate_solution
  array([ 0.552,  5.19 ,  4.07 ])

In that first case the scale parameter was the same for all dimensions. Lets us
now decide we want to affect each dimension at a different strength by using an
array of scales::

  >>> gm = GaussianMutator(scales=[0., .1, 10.0])
  >>> result = gm.combine(rep)
  >>> result == (rep,)
  True

  >>> rep.candidate_solution
  array([  0.552,   5.41 ,  10.   ])

In is also possible to mutate each coefficient proportionally to the size of
the domain by using the ``DomainAwareGaussianMutator``, for instance, we can
set the strength to 15% of the size of the domain as follows::

  >>> from evogrid.numeric.variators import DomainAwareGaussianMutator
  >>> dagm = DomainAwareGaussianMutator(scale=0.15)
  >>> result = dagm.combine(rep)
  >>> result == (rep,)
  True

  >>> rep.candidate_solution
  array([ 0.258,  6.84 ,  9.77 ])

Apart from mutators, it is also possible to combine a pair of replicators using
the ``BlendingCrossover`` that builds two new replicators buy linearly combining
the ``candidate_solution`` of the parents::

  >>> from evogrid.numeric.variators import BlendingCrossover
  >>> verifyClass(IVariator, BlendingCrossover)
  True

  >>> blx = BlendingCrossover()
  >>> rep2 = VectorReplicator(cs=[0.1, 8.27, 2.11], dom=dom4)

  >>> result = blx.combine(rep, rep2)
  >>> result == (rep, rep2)
  True

  >>> rep.candidate_solution
  array([  0.328,   7.36 ,  10.   ])

  >>> rep2.candidate_solution
  array([ 0.03,  7.75,  0.51])

Note that the first and third columns of the combined replicators lie outside
the bounds of the parents cause the value of the combination coefficient vary
between ``beta_min=0.1`` and ``beta_max=1.5`` by default.


Embedding directed local search in a variator
---------------------------------------------

Components that implements the ``IVariator`` interface are not required to
behave as blind darwinian combinators. They can be made aware of the meaning of
life and try to change the replicators towards what they think it the best
direction in the search spaces.

To do so, ``evogrid.numeric.variators`` has several implementations of local
optimizers that are base on the `scipy.optimize`_ package. For instance let use
test the `BFGS optimizer`_ wrapped into an ``IVariator`` component::

  >>> from evogrid.numeric.variators import BfgsVariator
  >>> verifyClass(IVariator, BfgsVariator)
  True

..  _`scipy.optimize`: http://projects.scipy.org/scipy/scipy/browser/trunk/Lib/optimize/optimize.py
..  _`BFGS optimizer`: http://en.wikipedia.org/wiki/BFGS_method

In order to make that variator of what is good or what is bad, we need ask an
``IEvaluator`` component, for instance a De Jong test function::

  >>> from evogrid.numeric.dejong import DeJongEvaluator
  >>> f7 = DeJongEvaluator(7)

We can now build the BFGS variator by adapting the ``f7`` evaluator::

  >>> bfgs_f7_variator = BfgsVariator(f7)

Let us now generate some replicator to test ``bfgs_f7_variator`` on it::

  >>> rep = VectorReplicator(cs=[ 0.1 ,  1.44,  1.8 ], dom=dom3)
  >>> f7.evaluate(rep)
  >>> rep.evaluation
  0.44859488409406462

By calling the ``combine`` method, ``rep`` will get improved by applying
maximum 10 iterations of the BFGS algorithm::

  >>> combined = bfgs_f7_variator.combine(rep)
  >>> rep is combined[0]
  True

  >>> rep.candidate_solution
  array([ 0. ,  2. ,  1.8])

  >>> f7.evaluate(rep)
  >>> rep.evaluation
  -1.6649654896774422

Please note that such local search variators can naturally benefit from
memoized enabled replicators::

  >>> from evogrid.common.evaluators import MemoizedEvaluator
  >>> mf7 = MemoizedEvaluator(f7)
  >>> mbfgs_f7_variator = BfgsVariator(mf7)

  >>> combined = mbfgs_f7_variator.combine(rep)
  >>> rep is combined[0]
  True

  >>> rep.candidate_solution
  array([ 0. ,  2. ,  1.8])

  >>> mf7.evaluate(rep)
  >>> rep.evaluation
  -1.6649654896774422

  >>> mf7._cache.hits
  8

  >>> mf7._cache.misses
  28

Please refer to the `evogrid.caching`_ module documentation for details
on memoizing components.

..  _`evogrid.caching`: caching.html


