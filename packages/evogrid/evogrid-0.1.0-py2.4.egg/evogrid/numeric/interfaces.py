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
"""Interfaces for the numerical representation"""

from zope.interface import Attribute, Interface
from evogrid.interfaces import IReplicator, IDomain

class IVectorReplicator(IReplicator):
    """Replicator whose candidate solution is a 1-d numpy array"""


class IMinMaxDomain(IDomain):
    """Domain for 1-d numpy arrays bounded by min and max arrays"""

    min = Attribute('Numerical array to define a minimal bound')

    min = Attribute('Numerical array to define a maximal bound')


class ITestFunction(Interface):
    """Test function to minimize"""

    def __call__(x):
        """x is a ndarray with shape (N,)

        return a numerical scalar
        """

class I2DimTestFunction(ITestFunction):
    """Test function that accepts ndarray with shape (2,)"""

class INDimTestFunction(ITestFunction):
    """Test function that accepts ndarray with shape (N,) for any N"""
