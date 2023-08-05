=================
Caching utilities
=================

:Author: Olivier Grisel <olivier.grisel@ensta.org>
:Description: This package holds tools to memoize method calls to optimize the
              performance of computer intensive methods such as evaluation
              functions for instance.

Cache implementation MUST all be thread-safe so that several threaded evolvers
can share the same cache instance in order to share memoized results.

.. sectnum::    :depth: 2
.. contents::   :depth: 2


RAM-based implementation
========================


The ICache interface
---------------------

The ``evogrid.caching`` module provides a set of utilities to make it easy to
plug caching strategies on CPU intensive components. Caching components must
implements the ``evogrid.caching.interfaces.ICache`` interface::

  >>> from zope.interface.verify import verifyClass
  >>> from evogrid.caching.interfaces import ICache

The simplest implementation is the ``RAMCache`` class that stores data in a
simple python dict::

  >>> from evogrid.caching.ram import RAMCache
  >>> verifyClass(ICache, RAMCache)
  True

Let us build an instance to test its API. By default the cache is empty and
its statistics are set to zero::

  >>> rc = RAMCache()
  >>> len(rc)
  0
  >>> (rc.hits, rc.misses)
  (0, 0)

By default the number of cached entries is not limited::

  >>> rc.max_entries is None
  True


Storing and retrieving entries in/from the cache
------------------------------------------------

Entries are stored in the cache by specifying a key as a dictionary of keywords
and values::

  >>> rc.set({'a': 1, 'b': 3}, 4)
  >>> len(rc)
  1
  >>> (rc.hits, rc.misses)
  (0, 0)

Entries can then get queried by specifying the wanted key::

  >>> rc.query({'a': 1, 'b': 3})
  4
  >>> len(rc)
  1
  >>> (rc.hits, rc.misses)
  (1, 0)

If the requested key is not stored in the cache, ``None`` is returned by
default::

  >>> rc.query({'not in': 'cache'}) is None
  True
  >>> (rc.hits, rc.misses)
  (1, 1)

One can also choose another default value instead of ``None``::

  >>> rc.query({'still not in': 'cache'}, 0)
  0
  >>> (rc.hits, rc.misses)
  (1, 2)


Invalidating cache entries
--------------------------

Let us add more data in the cache to show how invalidation works::

  >>> rc.set({'other': 'key'}, 'data for other key')
  >>> rc.set({'yet': 'again', 'another': 'key'}, 'data for yet another key')
  >>> rc.set({'a': 2, 'b': 3}, 5)
  >>> len(rc)
  4

  >>> rc.query({'yet': 'again', 'another': 'key'})
  'data for yet another key'

Invalidation can be done specifically by giving the key of the entry to
invalidate::

  >>> rc.invalidate({'yet': 'again', 'another': 'key'})
  >>> len(rc)
  3
  >>> rc.query({'yet': 'again', 'another': 'key'}) is None
  True

If no entry match the key, nothing happens::

  >>> rc.invalidate({'not': 'in cache'})
  >>> len(rc)
  3

One can also invalidate all the cache content at once by calling ``invalidate``
without giving a key::

  >>> rc.invalidate()
  >>> len(rc)
  0

The cache is then empty but its statistics remain unaffected by the
invalidation::

  >>> (rc.hits, rc.misses)
  (2, 3)


Limiting the number of stored entries
-------------------------------------

It is possible to prevent the cache to grow for ever by giving a bound for the
number of stored entries::

  >>> rc = RAMCache(max_entries=3)
  >>> rc.max_entries = 3

In that case, when adding more than ``max_entries`` objects to the cache, the
oldest entries are automatically discarded::

  >>> rc.set({'key': 1}, 1)
  >>> rc.set({'key': 2}, 4)
  >>> rc.set({'key': 3}, 9)
  >>> len(rc)
  3

  >>> rc.set({'key': 4}, 16)
  >>> len(rc)
  3
  >>> rc.query({'key': 1}) is None
  True

