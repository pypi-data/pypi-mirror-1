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
utils
"""
__docformat__ = 'restructuredtext'

import zope.component
from zope.component.interfaces import ComponentLookupError
from iw.cache.ramcache import IWRAMCache
from iw.cache.interfaces import IIWRAMCache, IIWMemcachedClient

import logging
LOG = logging.getLogger('iw.cache')

def get_storage(ns, maxAge=3600, storage=IIWRAMCache, servers=None):
    """return the correct cache method::

        >>> from iw.cache.testing import clearZCML
        >>> clearZCML()
        >>> from iw.cache.decorators import get_storage
        >>> cache = get_storage(ns='iw.cache')
        >>> cache is get_storage(ns='iw.cache') is not None
        True

    """
    if storage:
        obj = zope.component.queryUtility(storage, name=ns)
        if not obj and storage is IIWRAMCache:
            # if we can't find a ram cache we need to be sure that the
            # cache does not exist
            obj = zope.component.queryUtility(IIWMemcachedClient, name=ns)
    if not obj:
        # raise via getUtility
        zope.component.getUtility(storage, name=ns)
        # make sure it raise
        raise ComponentLookupError(
                    'No cache found for the %s namespace' % ns)
    return obj

def purge(ns=None, storage=IIWRAMCache):
    """puge a cache for ns or all cache
    """
    if ns:
        cache = get_storage(ns, storage=storage)
        cache.invalidateAll()
        LOG.info('cache %s purged' % (cache,))
    else:
        caches = zope.component.getAllUtilitiesRegisteredFor(storage)
        for name, cache in caches:
            cache.invalidateAll()
            LOG.info('cache %s purged' % (cache,))


