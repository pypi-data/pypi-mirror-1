#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Apache mod_python does not supply a WSGI middleware for its session module,
# so we define one here.
#
##

from harold.lib.mpwsgi import apache_request_key
from mod_python import apache, Session
from paste.wsgilib import add_close

##
# Environment key for use here and elsewhere.  From the
# it's-good-to-be-DRY-dept.

apache_session_key = 'apache.session.factory'


##
# Class to catch mod_python code's updates to outgoing headers.
#
# @param request original mod_python request object
# @param wsgi_headers mapping-like object for outgoing headers

class HeaderCatcher(object):
    def __init__(self, request, wsgi_headers):
        self.request = request
        self.wsgi_headers = wsgi_headers

    def headers_out(self):
        return self.wsgi_headers
    headers_out = property(headers_out)

    def __getattr__(self, name):
        return getattr(self.request, name)


##
#
# Middleware that wraps the mod_python.session.Session implementation
#
# @param app WSGI application
# @param **kwds key/value pairs passed to mod_python.Session

class ApacheSessionMiddleware:
    def __init__(self, app, **kwds):
        self.app = app
        self.kwds = kwds

    def __call__(self, environ, start_response):
        output_headers = apache.table()
        
        def factory():
            req = HeaderCatcher(environ[apache_request_key], output_headers)
            sid = self.sid()
            secret = self.secret()
            session = self.session = Session.Session(req, sid, secret)
            return session
        
        environ[apache_session_key] = factory

        def session_start_response(status, headers, exc_info=None):
            headers.extend(output_headers.items())
            return start_response(status, headers, exc_info)

        return add_close(self.app(environ, session_start_response), self.close)


    ##
    # Function to return user-supplied sid or default
    # @return sid from initial kwds or default
    
    def sid(self):
        try:
            return self.kwds['sid']
        except (KeyError, ):
            return 0


    ##
    # Function to return user-supplied secret or our default
    # @return secret string from initial kwds or default
    
    def secret(self):
        try:
            return self.kwds['secret']
        except (KeyError, ):
            return "always ask for 10% discount on purchase price"


    ##
    # Closes mod_python session object if available
    # @return None
    
    def close(self):
        try:
            self.session.save()
        except (AttributeError, ):
            pass