The ``RAMCache`` is even a little smarter than that since when it is full, it
tends to keep the entries that were accessed lastly. For instance suppose that
at some point ``{'key': 3}`` is accessed a lot but then ``{'key': 2}`` is
accessed once and then new keys are added old keys to be removed first::

  >>> rc.query({'key': 3})
  9
  >>> rc.query({'key': 3})
  9
  >>> rc.query({'key': 3})
  9
  >>> rc.query({'key': 2})
  4

By adding a new key, ``{'key': 4}`` will be removed first since it was never
accessed::

  >>> rc.set({'new': 'key'}, 'some data')
  >>> len(rc)
  3
  >>> rc.query({'key': 4}) is None
  True

Then it is ``{'key': 3}``'s turn since it is the new oldest accessed key (even if
it was accessed a lot some time ago)::

  >>> rc.set({'new new': 'key'}, 'some other data')
  >>> len(rc)
  3
  >>> rc.query({'key': 3}) is None
  True

``{'key': 2}`` is still inside cause it was accessed after ``{'key': 3}``::

  >>> rc.query({'key': 2})
  4

Memcached-based implementation
==============================

memcached_ is a TCP/IP server for sharing cached objects. ``EvoGrid`` provides
dedicated components to use a pool of memcached_ servers as caching backend.

To install memcached_ on a ``apt``-enable box (Debian, Ubuntu, ...) just do::

  $ sudo apt-get install memcached

For other platforms, please report to the memcached_ homepage for installation
instructions.

.. _memcached: http://www.danga.com/memcached/

Managing a pool of servers
--------------------------

The ``MemcachedServerManager`` component aims at making it easier to start and
stop memcached servers dedicated to an ``EvoGrid`` process::

  >>> from evogrid.caching.memcached import MemcachedServerManager
  >>> msm = MemcachedServerManager()

The manager stores the pid files of the running process in a dedicated
directory::

  >>> msm.pid_dir
  '/tmp/evogrid-...-memcached-pids'

By default, no server is running and thus this directory is empty::

  >>> import os
  >>> os.listdir(msm.pid_dir)
  []

To start a server, we need to specify the port number on which the server will
be listening on and optionally and IP address to restrict the requests to a
specific host. By default requests from any host are accepted. We can also
specify the maximum size of the cache in megabytes. By default this is set to
``64MB``::

  >>> msm.start(10100, maxsize=128)

In order to make that test work well, let us wait a bit for the server to come
up and running::

  >>> from time import sleep
  >>> sleep(0.01)

Let  us start a second server that only accept requests coming from localhost::

  >>> msm.start(10101, ip="127.0.0.1")
  >>> sleep(0.01)

One can check that the servers are launched by inspecting the pid directory::

  >>> os.listdir(msm.pid_dir)
  ['INDRR_ANY:10100.pid', '127.0.0.1:10101.pid']

Note that ``"INDRR_ANY"`` means that this server accept requests from any host.
One can also get the list of running servers directly::

  >>> msm.get_server_ports()
  [10100, 10101]

To stop a server, one just need to specify the port number::

  >>> msm.stop(10100)
  >>> os.listdir(msm.pid_dir)
  ['127.0.0.1:10101.pid']

By deleting the msm object itself, all running servers are shutdown and the
pid direcory is cleaned::

  >>> pid_dir = str(msm.pid_dir)
  >>> del msm
  >>> os.path.exists(pid_dir)
  False


Using MemcachedCache
--------------------

Now that we have an easy way to run memcached_ servers, let us use them. To do
so, we will need a dedicated component that implements the ``ICache`` interface
as we have seen it before with the ``RAMCache`` instance::

  >>> from evogrid.caching.memcached import MemcachedCache
  >>> verifyClass(ICache, MemcachedCache)
  True

In order to use that component we need a pool of memcached_ servers. Let us
build two of them as previously on localhost::

  >>> msm = MemcachedServerManager()
  >>> msm.start(10110) ; sleep(0.05)
  >>> msm.start(10111) ; sleep(0.05)

