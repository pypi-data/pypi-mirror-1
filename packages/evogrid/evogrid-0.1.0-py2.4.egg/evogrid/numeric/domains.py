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
"""Numerical domains"""

from evogrid.numeric.interfaces import IMinMaxDomain
from numpy import array, maximum, minimum, all
from zope.interface import implements
from zope.component import adapts

class HyperCubeDomain(object):
    """Numerical domain bound by min and max values"""
    implements(IMinMaxDomain)

    min, max = None, None

    def __init__(self, min, max):
        self.min = array(min)
        self.max = array(max)

    def __contains__(self, cs):
        # TODO: optimize
        return all(self.ensure_belong(cs) == cs)

    def ensure_belong(self, cs):
        cs = maximum(self.min, cs)
        return minimum(self.max, cs)

    def __repr__(self):
        class_name = self.__class__.__name__
        return "%s(%r, %r)" % (class_name, list(self.min), list(self.max))


class ResolutionDowngraderDomain(object):
    """Adapter to restict domain values to rounded values

    This can be usefull to optimize the efficiency of an evaluation caching
    strategy.
    """
    implements(IMinMaxDomain)
    adapts(IMinMaxDomain)

    def get_max(self):
        return self._domain.max

    max = property(get_max)

    def get_min(self):
        return self._domain.min

    min = property(get_min)

    # decimal resolution (number of digits)
    _resolution = 1

    def __init__(self, domain, resolution=1):
        self._resolution = resolution
        self._domain = domain
        self._scale = domain.max - domain.min

    def __contains__(self, cs):
        return self.ensure_belong(cs) == cs

    def ensure_belong(self, cs):
        scale = self._scale
        scaled = cs / scale
        cs = scaled.round(self._resolution) * scale
        return self._domain.ensure_belong(cs)

    def __repr__(self):
        class_name = self.__class__.__name__
        return "%s(%r, resolution=%r)" % (
            class_name, self._domain, self._resolution)


