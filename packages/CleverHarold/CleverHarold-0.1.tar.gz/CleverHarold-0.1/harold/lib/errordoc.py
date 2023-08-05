#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>


##
#
# Simple WSGI applications to display HTTP errors and set the resposes
# accordingly.
#
## 

from harold.lib import con_type
import kid


default_template = """
<html xmlns:py="http://purl.org/kid/ns">
    <head>
        <title>${code} ${message}</title>
    </head>
    <body>
        <h1>${message}</h1>
        <p>${description}</p>
        <hr />
        <b><em>${signature}</em></b>
    </body>
</html>
"""


class Error:
    """ Parent for error doc types

    Subclasses must implement a 'description(env)' method.

    Subclasses and instances can override the 'template' attribute,
    and subclasses can override the 'signature(env)' method.
    """
    template = default_template
    output = 'html'
    
    def __call__(self, environ, start_response):
        """ renders an error response

        """
        values = dict(code=self.code, message=self.message,
                      description=self.description(environ),
                      signature=self.signature(environ))
        error = kid.Template(self.template, **values)
        headers = [('Content-type', con_type.html), ]
        start_response('%(code)s %(message)s' % values, headers)
        return error.serialize(output=self.output)


    def signature(self, env):
        """ signature customized for request
	
	@param env request environment
	@return server signature string
        """
        name = env.get('SERVER_NAME', '')
        port = env.get('SERVER_PORT', 80)
        return 'WSGI (Unix) Server at %s Port %s' % (name, port)


class NotExist(Error):
    """ '400 - Bad Reqeust' error type

    """
    code = 400
    message = 'Bad Request'
    desc = ('The hostname you requested, %(SERVER_NAME)s, '
            'does not exist on this server.')
    
    def description(self, env):
	""" description customized for request
    
	@param env request environment
	@return error description string
	"""
        return self.desc % (env.get('SERVER_NAME'), )


class NotFound(Error):
    """ '404 - Not Found' error type

    """
    code = 404
    message = 'Not Found'
    desc = 'The requested URL %s was not found on this server.'

    def description(self, env):
	""" description customized for request
    
	@param env request environment
	@return error description string
	"""
        return self.desc % (env.get('PATH_INFO'), )