Let us build a tuple holding the ip/port of the servers we want to use as a
backend for our cache component::

  >>> servers = tuple("127.0.0.1:%d" % p for p in msm.get_server_ports())
  >>> servers
  ('127.0.0.1:10110', '127.0.0.1:10111')

We can now build our caching component::

  >>> mcc = MemcachedCache(servers)

One can also set the servers dynamically since the servers attribute is a
property that takes care of updating anything required dynamically::

  >>> mcc.servers = servers

This cache provides the same statistics as for the ``RAMCache`` instance::

  >>> len(mcc)
  0
  >>> (mcc.hits, mcc.misses)
  (0, 0)

One can also set the servers dynamically since the servers attribute is a
property that takes care of updating anything required dynamically::

  >>> mcc.servers = ('127.0.0.1:10111',)
  >>> len(mcc)
  0
  >>> (mcc.hits, mcc.misses)
  (0, 0)

Let us readd the two of them to resume our tests::

  >>> mcc.servers = servers


Storing and retrieving entries in/from the cache
------------------------------------------------

As previsously, entries are stored in the cache by specifying a key as a
dictionary of keywords and values::

  >>> mcc.set({'a': 1, 'b': 3}, 4)
  >>> len(mcc)
  1
  >>> (mcc.hits, mcc.misses)
  (0, 0)

Entries can then get queried by specifying the wanted key::

  >>> mcc.query({'a': 1, 'b': 3})
  4
  >>> len(mcc)
  1
  >>> (mcc.hits, mcc.misses)
  (1, 0)

If the requested key is not stored in the cache, ``None`` is returned by
default::

  >>> mcc.query({'not in': 'cache'}) is None
  True
  >>> (mcc.hits, mcc.misses)
  (1, 1)

One can also choose another default value instead of ``None``::

  >>> mcc.query({'still not in': 'cache'}, 0)
  0
  >>> (mcc.hits, mcc.misses)
  (1, 2)


Invalidating cache entries
--------------------------

Let us add more data in the cache to show how invalidation works::

  >>> mcc.set({'other': 'key'}, 'data for other key')
  >>> mcc.set({'yet': 'again', 'another': 'key'}, 'data for yet another key')
  >>> mcc.set({'a': 2, 'b': 3}, 5)
  >>> len(mcc)
  4

  >>> mcc.query({'yet': 'again', 'another': 'key'})
  'data for yet another key'

Invalidation can be done specifically by giving the key of the entry to
invalidate::

  >>> mcc.invalidate({'yet': 'again', 'another': 'key'})
  >>> len(mcc)
  3
  >>> mcc.query({'yet': 'again', 'another': 'key'}) is None
  True

If no entry match the key, nothing happens::

  >>> mcc.invalidate({'not': 'in cache'})
  >>> len(mcc)
  3

One can also invalidate all the cache content at once by calling ``invalidate``
without giving a key::

  >>> mcc.invalidate()

In this case this is a bit different from the ``RAMCache`` case since after
invalidation entries are still present in the cache but there are not returned
any more when asking for them. They will cleaned later on when adding new cache
entries::

  >>> len(mcc)
  3
  >>> mcc.query({'other': 'key'}) is None
  True
  >>> mcc.query({'a': 2, 'b': 3}) is None
  True

The cache is then empty but its statistics remain unaffected by the
invalidation::

  >>> (mcc.hits, mcc.misses)
  (2, 5)


Limiting the size of the cache
------------------------------

Please note that ``MemcachedCache`` does not have a ``max_entries`` attribute as
for the ``RAMCache`` instance::

  >>> getattr(mcc, 'max_entries', None) is None
  True

The memcached_ backends have a builtin maximum size and they take care of
removing entries when they reach that size according to their internal policy.


Caching computer intensive evolutionary components
==================================================

Some components have builtin support for memoization through the use of
``ICache`` implementations. The following introduces two such components: the
distance computation of a sharing aware comparator and the evaluator.


Memoizing distance computation for sharing
------------------------------------------

