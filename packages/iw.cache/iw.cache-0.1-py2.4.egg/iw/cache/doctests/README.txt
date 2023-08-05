========
iw.cache
========

Cache utilities
---------------

The package provide some cache utilities.
See memcache.txt and ramcache.txt

This helper will let us easily execute ZCML snippets::

  >>> from cStringIO import StringIO
  >>> from zope.configuration.xmlconfig import xmlconfig
  >>> def runSnippet(snippet):
  ...     template = """\
  ...     <configure xmlns="http://namespaces.zope.org/zope"
  ...                xmlns:iw="http://namespaces.ingeniweb.com/iw"
  ...                i18n_domain="zope">
  ...     %s
  ...     </configure>"""
  ...     xmlconfig(StringIO(template % snippet))

Cache decorators
----------------

Then we can register a ram cache::

    >>> from iw.cache.testing import clearZCML
    >>> clearZCML()
    >>> runSnippet("""
    ...     <iw:ramCache
    ...         name="same_type"
    ...         maxage="3600"
    ...         />
    ... """)

This create a ram cache utility::

    >>> import zope.component
    >>> from iw.cache.interfaces import IIWRAMCache
    >>> zope.component.getUtility(IIWRAMCache, name='same_type')
    <iw.cache.ramcache.IWRAMCache object at ...>

The package provide a cache decorator::

    >>> from iw.cache import cache
    >>> @cache('same_type')
    ... def same_type(a, b):
    ...     print 'Not cached'
    ...     return type(a) == type(b)

When the function is called, the value is not yet cached::

    >>> same_type(0, '0')
    Not cached
    False

And calling the same function with same args while return the cached value::

    >>> same_type(0, '0')
    False

An alias is provide to easyly use ramcache::

    >>> from iw.cache import ramcache
    >>> @ramcache('ramcache.alias')
    ... def test_alias():
    ...     print 'Not cached'
    ...     return True

    >>> test_alias()
    Not cached
    True

    >>> test_alias()
    True

Memcached
---------

We also can use the memcachedServer directive to use a memcached server::

    >>> clearZCML()
    >>> runSnippet("""
    ...     <iw:memcachedServer
    ...         name="memcached.storage1"
    ...         server="127.0.0.1:11211"
    ...         maxage="3600"
    ...         />
    ... """)

We need to purge the cache for testing::

    >>> from iw.cache import purge
    >>> from iw.cache.interfaces import IIWMemcachedClient
    >>> purge('memcached.storage1', storage=IIWMemcachedClient)

Then we can use the name space with the decorator::

    >>> @cache('memcached.storage1', storage=IIWMemcachedClient)
    ... def same_type2(a, b):
    ...     print 'Not cached'
    ...     return type(a) == type(b)

And it works::

    >>> same_type2(0, '0')
    Not cached
    False

    >>> same_type2(0, '0')
    False

An alias is provide to easyly use memcache::

    >>> from iw.cache import memcache
    >>> @ramcache('memcached.storage1')
    ... def test_alias():
    ...     print 'Not cached'
    ...     return True

    >>> test_alias()
    Not cached
    True

    >>> test_alias()
    True

