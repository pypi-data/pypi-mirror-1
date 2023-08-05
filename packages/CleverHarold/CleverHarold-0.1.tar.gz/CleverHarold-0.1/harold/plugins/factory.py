#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Filters and apps for `Python Paste`_.
#
# This module paste-ifies the publisher types and other WSGI bits.
# Requires static.py_.
#
# .. _`Python Paste`: http://www.pythonpaste.org/
# .. _WSGI:  http://www.python.org/dev/peps/pep-0333/
# .. _static.py:  http://lukearno.com/projects/static/
#
##

from paste.auth.basic import AuthBasicHandler
from paste.deploy.converters import aslist, asbool
from static import Cling

from harold.cache import CacheMiddleware
from harold.lib import config_expression, import_attribute, import_wrapper
from harold.lib.debug import DebugInfo, Timer
from harold.lib.errordoc import NotFound
from harold.log.middleware import RequestLog
from harold.sessions import Session

from harold.database import (ActiveMapperProvider, DBAPIProvider,
                             SQLAlchemyProvider, SQLObjectProvider, )


def wsgi_static_factory(global_conf, root=None, **kwds):
    """ Application factory for the static.Cling

    @param global_conf mapping supplied by paste
    @param root name of directory from which to serve files
    @param **kwds other key/value pairs, passed to Cling
    @return Cling application serving files from root
    """
    return Cling(root=root, **kwds)


def debug_info(app, global_conf, **kwds):
    """ Filter factory for DebugInfo

    @param app contained WSGI application
    @param global_conf mapping supplied by paste
    @param **kwds currently ignored
    @param DebugInfo middleware instance
    """
    return DebugInfo(app)


def request_timer(app, global_conf, comment=False, **kwds):
    """ Filter factory for Timer

    @param app contained WSGI application
    @param global_conf mapping supplied by paste
    @param **kwds currently ignored
    @return Timer middleware instance
    """
    return Timer(app, comment=comment)


def make_publisher_filter(name):
    """ Creates and returns a filter_factory function

    @param name package and callable name, in the form pkg.subpkg.mod:call
    @return closure for creating harold publisher
    """
    publisher = import_attribute(name)

    def factory(app, global_conf, dirs=(), layout=None, defaults=(), debug=False):
        """ Function to create harold publisher middleware instance

        @param app contained WSGI application
        @param global_conf mapping supplied by paste
        @param dirs string of one or more directory names
        @param layout named layout file, as a string
        @param defaults string of one or more layout modules
        @param debug debugging flag for publisher
        @return harold publisher middleware instance
        """
        debug = asbool(debug)
        dirs = aslist(dirs)
        defaults = aslist(defaults)
        return publisher(app,
                         dirs=dirs,
                         layout=layout,
                         defaults=defaults,
                         debug=debug)
    return factory


cheetah_publisher = make_publisher_filter('harold.publishers:cheetah_publisher')
code_publisher = make_publisher_filter('harold.publishers:code_publisher')
kid_publisher = make_publisher_filter('harold.publishers:kid_publisher')
markdown_publisher = make_publisher_filter('harold.publishers:markdown_publisher')
rest_publisher = make_publisher_filter('harold.publishers:rest_publisher')


def session_filter(app, global_conf, provider=None, **kwds):
    """ Filter factory for harold.sessions.Session

    @param app contained WSGI application
    @param global_conf mapping supplied by paste
    @keyparam provider type string in the form of pkg.subpkg.mod:callable
    @return Session middleware instance
    """
    selector = None
    if provider:
        provider = import_attribute(provider)
        def selector(seq):
            return [cls for cls in seq if cls==provider][0]
    return Session(app, select=selector)


