# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import cPickle

from harold.lib import make_annotated
from harold.cache.lib import Cacheable, CacheType, CacheEntry


class CacheableCall(Cacheable):
    """ Encapsulates a cacheable function or method call

    """
    def __init__(self, call, ttl):
        super(CacheableCall, self).__init__(ttl)
        self.call = call

    def key(self, args, kwds):
        """ creates key for call, args and keywords

        @param args positional arguments to call
        @param kwds keyword arguments to call
        @return two-tuple that uniquely identifies call and arguments
        """
        try:
            return (hash(self.call), cPickle.dumps((args, kwds)))
        except (TypeError, ):
            pass


class ResultsCache(CacheType):
    """ Cache for callable results """


cacheable_anno_template = """
def %(name)s%(signature)s:
    %(docstring)r
    return %(name)s.func_cacheable%(values)s
"""


def cacheable(store=None, ttl=None):
    """ returns decorator for caching results to callables
    
    @keyparam store storage instance or factory
    @keyparam ttl time to live
    @return callable decorator
    """
    def inner(original):
        """ creates a caching version of the original callable

        @param original function or method
        @return replacement function        
        """
        cache = ResultsCache(store)
        call = CacheableCall(original, ttl)
        counter_incr = cache.counter_incr
        func_key = hash(original)

        def cacheable_anno(*args, **kwds):
            res_key = call.key(args, kwds)
            if not res_key:
                counter_incr('errors', res_key)
                return original(*args, **kwds)

            try:
                result = cache[res_key]
                if result.valid():
                    counter_incr('hit', res_key)
                    return result.value
                else:
                    counter_incr('cleared', res_key)                
                    del(cache[res_key])
                    raise KeyError
            except (KeyError, ):
                counter_incr('missed', res_key)
                result = original(*args, **kwds)
                cache[res_key] = CacheEntry(ttl, result)
                return result

        replacement = make_annotated(original, cacheable_anno_template)
        replacement.func_cacheable = cacheable_anno
        replacement.cache = cache
        return replacement
    return inner
