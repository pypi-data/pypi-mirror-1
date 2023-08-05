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
"""Numerical replicators"""

from evogrid.common.replicators import DomainedReplicator
from evogrid.numeric.interfaces import IVectorReplicator
from numpy import array
from zope.interface import implements

class VectorReplicator(DomainedReplicator):
    """DomainedReplicator with a numpy array as candidate solution"""
    implements(IVectorReplicator)

    def _get_cs(self):
        return self._candidate_solution

    def _set_cs(self, cs):
        if cs is not None:
            cs = array(cs)
        # check the domain constraints
        super(VectorReplicator, self)._set_cs(cs)

    candidate_solution = property(_get_cs, _set_cs)

    def __eq__(self, other):
        """Test candidate solution equality

        All vector parameters must be equal.
        """
        return (self.candidate_solution == other.candidate_solution).all()
