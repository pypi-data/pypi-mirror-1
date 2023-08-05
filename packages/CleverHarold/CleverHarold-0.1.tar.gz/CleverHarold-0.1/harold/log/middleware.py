#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

# This is just a sketch so far, not worthy of documentation.  It's
# also inefficient, and it doesn't integrate with harold.log.

import time
from harold.lib import mapping_response_hook, header_match

default_format = '%h %l %u %t "%r" %>s %b'
default_value = '-'
arg_pat = '%(?:\{(?P<arg>.*?)\})*?'


def remote_host(app, info, res, env):
    return env.get('REMOTE_ADDR', default_value)

def remote_log(app, info, res, env):
    return default_value

def remote_user(app, info, res, env):
    return env.get('REMOTE_USER', default_value)

def received_time(app, info, res, env):
    return time.ctime(env.get('requestlog.start', default_value))

def first_request_line(app, info, res, env):
    return '%s %s' % (env['REQUEST_METHOD'], env.get('SCRIPT_NAME', '') + env['PATH_INFO'] or '/', )

def first_response(app, info, res, env):
    ## needs to account for redirects
    return info['status'].split(' ')[0]

def last_response(app, info, res, env):
    return info['status'].split(' ')[0]

def response_size(app, info, res, env):
    try:
        return len(res)
    except:
        return -1


replacers = {
    # partially implemented
    '%h' : remote_host,
    '%l' : remote_log,
    '%u' : remote_user,
    '%t' : received_time,
    '%r' : first_request_line,
    '%s' : first_response,
    '%>s' : last_response,
    '%b' : response_size,
}    

# not implemented
##     '%A' : 'local_ip',
##     '%B' : 'size or 0',
##     arg_pat + 'C' : 'request cookie NAME',
##     '%D' : 'request processing time microseconds',
##     arg_pat + 'e' : 'environ NAME',
##     '%f' : 'filename',
##     '%H' : 'request protocol',
##     '%{NAME}i' : environ['incoming header']['NAME'],
##     '%m' : environ['request method'],
##     '%{NAME}n' : 'note NAME from another module',
##     '%{NAME}o' : environ['outgoing header']['NAME'],
##     '%p' : environ['http port'],
##     '%P' : environ['process id of child'],
##     '%{pid}P' : environ['process id of child'],
##     '%{tid}P' : environ['thread id of child'],
##     '%{hextid}P' : environ['thread id (hex) of child'],
##     '%q' : environ['query string'],
##     '%{format}t' : 'request received time, format via strftime',
##     '%T' : 'request serve time n seconds',
##     '%U' : lambda env: env['url path'],
##     '%v' : 'server name',
##     '%V' : 'server name',
##     '%X' : 'connection status',
##     '%I' : 'bytes in',
##     '%O' : 'bytes out',

from harold.log import logger
class RequestLog:
    def __init__(self, app, format=None):
        self.app = app
        if format is None:
            format = default_format
        self.format = format
        self.log = logger(self)
        
    def __call__(self, environ, start_response):
        environ['requestlog.start'] = time.time()
        response_info = {}
        mapping_response = mapping_response_hook(start_response, response_info)        
        response = self.app(environ, mapping_response)
        message = self.message(response_info, response, environ)
        self.log.debug(message)
        return response

    def message(self, mapping, data, env):
        msg = self.format
        for key, value in replacers.items():
            msg = msg.replace(key, str(value(self, mapping, data, env)))
        return msg

"""
Common Log Format (CLF)
"%h %l %u %t \"%r\" %>s %b"
Common Log Format with Virtual Host
"%v %h %l %u %t \"%r\" %>s %b"
NCSA extended/combined log format
"%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\""
Referer log format
"%{Referer}i -> %U"
Agent (Browser) log format
"%{User-agent}i"

%%  The percent sign
  %a  Remote IP-address

  %A Local IP-address

  %B Size of response in bytes, excluding HTTP headers.

  %b  Size of response in bytes, excluding HTTP headers. In CLF format, i.e. a '-' rather than a 0 when no bytes are sent.

  %{Foobar}C The contents of cookie Foobar in the request sent to the
   server.

  %D The time taken to serve the request, in microseconds.

  %{FOOBAR}e The contents of the environment variable FOOBAR

  %f Filename

  %h Remote host

  %H The request protocol

  %{Foobar}i  The contents of Foobar: header line(s) in the request sent to the server.

  %l  Remote logname (from identd, if supplied). This will return a dash unless mod_ident is present and IdentityCheck is set On.

  %m  The request method

  %{Foobar}n The contents of note Foobar from another module.

  %{Foobar}o The contents of Foobar: header line(s) in the reply.

  %p The canonical port of the server serving the request

  %P The process ID of the child that serviced the request.

  %{format}P The process ID or thread id of the child that serviced
   the request. Valid formats are pid, tid, and hextid. hextid
   requires APR 1.2.0 or higher.

  %q The query string (prepended with a ? if a query string exists,
   otherwise an empty string)

  %r First line of request

  %s Status. For requests that got internally redirected, this is the
   status of the *original* request --- %>s for the last.

  %t Time the request was received (standard english format)

  %{format}t The time, in the form given by format, which should be in
   strftime(3) format. (potentially localized)

  %T The time taken to serve the request, in seconds.

  %u Remote user (from auth; may be bogus if return status (%s) is
   401)

  %U The URL path requested, not including any query string.

  %v The canonical ServerName of the server serving the request.

  %V The server name according to the UseCanonicalName setting.

  %X Connection status when response is completed:

  X = connection aborted before the response completed.

  + = connection may be kept alive after the response is sent.

  - = connection will be closed after the response is sent.  (This
  directive was %c in late versions of Apache 1.3, but this conflicted
  with the historical ssl %{var}c syntax.)

  %I Bytes received, including request and headers, cannot be
   zero. You need to enable mod_logio to use this.

  %O Bytes sent, including headers, cannot be zero. You need to enable
   mod_logio to use this.

"""


