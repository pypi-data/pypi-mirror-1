=========================================
Multi Objective Optimization with EvoGrid
=========================================

:Author: Olivier Grisel <olivier.grisel@ensta.org>
:Description: Components overview to perform MOO with the EvoGrid system

`Multi Objective optimization`_ problems is a class of problems were
several conflicting criteria are to be optimized simultaneously. To make a
comparison with classical EC optimizations, the main difference is that we
have several `fitness` criteria that cannot be preferred to one another.

Meta heuristic techniques such as evolutionary computation are often
efficient approach to solve hard multi objective. This tutorial will
show dedicated components to address that class of problems.

.. sectnum::    :depth: 2
.. contents::   :depth: 2


Comparators
===========

Evogrid offers a variety of comparators that are able to deal with
vector evaluated replicators. All those MO-aware comparators implement
the following interface::

   >>> from evogrid.mo.interfaces import IMultiObjectiveComparator
   >>> from zope.interface.verify import verifyClass

Let us first build some replicators with a vector of two integers as
evaluation to test those comparator implementations::

    >>> from evogrid.common.replicators import Replicator
    >>> r00    = Replicator(ev=(0, 0))
    >>> r00bis = Replicator(ev=(0, 0))
    >>> r10    = Replicator(ev=(1, 0))
    >>> r11    = Replicator(ev=(1, 1))
    >>> r01    = Replicator(ev=(0, 1))


Lagrangian based comparator
---------------------------

The naive approach to multi-criterion comparison is to find compromise
by weighting each criterion according to it's relative importance.

This strategy can thus transforms a multi objective optimization problem
into a classical single objective optimization problem::

    >>> from evogrid.mo.comparators import WeightedSumComparator
    >>> verifyClass(IMultiObjectiveComparator, WeightedSumComparator)
    True

Let us assume the first criterion is twice as much as important as the second
one::

    >>> weigths = (2, 1)
    >>> wsc = WeightedSumComparator(weigths)
    >>> wsc.cmp(r00, r00bis)
    0
    >>> wsc.cmp(r10, r00)
    1
    >>> wsc.cmp(r00, r01)
    -1
    >>> wsc.cmp(r00, r11)
    -1
    >>> wsc.cmp(r01, r11)
    -1
    >>> wsc.cmp(r10, r01)
    1


Pareto dominance
----------------

``EvoGrid`` provides implementations for the classical Pareto dominance
relations in three flavours::

    >>> from evogrid.mo.comparators import WeakParetoComparator
    >>> from evogrid.mo.comparators import StrongParetoComparator
    >>> from evogrid.mo.comparators import RelaxedParetoComparator
    >>> verifyClass(IMultiObjectiveComparator, WeakParetoComparator)
    True
    >>> verifyClass(IMultiObjectiveComparator, StrongParetoComparator)
    True
    >>> verifyClass(IMultiObjectiveComparator, RelaxedParetoComparator)
    True


Weak Pareto dominance
~~~~~~~~~~~~~~~~~~~~~

We say that a vector v1 weakly Pareto-dominates another vector v2 if none of the
v2 coordinates is strictly greater than those in v1 and at least one the v1 is
stricly greater than its v2 counterpart. The ``WeakParetoComparator`` implements
the weak Pareto dominance::

    >>> wpc = WeakParetoComparator(vector_len=2)
    >>> wpc.cmp(r00, r00bis)
    0
    >>> wpc.cmp(r10, r00)
    1
    >>> wpc.cmp(r00, r01)
    -1
    >>> wpc.cmp(r00, r11)
    -1
    >>> wpc.cmp(r01, r11)
    -1
    >>> wpc.cmp(r10, r01)
    0

Pareto comparators also support using custom comparison functions for each
criterion evaluation. In the following example, the second criterion is to be
minimised whereas the first is still to be maximised::

    >>> my_cmp_funcs = (cmp, lambda x, y: -cmp(x, y))
    >>> wpc2 = WeakParetoComparator(cmp_funcs=my_cmp_funcs)
    >>> wpc2.cmp(r00, r00bis)
    0
    >>> wpc2.cmp(r10, r00)
    1
    >>> wpc2.cmp(r00, r01)
    1
    >>> wpc2.cmp(r00, r11)
    0
    >>> wpc2.cmp(r01, r11)
    -1
    >>> wpc2.cmp(r10, r01)
    1

This can also be useful if we want to mask (ignore) some criterion in the
evaluation vecto. In the following we ignore the second criterion and thus we
get the classical comparison on the first one::

    >>> wpc3 = WeakParetoComparator(vector_len=2, mask=(True, False))
    >>> wpc3.cmp(r00, r00bis)
    0
    >>> wpc3.cmp(r10, r00)
    1
    >>> wpc3.cmp(r00, r01)
    0
    >>> wpc3.cmp(r00, r11)
    -1
    >>> wpc3.cmp(r01, r11)
    -1
    >>> wpc3.cmp(r10, r01)
    1

Please also note that the Pareto-based comparators need at least the
``vector_len`` or a list of custom ``cmp_funcs`` at init time::

    >>> WeakParetoComparator()                            # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ParetoComparator need at least vector_len or cmp_funcs at init...


Strong Pareto dominance
~~~~~~~~~~~~~~~~~~~~~~~

``EvoGrid`` also provides an implementation of the strong Pareto-dominance
where all components of the dominant vector are strictly greater than their
counterpart. The initialization of a ``StrongParetoComparator`` instance
follows the same rules as for the ``WeakParetoComparator`` class::

    >>> spc = StrongParetoComparator(vector_len=2)
    >>> spc.cmp(r00, r00bis)
    0
    >>> spc.cmp(r10, r00)
    0
    >>> spc.cmp(r00, r01)
    0
    >>> spc.cmp(r00, r11)
    -1
    >>> spc.cmp(r01, r11)
    0
    >>> spc.cmp(r10, r01)
    0

As you can see this comparison scheme is often not able to decide which
vector is better. If this occurs, it might be a good idea to use the
``WeakParetoComparator`` instead or even a relaxed version of the
Pareto-dominance.


Relaxed Pareto dominance
~~~~~~~~~~~~~~~~~~~~~~~~

TODO


Fitness sharing
~~~~~~~~~~~~~~~

TODO



MO aware evolvers
=================

Most evolutionary loops (pool, selection, variation, evaluation, replacement)
built for single can get adapted in a few steps to work in a MO setting:

  - make the selection and replacement operators use a comparator that provides
    the ``IMultiObjectiveComparator`` interface instead of just ``IComparator``

  - make the evaluation component generate a vector of fitness values instead of
    a single scalar.

It might also be interesting to make the ``EliteArchive`` use a
``FitnessSharingAwareComparator`` instance in order to get a widely spread
approximation of the Pareto Optimal Set.

.. References:
..
..  _`multi objective optimization`: http://www.calresco.org/lucas/pmo.htm
