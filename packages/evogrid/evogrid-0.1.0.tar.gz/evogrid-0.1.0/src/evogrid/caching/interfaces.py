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
"""Interfaces for caching related components"""

from zope.interface import Interface, Attribute

class ICache(Interface):
    """Generic cache interface to store data for keys

    A key is a picklable mapping of python object to uniquely identify a cached
    entry. Stored values can be any picklable object.

    Cache implementations should automatically update their statistics and be
    thread-safe.
    """

    hits = Attribute("Number of times the cache was successfully accessed")

    misses = Attribute(
        "Number of times the cache could not find a matching cached entry")

    def invalidate(key=None):
        """Invalidate the cache entry corresponding to key

        If key is None, all entries are invalidated.
        """

    def query(key, default=None):
        """Return the cached entry matching key

        Return ``default`` if no matching entry is found.
        """

    def set(key, data):
        """Stores ``data`` in the cache at ``key``"""

    def __len__():
        """Number of cached entries"""

