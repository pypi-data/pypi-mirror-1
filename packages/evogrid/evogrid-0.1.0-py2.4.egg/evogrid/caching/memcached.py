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
"""python-memcached based cache implementation

This cache implementation relies on a external caching server (memcached) and
uses the python-memcached client API to access it.

This module also provides so utilities to start a memcached server from python.
"""

from base64 import b64encode
from cPickle import dumps
from evogrid.caching.interfaces import ICache
from memcache import Client
from tempfile import mkdtemp
from thread import get_ident
from threading import Lock
from zope.interface import implements
import os
import shutil

class MemcachedCache(object):
    """Storage for cache implementation that stores entries on external servers

    Thread safeness is achevied by broadcasting cache request to a unique
    Client instance per thread.
    """
    implements(ICache)

    #
    # ICache public attributes implemented as readonly properties
    #

    def _get_hits(self):
        return self._aggregate_stat('get_hits')

    hits = property(_get_hits)

    def _get_misses(self):
        return self._aggregate_stat('get_misses')

    misses = property(_get_misses)

    #
    # MemcachedCache public attribute implemented as property
    #

    def _get_servers(self):
        return self._servers

    def _set_servers(self, servers):
        """Thread safe update of the servers list"""
        self._servers_lock.acquire()
        try:
            self._servers = servers
            for storage in self._storages.itervalues():
                storage.set_servers(servers)
        finally:
            self._servers_lock.release()

    servers = property(_get_servers, _set_servers)

    #
    # Private API and thread safeness management
    #

    def __init__(self, servers=("127.0.0.1:11211",)):
        self._servers_lock = Lock()
        self._servers = tuple(servers)

        # map of memcached storages: keys are thread_ident
        # each storage is memcache.Client instance that is used only in one
        # thread
        self._storages = {}

    def _aggregate_stat(self, key):
        total_stats = self._get_storage().get_stats()
        value = 0
        for _, data in total_stats:
            value += int(data[key])
        return value

    def _get_storage(self):
        key = get_ident()
        storage = self._storages.get(key, None)
        if storage is None:
            storage = self._storages.setdefault(key, Client(self.servers))
        return storage

    #
    # ICache public methods
    #

    def __len__(self):
        return self._aggregate_stat('curr_items')

    def invalidate(self, key=None):
        if key is None:
            self._get_storage().flush_all()
        else:
            key = self._build_key(key)
            self._get_storage().delete(key)

    def query(self, key, default=None):
        """Search the store to find a matching entry

        If nothing is found return default.
        """
        key = self._build_key(key)
        res = self._get_storage().get(key)
        if res is None:
            return default
        else:
            return res

    def set(self, key, data):
        """Add data to the store"""
        key = self._build_key(key)
        self._get_storage().set(key, data)

    def _build_key(key):
        """Build a string out of a dictionary based key

        The key should not contain any whitespace or '\n' character thus we
        use the base64 encoding of the pickle of the given object.
        """
        return b64encode(dumps(key))

    _build_key = staticmethod(_build_key)



class MemcachedServerManager(object):
    """Utility class to manage memcached servers from python"""

    # IP to listen on by default. use None not to restrict IP
    default_ip = None

    def __init__(self, pid_dir=None, ip=None):
        # directory to store pid files of running servers
        if pid_dir is None:
            pid_dir = mkdtemp(suffix='-memcached-pids', prefix='evogrid-')
        self.pid_dir = pid_dir

        # default ip address for servers to listen on
        if ip is not None:
            self.default_ip = ip

    def __del__(self):
        self.stop_all()
        shutil.rmtree(self.pid_dir)

    def start(self, port, ip=None, maxsize=64):
        ip = self._find_ip(ip)

        cmd = "memcached -p %d -m %d -d -P %s" % (
            port, maxsize, self._build_filename(port, ip))

        if ip != "INDRR_ANY":
            cmd = "%s -l %s" % (cmd, ip)

        code = os.system(cmd)
        if code != 0:
            raise RuntimeError("Failed to start server with: %s" % cmd)

    def stop(self, port):
        """Stop the managed server that listen on `port`"""
        filename = self._get_pid_filename(port)
        if filename is not None:
            self._stop(filename)

    def stop_all(self):
        """Stop all running managed servers"""
        for filename in os.listdir(self.pid_dir):
            self._stop(os.path.join(self.pid_dir, filename))

    def get_server_ports(self):
        """Return the list of running server ports"""
        return [self._port_from_filename(f) for f in os.listdir(self.pid_dir)]

    def _port_from_filename(self, filename):
        return int(filename.rsplit('.', 1)[0].split(':')[1])

    def _stop(self, filename):
        os.kill(int(file(filename).read()), 15)
        os.unlink(filename)

    def _build_filename(self, port, ip=None):
        filename = "%s:%d.pid" % (self._find_ip(ip), port)
        return os.path.join(self.pid_dir, filename)

    def _get_pid_filename(self, port, default=None):
        for filename in os.listdir(self.pid_dir):
            if port == self._port_from_filename(filename):
                return os.path.join(self.pid_dir, filename)
        return default

    def _find_ip(self, ip):
        return ip or self.default_ip or "INDRR_ANY"



