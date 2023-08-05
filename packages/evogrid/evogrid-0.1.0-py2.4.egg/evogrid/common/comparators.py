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
"""Classical comparator implementations
"""

from zope import interface
from evogrid.interfaces import IComparator

class SimpleComparator(object):
    """Default comparator that uses the builtin `cmp` function on evaluations

    By setting minimize=True at init time, the opposite of cmp is used to
    transform a maximization problem into a minimization problem.
    """
    interface.implements(IComparator)

    def __init__(self,  custom_cmp=None, minimize=False):
        base_cmp = custom_cmp or cmp

        if minimize:
            self._cmp = lambda x, y: -cmp(x, y)
        else:
            self._cmp = base_cmp

    def cmp(self, r1, r2,):
        return self._cmp(r1.evaluation, r2.evaluation)

    def max(self, replicators):
        replicators = iter(replicators)
        current_max = replicators.next()
        for r in replicators:
            if self.cmp(r, current_max) > 0:
                current_max = r
        return current_max


