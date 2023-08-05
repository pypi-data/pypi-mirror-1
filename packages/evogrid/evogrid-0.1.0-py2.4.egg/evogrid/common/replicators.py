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
"""Default replicator implementation"""
from copy import deepcopy

from zope.interface import implements
from evogrid.interfaces import IReplicator, IDomainedReplicator

class Replicator(object):
    implements(IReplicator)

    evaluation = None

    candidate_solution = None

    _attributes = (('cs', 'candidate_solution'), ('ev', 'evaluation'),)

    def __init__(self, cs=None, ev=None):
        self.candidate_solution = cs
        self.evaluation = ev

    def __eq__(self, other):
        return self.candidate_solution == other.candidate_solution

    def __repr__(self):
        build_strings = []
        for arg, attr_name in self._attributes:
            attr = getattr(self, attr_name, None)
            if attr is not None:
                build_strings.append("%s=%r" % (arg, attr))
        class_name = self.__class__.__name__
        return "%s(%s)" % (class_name, ', '.join(build_strings))

    def replicate(self):
        """Exact replication through deepcopy"""
        return deepcopy(self)


class DomainedReplicator(Replicator):
    implements(IDomainedReplicator)

    _domain = None

    def _get_domain(self):
        return self._domain

    def _set_domain(self, dom):
        self._domain = dom
        if self._candidate_solution is not None:
            # trigger domain constrain thanks to the candidate_solution
            # property implementation
            self.candidate_solution = self.candidate_solution

    domain = property(_get_domain, _set_domain)

    _candidate_solution = None

    def _get_cs(self):
        return self._candidate_solution

    def _set_cs(self, cs):
        domain = self.domain
        if domain is not None:
            cs = domain.ensure_belong(cs)
        self._candidate_solution = cs

    candidate_solution = property(_get_cs, _set_cs)

    _attributes = Replicator._attributes + (('dom', 'domain'),)

    def __init__(self, cs=None, ev=None, dom=None):
        self.domain = dom
        super(DomainedReplicator, self).__init__(cs=cs, ev=ev)


