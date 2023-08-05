# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
"""
__docformat__ = 'restructuredtext'


from zope.app.component.metaconfigure import utility
from iw.cache.interfaces import IIWMemcachedClient
from iw.cache.memcached import IWMemcachedClient
from iw.cache.memcached import NS as memcached_ns
from iw.cache.interfaces import IIWRAMCache
from iw.cache.ramcache import IWRAMCache
from iw.cache.ramcache import NS as ramcache_ns

def memcachedserver(_context, server=None, name=None, maxage=None):
    if name is None:
        name = NS
    if maxage is None:
        maxage = 3600
    if server is None:
        servers = ['127.0.0.1:11211']
    else:
        servers = [str(server)]
    component = IWMemcachedClient(servers=servers, defaultNS=name,
                                  defaultAge=maxage)
    utility(_context, provides=IIWMemcachedClient,
            component=component, name=name)

def ramcache(_context, name=None, maxage=None):
    if name is None:
        name = NS
    if maxage is None:
        maxage = 3600
    component = IWRAMCache(ns=name, maxAge=maxage)
    utility(_context, provides=IIWRAMCache,
            component=component, name=name)

