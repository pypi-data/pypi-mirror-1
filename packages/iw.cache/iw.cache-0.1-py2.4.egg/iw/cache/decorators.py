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
cache decorators
"""
__docformat__ = 'restructuredtext'

import zope.component
import  plone.memoize.volatile

from iw.cache.interfaces import IIWRAMCache
from iw.cache.interfaces import IIWMemcachedClient
from iw.cache.utils import get_storage
from iw.cache.keys import cache_key

def cache(ns, get_key=None, maxAge=3600, storage=IIWRAMCache):
    """a cache decorator
    """
    get_cache = lambda *a, **k: get_storage(ns, maxAge, storage)

    if not get_key:
        get_key = cache_key

    return plone.memoize.volatile.cache(get_key, get_cache=get_cache)

def ramcache(ns, get_key=None, maxAge=3600):
    return cache(ns, get_key=get_key, maxAge=maxAge, storage=IIWRAMCache)

def memcache(ns, get_key=None, maxAge=3600):
    return cache(ns, get_key=get_key, maxAge=maxAge, storage=IIWMemcachedClient)