def cache_filter(app, global_conf, mapping=[], store=None, **kwds):
    """ Filter factory for harold.cache.CacheMiddleware

    @param app contained WSGI application
    @param global_conf mapping supplied by paste
    @keyparam sequence of cache param dics, with entries: pattern, keys, and ttl
    @keyparam store callable string in the form pkg.subpkg.mod:callable, or None
    @keyparam filename for DbmStorage, name of file
    @keyparam flag for DbmStorage, file open flag
    @keyparam mode for DbmStorage, file open mode
    @keyparam servers for MemCachedStorage, sequence of server:port values
    @keyparam debug for MemCachedStorage, debug flag
    @return CacheMiddleware instance
    """
    if store == 'harold.cache.storage:DbmStorage':
        filename = kwds.get('filename', None)
        flag = kwds.get('flag', 'n')
        mode = kwds.get('mode', 0666)
        if filename is None:
            raise RuntimeError('DbmStorage requires a filename')
        cls = import_attribute(store)
        store = cls.factory(filename, flag, mode)

    elif store == 'harold.cache.storage:MemCachedStorage':
        servers = kwds.get('servers', None)
        debug = kwds.get('debug', False)
        if servers is None:
            raise RuntimeError('MemCachedStorage requires a server list')
        servers = aslist(servers)
        debug = asbool(debug)
        cls = import_attribute(store)
        store = cls.factory(servers, debug)

    elif store:
        store = import_attribute(store)

    mapping = config_expression(mapping)
    return CacheMiddleware(app, mapping=mapping, store=store)


def activemapper_provider(app, global_conf, dsn, models, debug=False):
    """ Filter factory for harold.database.ActiveMapperProvider

    @param app contained WSGI application
    @param global_conf mapping supplied by paste
    @param dsn database dsn string or dictionary

    @param models string identifying models modules, e.g.,
    bookstore.models.books bookstore.models.authors

    @return ActiveMapperProvider instance
    """
    dsn = config_expression(dsn)
    debug = asbool(debug)
    models = [import_wrapper(model) for model in aslist(models)]    
    return ActiveMapperProvider(app, dsn, models, debug=debug)


def dbapi_provider(app, global_conf, dsn, models, module, debug=False):
    """ Filter factory for harold.database.DBAPIProvider

    @param app contained WSGI application
    @param global_conf mapping supplied by paste
    @param dsn database dsn string or dictionary

    @param models string identifying models modules, e.g.,
    bookstore.models.books bookstore.models.authors

    @param module module string in dotted name form or dbapi module object
    @return DBAPIProvider instance
    """
    dsn = config_expression(dsn)
    debug = asbool(debug)
    models = [import_wrapper(model) for model in aslist(models)]
    module = import_wrapper(module)
    return DBAPIProvider(app, dsn, models, module=module, debug=debug)


def sqlalchemy_provider(app, global_conf, dsn, models, debug=False):
    """ Filter factory for harold.database.SQLAlchemyProvider

    @param app contained WSGI application
    @param global_conf mapping supplied by paste
    @param dsn database dsn string

    @param models string identifying models modules, e.g.,
    bookstore.models.books bookstore.models.authors

    @return SQLAlchemyProvider instance
    """
    dsn = config_expression(dsn)
    models = [import_wrapper(model) for model in aslist(models)]
    debug = asbool(debug)
    return SQLAlchemyProvider(app, dsn, models, debug=debug)


def sqlobject_provider(app, global_conf, dsn, models, debug=False):
    """ Filter factory for harold.database.SQLObjectProvider

    @param app contained WSGI application
    @param global_conf mapping supplied by paste
    @param dsn database dsn string

    @param models string identifying models modules, e.g.,
    bookstore.models.books bookstore.models.authors

    @return SQLObjectProvider instance
    """
    dsn = config_expression(dsn)
    models = [import_wrapper(model) for model in aslist(models)]
    debug = asbool(debug)
    return SQLObjectProvider(app, dsn, models, debug=debug)


def error_notfound(global_conf, filename=None, **kwds):
    """ Application factory for NotFound

    @param global_conf mapping supplied by paste
    @param filename optional template filename
    @return NotFound application instance
    """
    app = NotFound()
    if filename is not None:
        app.template = filename
    return app


def requestlog_writer(app, global_conf, format=None, **kwds):
    """ Filter factory for RequestLog 

    @param app contained WSGI application
    @param global_conf mapping supplied by paste
    @param format optional message format
    @return RequestLog middleware instance
    """
    return RequestLog(app, format=format)
