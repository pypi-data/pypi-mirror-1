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
"""Numerical replicator providers"""

from evogrid.interfaces import IProvider
from evogrid.numeric.interfaces import IMinMaxDomain
from evogrid.numeric.domains import HyperCubeDomain
from evogrid.numeric.replicators import VectorReplicator
from itertools import izip
from numpy import array
from numpy.random import uniform
from zope.interface import implements

class UniformReplicatorGenerator(object):
    """Randomly generate vector-based replicators replicator"""
    implements(IProvider)

    def __init__(self, min=None, max=None, dom=None):
        if min is None or max is None:
            if IMinMaxDomain.providedBy(dom):
                min, max = dom.min, dom.max
            else:
                raise ValueError('min and max must be specified')
        self._min = min
        self._max = max
        self._dom = dom or HyperCubeDomain(min, max)

    def next(self):
        ranges = izip(self._min, self._max)
        cs = array([uniform(min, max) for min, max in ranges])
        return VectorReplicator(cs=cs, dom=self._dom)

    def __iter__(self):
        return self


