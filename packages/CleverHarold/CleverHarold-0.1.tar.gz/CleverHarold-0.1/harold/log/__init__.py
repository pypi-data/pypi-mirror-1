#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
#
# Synopsis
# ========
#
# To log to the 'harold' channel, the simplest usage is::
#
#    from harold import log
#    ...
#    log.warn("Please don't do that")
#
#
# For a module-level logger::
#
#    from harold.log import logger
#    ...
#    log = logger(__name__)
#    log.debug('Loaded module')
#
#
# For a class-level logger::
#
#    from harold.log import logger
#
#    class Spam:
#        def __init__(self):
#            self.log = logger(self)
#            self.log.debug('Created instance')
##

import logging
import logging.config

import harold
from harold.lib import detect_runtime_config


default_format = '%(asctime)s - %(levelname)s %(name)s - %(message)s'
default_dateformat = None # ISO8601
default_level = logging.DEBUG
default_handler = logging.StreamHandler()


namers = [
    lambda x: x.__name__,
    lambda x: x.__class__.__name__.split('.')[-1],
    lambda x: str(x),
]


def logger(obj, channel=None, level=None, handler=None, format=None,
           dateformat=None, report=True):
    """ defines a Logger instance for an object

    @param obj any object
    @param channel optional channel name, uses obj name or string value if None
    @param level optional level; if None, uses module default
    @param handler optional handler; if None uses module default StreamHandler
    @param format optional message format; if None uses module default
    @param dateformat optional date format; if None uses default (ISO8601)
    @return logging.Logger instance
    """
    if channel is None:
        for namer in namers:
            try:
                channel = namer(obj)
            except:
                pass
            else:
                break

    
    logobj = logging.getLogger(channel)
    if logobj.handlers:
        return logobj

    if level is None:
        level = default_level
    if format is None:
        format = default_format
    if dateformat is None:
        # both can be None, but this supports monkey patching.
        # and harold likes monkeys.
        dateformat = default_dateformat
    if handler is None:
        handler = default_handler

    formatter = logging.Formatter(format, dateformat)
    handler.setFormatter(formatter)
   
    logobj.addHandler(handler)
    logobj.setLevel(level)
    logobj.propagate = 0

    if report:
        logging.debug("created log channel '%s' at level %s", channel,
                      logging._levelNames[level])
    return logobj


def isolate_channel(obj, channel=None):
    logobj = logger(obj, channel=channel)
    class IsolatedChannel(logging.Filter):
        def filter(self, r):
            return int(r.name == logobj.name)
    default_handler.addFilter(IsolatedChannel())


def disable():
    """ turn off logging

    @return None
    """
    default_handler.setLevel(100)


def init():
    """ locate and apply logging configuration (on import or reload)

    @return None
    """
    root = logging.root
    root.setLevel(default_level)
    formatter = logging.Formatter(default_format, default_dateformat)
    default_handler.setFormatter(formatter)
    root.addHandler(default_handler)
    
    cfg = detect_runtime_config()
    if cfg:
        try:
            logging.config.fileConfig(cfg)
        except (Exception, ), exc:
            print 'Unable to apply logging config in %s' % (cfg, )
            print 'Ignoring exception "%r"' % (exc, )
    else:
        pass
        #print 'Unable to detect configuration file.'
        #print 'Logging configuration not attempted.'

init()


##
# Convenience logger instance
log = logger(harold, report=False)


##
# Convenience logger methods
critical, error, warning, info, debug = \
          log.critical, log.error, log.warning, log.info, log.debug
