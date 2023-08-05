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
"""Default pools implementations
"""
from itertools import chain

from zope.interface import implements
from zope.component import adapts
from pprint import PrettyPrinter

from evogrid.common.comparators import SimpleComparator
from evogrid.interfaces import IPool, IComparator, IProvider

# Pretty printer used for __repr__ methods to ease doctests readability
pformat = PrettyPrinter(width=74).pformat

#
# RAM based pools (non persistent)
#

class Pool(set):
    """Simple set based pool implementation"""
    implements(IPool)

    def remove(self, replicator):
        try:
            return set.remove(self, replicator)
        except KeyError, e:
            # recast KeyError into ValueError to comply with the IPool interface
            raise ValueError(e)

    def pop(self):
        try:
            return set.pop(self)
        except KeyError, e:
            # recast KeyError into ValueError to comply with the IPool interface
            raise ValueError(e)

    def __repr__(self):
        return "Pool(%s)" % pformat(list(self))


class OrderedPool(list):
    """Simple list based pool implementation"""
    implements(IPool)

    add = list.append

    def clear(self):
        del self[:]

    def pop(self):
        try:
            return list.pop(self)
        except IndexError, e:
            # recast IndexError into ValueError to comply with the IPool
            # interface
            raise ValueError(e)

    def remove(self, replicator):
        """Default list.remove uses '==' instead of physical equality"""
        to_remove = None
        for i, contained in enumerate(self):
            if contained is replicator:
                to_remove = i
                break
        if to_remove is not None:
            del self[to_remove]
        else:
            raise ValueError("%r not in pool" % replicator)

    def __repr__(self):
        return "OrderedPool(%s)" % pformat(list(self))

    def __contains__(self, replicator):
        """Default list.__contains__ tests '==' instead of physical equality"""
        for contained in self:
            if contained is replicator:
                return True
        return False


#
# Virtual (compound pools)
#

class UnionPool(object):
    """Virtual pool that behaves as the union of several back end pools

    A creation pool that is used to add new replicators if any can be provided
    as optional argument. If none is provided, the last backend pool is used
    for creations.
    """
    implements(IPool)

    def __init__(self, pools, creation_pool=None):
        self._pools = pools
        self._reversed_pools = reversed(pools)
        self._creation_pool = pools[-1]

    def add(self, replicator):
        self._creation_pool.add(replicator)

    def pop(self):
        for pool in self._reversed_pools:
            if len(pool):
                return pool.pop()
        # all backends are empty, use the last to trigger the exception
        return pool.pop()

    def remove(self, replicator):
        for pool in self._pools:
            if replicator in pool:
                return pool.remove(replicator)
        # no backend contains `replicator` use the last one to trigger the
        # exception
        return pool.remove(replicator)

    def clear(self):
        for pool in self._pools:
            pool.clear()

    def __len__(self):
        return reduce(int.__add__, (len(pool) for pool in self._pools))

    def __iter__(self):
        return chain(*self._pools)

    def __contains__(self, replicator):
        for pool in self._pools:
            if replicator in pool:
                return True
        return False

    def __repr__(self):
        return "UnionPool(%s)" % pformat(list(self._pools))


#
# Elite archive and provider adapter
#

class EliteArchive(object):
    """Weak elitism adapter that keeps only the best replicators in the pool

    Only replicators that are better or equivalent to existing are admitted in
    the elite archive. By adding a better individual into the archive, all
    other lower quality replicators are autmatically removed.
    """
    implements(IPool)
    adapts(IPool, IComparator)

    def __init__(self, pool=None, comparator=None):
        self._last_added = None
        self._comparator = comparator or SimpleComparator()
        if pool is None:
            pool = Pool()
        elif not IPool.providedBy(pool):
            pool = Pool(pool)

        # initialize the internal pool storage by respecting the EliteArchive
        # constraints (keep only the bests)
        replicators = list(pool)
        self._storage = pool
        self._storage.clear()
        for rep in replicators:
            self.add(rep)

    def add(self, rep):
        if self._last_added is not None:
            cmp_res = self._comparator.cmp(rep, self._last_added)
            if cmp_res < 0:
                # rep is not good enough: ignore it
                return
            if cmp_res > 0:
                # rep is the best replicator so far: clear the pool before
                # adding it
                self._storage.clear()
            for already_in in self._storage:
                if already_in == rep:
                    # a similar replicator is already in the archive:
                    # drop the new one
                    return
        self._last_added = rep
        self._storage.add(rep)

    def pop(self):
        return self._storage.pop()

    def remove(self, rep):
        return self._storage.remove(rep)

    def clear(self):
        self._last_added = None # reset to default cache
        return self._storage.clear()

    def __len__(self):
        return self._storage.__len__()

    def __iter__(self):
        return self._storage.__iter__()

    def __contains__(self, rep):
        return self._storage.__contains__(rep)

    def __repr__(self):
        return "EliteArchive(%s)" % pformat(list(self))


class ProviderFromEliteArchive(object):
    """Adapts an elite archive to plug it in a chain of adapters"""
    implements(IProvider)
    adapts(IProvider, IPool)

    def __init__(self, archive, provider):
        self._provider = provider
        self._archive = archive

    def next(self):
        rep = self._provider.next()
        self._archive.add(rep)
        return rep

    def __iter__(self):
        return self



