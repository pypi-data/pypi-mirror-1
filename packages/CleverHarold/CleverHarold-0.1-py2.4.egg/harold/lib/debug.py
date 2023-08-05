#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Module that defines simple debugging middleware.
#
# Two classes are provided here, one for writing the WSGI environment
# to an HTML document as a comment, and another for writing execution
# time.
#
##

import re
import time
from paste.wsgilib import add_close
from harold.lib import headers_response_hook, header_match, con_type

##
# Function to find html content type in headers.

has_html_header = header_match('content-type', con_type.html)


class DebugInfo:
    """ DebugInfo(app) -> writes request environment as html comment

    @param app WSGI application
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """ When called by the server, append the environment to any html

        @param environ WSGI request environment
        @param start_response WSGI responder
        @return original response or html-with-debug-comments iterator
        """
        headers_copy = []
        header_hook = headers_response_hook(start_response, headers_copy)
        response = self.app(environ, header_hook)
        data = [d for d in response]
        if data and data[0] and has_html_header(headers_copy):
            d = '<!--\n'
            items = environ.items()
            items.sort(key=lambda x:x[0].lower())
            for key, value in items:
                d += '%s : %s\n' % (key, value)
            d += '-->'
            try:
                data[0] = re.sub('(?i)(</html>)', r'\n%s\1' % d, data[0])
            except (TypeError, ):
                pass
        try:
            data = add_close(data, response.close)
        except (AttributeError, ):
            pass
        return data


class Timer:
    """ Timer(app) -> adds processing time to every request

    @param app WSGI application
    """
    def __init__(self, app, comment=False):
        self.app = app
        self.comment = comment

    def __call__(self, environ, start_response):
        """ When called by the server, append the request processing time

        @param environ WSGI request environment
        @param start_response WSGI responder
        @return original response or html-with-debug-comments iterator
        """
        headers_copy = []
        header_hook = headers_response_hook(start_response, headers_copy)
        t0 = time.time()
        response = self.app(environ, header_hook)
        data = [d for d in response]
        t1 = time.time() - t0

        if data and data[0] and has_html_header(headers_copy):
            message = '\nProcessing Time: %0.5f ms' % t1
            if self.comment:
                message = '<!-- %s -->' % message
            try:
                data[0] = re.sub('(?i)(</html>)',
                                 r'%s\1' % message,
                                 data[0])
            except (TypeError, ):
                pass
        try:
            data = add_close(data, response.close)
        except (AttributeError, ):
            pass
        return data
