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
memcached
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface

from lovely.memcached.utility import MemcachedClient

from interfaces import IIWMemcachedClient
from interfaces import MemcachedError

NS='iw.cache.memcached'

_marker = object()


class IWMemcachedClient(MemcachedClient):
    """used to have a plone.memoize compatible
    storage.
    """
    zope.interface.implements(IIWMemcachedClient)

    def get(self, key, default=_marker):
        """returns query results"""
        value = super(IWMemcachedClient, self).query(key, ns=self.defaultNS, default=default)
        if value is _marker:
            raise MemcachedError('Seems the server for %s is not up' % self.defaultNS)
        return value

    def __setitem__(self, key, value):
        self.set(value, key, ns=self.defaultNS)

