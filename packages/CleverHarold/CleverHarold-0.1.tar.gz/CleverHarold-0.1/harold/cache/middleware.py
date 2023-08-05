#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import re

from harold.lib import is_iterator, request_path, mapping_response_hook
from harold.log import logger
from harold.cache.lib import Cacheable, CacheType, CacheEntry


# It's amazing we can't get this somewhere else.
re_type = type(re.compile(''))


class CacheableUrl(Cacheable):
    """ Encapsulates a cachable response to a URL request

    @param pattern string or match object to apply to url paths
    @param keys WSGI environ key or sequence of keys
    @param ttl time to live
    """
    def __init__(self, pattern, keys=None, ttl=None):
        super(CacheableUrl, self).__init__(ttl)
        if not isinstance(pattern, re_type):
            pattern = re.compile(pattern)
        if not isinstance(keys, (tuple, list)):
            keys = (keys, )
        self.pattern = pattern
        self.keys = keys

    def key(self, environ):
        """ creates key for cachable url

        @param environ WSGI request environment
        @return suitable key
        """
        path = request_path(environ)
        keys = [(key, environ.get(key)) for key in self.keys]
        return (path, ) + tuple(keys)

    def match(self, environ):
        """ matches url pattern against environment

        @param environ WSGI request environment
        @return True if self.pattern matches request environment path
        """
        return self.pattern.match(request_path(environ)) and True or False


class WSGICacheEntry(CacheEntry):
    """ Encapsulates a WSGI response as an entry in a Cache

    @param ttl time to live
    @param value data to cache
    @param status response status string
    @param headers response headers sequence
    """
    def __init__(self, ttl, value, status, headers):
        super(WSGICacheEntry, self).__init__(ttl, value)
        self.status = status
        self.headers = headers


class CacheMiddleware(CacheType):
    """ Cache WSGI middleware


    mapping = [
        dict(pattern='/path/to/url', keys=None, ttl=3),
        dict(pattern='/other/.*', keys='REMOTE_USER', ttl=3)
        ]

    @param app wrapped WSGI application
    @param mapping sequence of cacheable parameter dicts
    @keyparam store storage instance or storage factory 
    """
    def __init__(self, app, mapping, store=None):
        super(CacheMiddleware, self).__init__(store)
        self.app = app
        self.mapping = [CacheableUrl(**entry) for entry in mapping]
        self.log = logger(self.store)

    def __call__(self, environ, start_response):
        item = self.match(environ)
        if item:
            key = item.key(environ)
            self.counter_incr('matched', key[0])
            try:
                entry = self[key]
                if entry.valid():
                    self.counter_incr('hit', key[0])
                    start_response(entry.status, entry.headers)
                    return entry.value
                else:
                    del(self[key])
                    self.counter_incr('cleared', key[0])
                    raise KeyError
            except (KeyError, ):
                response = {}
                hook = mapping_response_hook(start_response, response)
                value = self.app(environ, hook)
                if is_iterator(value):
                    value = [v for v in value]
                self[key] = WSGICacheEntry(item.ttl, value,
                                           response['status'],
                                           response['headers'])
                self.counter_incr('missed', key[0])
                return value
        else:
            self.counter_incr('notmatched', '')
            return self.app(environ, start_response)


    def match(self, environ):
        """ applies url patterns to requested path

        @param environ WSGI request environment
        @return CacheableUrl instance on match, or None
        """
        for item in self.mapping:
            if item.match(environ):
                return item
