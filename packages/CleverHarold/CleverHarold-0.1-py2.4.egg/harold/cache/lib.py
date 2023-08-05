#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

""" Cache middleware and decorator


"""
import time


from harold.lib import synchronized
from harold.cache.langoliers import Langoliers
from harold.cache.storage import MemoryStorage

##
# Module-level global for default time to live; allows for monkey
# patching, which makes testing faster.
default_ttl = 60


##
# Module-level global for default store types; allows for
# monkey patching.
default_store = MemoryStorage


##
# Convenience sequence of most cache counter keys
counter_keys = 'hit missed cleared matched notmatched'.split()


class Cacheable(object):
    """ Base for types that encapsulate a cacheable item of some kind

    @param ttl time to live in seconds
    """
    def __init__(self, ttl):
        self.ttl = (ttl is None and default_ttl or ttl)

    def key(self, *args, **kwds):
        raise NotImplementedError()

    def match(self, *args, **kwds):
        raise NotImplementedError()


class CacheEntry(object):
    """ Encapsulates an entry in a Cache

    @param ttl time to live
    @param value data to cache
    """
    def __init__(self, ttl, value):
        self.ttl = ttl
        self.expires = (ttl > 0 and ttl + time.time() or 0)
        self.value = value

    def valid(self):
        """ indicates validity of cache entry

        @return True if valid, False if not
        """
        expires = self.expires
        return (expires == 0 and True or time.time() < expires)


class CacheType(object):
    """ Base type for Cache implementations

    @param store storage instance or factory
    """
    def __init__(self, store):
        if store is None:
            store = default_store
        try:
            store = store()
        except (TypeError, ):
            pass
        self.store = store
        self.counters = dict.fromkeys(counter_keys, 0)
        Langoliers.register(self)

    @synchronized
    def get(self, key, default=None):
        """ return an item from the cache by key or the default if not found

        """
        return self.store.get(key, default=default)

    @synchronized
    def __getitem__(self, key):
        return self.store[key]

    @synchronized
    def __setitem__(self, key, value):
        if not isinstance(value, CacheEntry):
            raise TypeError('Values must be CacheEntry instances')
        self.store[key] = value

    @synchronized
    def __delitem__(self, key):
        del(self.store[key])

    @synchronized
    def keys(self):
        return self.store.keys()

    @synchronized
    def items(self):
        return self.store.items()

    @synchronized
    def values(self):
        return self.store.values()

    @synchronized
    def counter_incr(self, counter, item):
        try:
            self.counters[counter] += 1
        except (KeyError, ):
            self.counters[counter] = 1
        try:
            self.log.debug('"%s" - %s:%s', item, counter, self.counters[counter])
        except (AttributeError, ):
            pass
