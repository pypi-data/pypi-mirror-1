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
"""Adapters for variators components

As Variator components are highly representation dependent, no default
implementation is provided.

However, you will find here a default multi-adapter for the following scheme:
(IVariator, IProvider) -> IProvider
"""

from itertools import islice
from zope.interface import implements
from zope.component import provideAdapter, adapts

from evogrid.interfaces import IVariator
from evogrid.interfaces import IChainedProvider, IProvider

class ProviderFromVariator(object):
    """Default multi-adapter to plug variators in providers chains

    This uses a class that wraps a generator since generators are builtin
    python objects that do not support interface implementation.

    The provider attribute is a property so that the wraped generator gets
    updated on provider update.
    """
    implements(IChainedProvider)
    adapts(IVariator, IProvider)

    def __init__(self, variator, provider):
        self._variator = variator
        self.provider = provider

    def _buildGenerator(self, provider, variator):
        while True:
            reps_to_combine = list(islice(provider, variator.number_to_combine))
            for combined in variator.combine(*reps_to_combine):
                yield combined

    def _getProvider(self):
        return self._provider

    def _setProvider(self, provider):
        """update the embedded generator on upstream provider update"""
        self._provider = provider
        self._generator = self._buildGenerator(provider, self._variator)

    provider = property(_getProvider, _setProvider)

    def next(self):
        return self._generator.next()

    def __iter__(self):
        return self._generator

# Register ProviderFromVariator as default adapter
provideAdapter(ProviderFromVariator)

