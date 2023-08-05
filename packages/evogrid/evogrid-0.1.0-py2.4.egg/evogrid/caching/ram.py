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
"""RAM-based cache implementation

This RAM cache is inspired on zope.app.cache.ram but a bit simpler cause we
don't want to inherit from ``Persistent`` and has a slightly different
interface as well.

The original implementation of RAMCache is copyright Zope Corporation and
contributors and is distributed under the terms of the Zope Public License.
"""

from cPickle import dumps
from evogrid.caching.interfaces import ICache
from threading import Lock
from zope.interface import implements

_marker = object()

class RAMCache(object):
    """Cache implementation that stores entries in a python dict"""
    implements(ICache)

    hits = 0

    misses = 0

    max_entries = None

    def __init__(self, max_entries=None):
        self.max_entries = max_entries
        self._store = {}
        self._sorted_keys = [] # keys the more accessed are first
        self._lock = Lock()

    def __len__(self):
        return len(self._store)

    def invalidate(self, key=None):
        if key is None:
            self._lock.acquire()
            try:
                self._store.clear()
                del self._sorted_keys[:]
            finally:
                self._lock.release()
        else:
            key = self._buildKey(key)
            if not key in self._store:
                # optim: test to avoid lock acquisition if not necessary
                return
            self._lock.acquire()
            try:
                if key in self._store:
                    del self._store[key]
                    self._sorted_keys.remove(key)
                    # key should appear only once in that list
            finally:
                self._lock.release()

    def query(self, key, default=None):
        """Search the store to find a matching entry

        If nothing is found return default. If a matching entry is found,
        the _sorted_keys list order is updated. The misses and hits counters
        are updated.
        """
        key = self._buildKey(key)
        _store, _sorted_keys = self._store, self._sorted_keys
        result = _store.get(key, _marker)
        if result is _marker:
            # no need to acquire the lock if the result is not found
            self.misses += 1
            return default

        # a matching entry was found, we need to acquire the lock to update the
        # keys order

        self._lock.acquire()
        try:
            # need to retest the presence of the key after lock acquisition
            if key in _store:
                # put that key in the first position
                _sorted_keys.remove(key)
                _sorted_keys.insert(0, key)
        finally:
            self._lock.release()

        self.hits += 1
        return result

    def set(self, key, data):
        """Add data to the store

        Check that the store size does not exceed ``max_entries``.
        """
        key = self._buildKey(key)
        _store, _sorted_keys = self._store, self._sorted_keys

        if key in _store and _store[key] == data:
            # optim to avoid lock acquisition if not necessary
            return
        self._lock.acquire()
        try:
            if key not in _store:
                # the containment test with lock acquisition is mandatory
                # to avoid sorting the key twice

                # check that the store is not too big
                len_self = len(self)
                max_entries = self.max_entries
                if (max_entries is not None and len_self >= max_entries):
                    for i in xrange(len_self - max_entries + 1):
                        del _store[_sorted_keys.pop()]

                # add the new entry to the store
                _store[key] = data
                _sorted_keys.insert(0, key)
        finally:
            self._lock.release()

    def _buildKey(kw):
        "Build a tuple which can be used as an index for a cached value"
        k = tuple(sorted(kw.iteritems()))
        try:
            return hash(k)
        except TypeError:
            return dumps(k)

    _buildKey = staticmethod(_buildKey)


