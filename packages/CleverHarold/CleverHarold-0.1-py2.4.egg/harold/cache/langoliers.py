#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import threading
import time
import weakref

from harold.lib import synchronized


class Langoliers(threading.Thread):
    """ Thread to remove invalid cache entries

    """
    caches = weakref.WeakKeyDictionary()
    snooze = 3

    def __init__(self):
        super(Langoliers, self).__init__()
        self.setDaemon(True)
        self.__lock = threading.RLock()

    def run(self):
        lock = self.__lock
        while True:
            time.sleep(self.snooze)
            lock.acquire()
            try:
                for cache in self.caches.keys():
                    for key in cache.keys():
                        try:
                            entry = cache[key]
                        except (KeyError, ):
                            pass
                        else:
                            if not entry.valid():
                                cache.counter_incr('cleared', key[0])
                                del(cache[key])
            finally:
                lock.release()


    @classmethod
    @synchronized
    def register(cls, cache):
        """ adds cache to mapping of caches to sweep and prune

        @param cache cache instance to prune
        @return None
        """
        cls.caches[cache] = True

##
# Module-level Langoliers instance that's started automatically
langoliers = Langoliers()
langoliers.start()
