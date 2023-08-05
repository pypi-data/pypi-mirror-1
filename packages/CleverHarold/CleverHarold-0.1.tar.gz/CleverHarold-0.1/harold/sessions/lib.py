#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Provides WSGI middleware for known session providers.
#
# Current supported providers are apache/mod_python, flup, and paste.
#
##

from harold.lib import keys
from harold.log import logger


def default_selector(seq):
    return seq[0]


class Session:
    """ Client interface for selecting, installing, and calling a
    session middleware provider.

    @param app WSGI application or middleware
    @param select callable used to choose session middleware from type
    list; default selects first type
    @param **kwds key/value pairs supplied to session middleware
    @exception Exception when no session middleware selectable
    """

    ##
    # Filled programmatically as this module is imported
    types = list()
    
    def __init__(self, app, select=None, **kwds):
        if select is None:
            select = default_selector
        try:
            self.type = select(self.types)
        except:
            raise RuntimeError('No session provider')
        self.obj = self.type.new(app, **kwds)
        self.log = logger(self.obj)


    def __call__(self, environ, start_response):
        # we use a small closure here (and force the client to call it
        # at access time) because the session provider hasn't run yet
        # and decorated the environment.
        environ[keys.session] = lambda : self.type.get(environ)
        environ[keys.session_object] = self.obj
        self.log.debug('added session to environ')
        results = self.obj(environ, start_response)
        return results


class SessionTypeAuto(type):
    """ Metaclass that fills the Session.types sequence with subclasses
    of SessionType as they are defined.  The list is filled in the
    same order as the classes are defined, so their order in this
    module is significant.

    This metaclass also some defines class/static methods automatically
    if their names are found in the incoming namespace.  Repeat less.

    @param name class name
    @param bases class bases
    @param names class namespace
    """    
    auto_methods = {
        'available' : classmethod,        
        'get' : staticmethod,
        'importer' : staticmethod,
        'new' : staticmethod,
    }

    def __init__(cls, name, bases, names):
        super(SessionTypeAuto, cls).__init__(name, bases, names)
        for name, method in SessionTypeAuto.auto_methods.items():
            try:
                setattr(cls, name, method(names[name]))
            except (KeyError, ):
                pass
        if cls.available() and cls not in Session.types:
            Session.types.append(cls)


class SessionType:
    """ Base class for session implementation wrappers.

    Each subclass must provide a 'new' method that wraps a given
    application with a new session provider.

    Each subclass must provide a 'get' method that selects and, if
    necessary, creates, an appropriate session object from the given
    environment.

    Each subclass must provide an 'importer' method that attempts
    to import the module(s) needed by the provider.

    Note: 'new', 'get', and 'importer', methods are automatically
    converted to static methods by the metaclass, so they should not be
    set explicitly as such.
    """    
    __metaclass__ = SessionTypeAuto
    
    def available(cls):
        """ Determines if the session provider is installed and available.

        @return True if session provider is avaialble
        """
        try:
            cls.importer()
            return True
        except (ImportError, ):
            return False
    
    def importer():
        """ imports needed module(s) for session provider

        Since we don't know what the client has available, we hide
        each import statement in a class method like this.  The
        metaclass can uses this method and the available method to
        determine if the session provider is available at run time.

        The default implementation always raises an ImportError to
        ensure it's not ever added to the session_types seqeuence.
        """
        raise ImportError('Needed for installation check')


class ApacheSession(SessionType):
    """ Session provider for the mod_python Session implementation

    """
    def get(environ):
        """ Selects the session created by the mod_python middleware
        provider

        @param environ WSGI environ
        @return session object (dict-like)
        """
        from harold.sessions.mpsession import apache_session_key
        return environ[apache_session_key]()


    def importer():
        """ imports mod_python bits
        
        @exception ImportError when not running mod_python
        """
        from harold.sessions.mpsession import ApacheSessionMiddleware

    
    def new(app, **kwds):
        """ Creates a mod_python session provider

        @param app WSGI application
        @param **kwds key/value pairs passed to ApacheSessionMiddleware
        @return ApacheSessionMiddleware instance
        """
        from harold.sessions.mpsession import ApacheSessionMiddleware        
        session_app = ApacheSessionMiddleware(app, **kwds)
        return session_app


class FlupSession(SessionType):
    """ Session provider for the flup.middleware.session
    implementation

    """
    def get(environ):
        """ Selects the session created by flup.middleware.session
        provider

        @param environ WSGI environ
        @return session object (dict-like)
        """
        return environ['com.saddi.service.session'].session


    def importer():
        """ Imports flup session bits
        
        @exception ImportError when flup not installed
        """
        import flup.middleware.session


    def new(app, store_name='MemorySessionStore', **kwds):
        """ Creates a flup session provider
        
        @param app WSGI application
        @keyparam store_name name of flup store type to select from
        flup.middleware.session module; default is 'SessionMiddleware'
        @param **kwds key/value pairs passed to
        flup.middleware.session.SessionStore and SessionMiddleware
        @return ApacheSessionMiddleware instance
        """
        from flup.middleware import session
        store = getattr(session, store_name)(**kwds)
        session_app = session.SessionMiddleware(store, app)
        return session_app


class PasteSession(SessionType):
    """ Session provider for the paste.session implementation

    """
    def get(environ):
        """ Selects the session created by paste
        
        @param environ WSGI environ
        @return session object (dict-like)
        """
        return environ['paste.session.factory']()


    def importer():
        """ Imports paste session bits

        @exception ImportError when flup not installed
        """
        import paste.session


    def new(app, **kwds):
        """ Creates a paste session provider

        @param app WSGI application
        @param **kwds key/value pairs passed to
        paste.session.SessionMiddleware
        @return paste SessionMiddleware instance
        """
        from paste.session import SessionMiddleware
        session_app = SessionMiddleware(app)
        return session_app