Sharing-enabled evolution makes the sharing aware comparators spend
their time computing the distance of candidate solutions to the other members
of some pool named the sharing context. By default they use a simple one
dimensional implementation of ``IDistance``::

  >>> from evogrid.sharing.interfaces import IDistance
  >>> from evogrid.sharing.comparators import one_dim_distance
  >>> verifyClass(IDistance, one_dim_distance)
  True

  >>> one_dim_distance(0, 3)
  3
  >>> one_dim_distance(3, 0)
  3
  >>> one_dim_distance(3, 3)
  0
  >>> one_dim_distance(2, -4)
  6

This distance component can then get adapted with a cache instance to a memoized
distance::

  >>> cache = RAMCache(max_entries=100)
  >>> from evogrid.sharing.comparators import MemoizedDistance
  >>> verifyClass(IDistance, MemoizedDistance)
  True

  >>> mdist = MemoizedDistance(one_dim_distance, cache)
  >>> mdist(0, 3)
  3
  >>> mdist(3, 0)
  3
  >>> mdist(3, 3)
  0
  >>> mdist(2, -4)
  6

Let us see how the cache behave::

  >>> cache.hits, cache.misses
  (1, 3)

We got one hit because the memoized distance exploit the symmetry implied by the
``IDistance`` interface and thus could guess that ``mdist(3, 0)`` yields the
same result as the previsously seen ``mdist(0, 3)``.

Of course, that would also work with a memcached_ client instead of a
``RAMCache`` instance::

  >>> mdist = MemoizedDistance(one_dim_distance, mcc)
  >>> mdist(0, 3)
  3
  >>> mdist(3, 0)
  3
  >>> mdist(3, 3)
  0
  >>> mdist(2, -4)
  6


Memoizing fitness evaluations
-----------------------------

The other use case for caching redundant computations is the fitness
evaluation step of any evolutionary algorithm. This step is usually
the most computer intensive part of an evolutionary loop and due to the
highly random nature of the variation components and depending on the
resolution of the search space, a given candidate solution can sometimes
get evaluated a high number of times. To avoid such waste let us see
how to plug a cache instance to any evaluator function ::

  >>> from evogrid.interfaces import IEvaluator
  >>> from evogrid.common.evaluators import MemoizedEvaluator, BaseEvaluator
  >>> verifyClass(IEvaluator, MemoizedEvaluator)
  True

Let us build a sample replicator class to test our memoizing adapter::

  >>> from zope.interface import implements
  >>> class SumEvaluator(BaseEvaluator):
  ...     implements(IEvaluator)
  ...     def compute_fitness(self, cs):
  ...         return sum(cs)
  ...
  >>> verifyClass(IEvaluator, SumEvaluator)
  True
  >>> se = SumEvaluator()

Let us test it on some replicators::

  >>> from evogrid.common.replicators import Replicator
  >>> replicators = [Replicator((0, 1, 2)),  Replicator((2, 0, 4)),
  ...                Replicator((5, -2, 2)), Replicator((2, 0, 4))]

  >>> [r.evaluation for r in replicators]
  [None, None, None, None]

  >>> for r in replicators:
  ...     se.evaluate(r)

  >>> [r.evaluation for r in replicators]
  [3, 6, 5, 6]

As you can see the ``(2, 0, 4)`` has been evaluated twice, let us see how
memoization handle this case by using a ``RAMCache`` instance::

  >>> cache = RAMCache()
  >>> mse = MemoizedEvaluator(se, cache)

Let us build new replicators instance to ensure that ``mse`` actually updates
their ``evaluation`` attribute::

  >>> replicators = [Replicator((0, 1, 2)),  Replicator((2, 0, 4)),
  ...                Replicator((5, -2, 2)), Replicator((2, 0, 4))]

  >>> [r.evaluation for r in replicators]
  [None, None, None, None]

  >>> for r in replicators:
  ...     mse.evaluate(r)

  >>> [r.evaluation for r in replicators]
  [3, 6, 5, 6]

Let us now check the state of the cache::

  >>> len(cache)
  3
  >>> cache.hits, cache.misses
  (1, 3)

This confirms the fact that the ``evaluate`` method has only be called once for
the ``(2, 0, 4)`` candidate solution.
