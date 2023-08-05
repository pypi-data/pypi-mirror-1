#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import os
import re
import sys

from inspect import getargspec, formatargspec
from urllib import quote
from threading import RLock


class attrs:
    pass


keys = attrs()
keys.env = 'environ'
keys.form_error = 'harold.form.errors'
keys.form_value = 'harold.form.values'
keys.session = 'harold.session'
keys.session_object = 'harold.session.instance'
keys.data_connection = 'harold.db.connection'
keys.data_session = 'harold.db.session'

keys.headers = 'harold.publisher.headers'
keys.content_type = 'harold.publisher.content_type'
keys.view = 'harold.publisher.view'
keys.layout = 'harold.publisher.layout'
keys.defaults = 'harold.publisher.defaults'
keys.response_status = 'harold.publisher.response_status'


con_type = attrs()
con_type.plain = 'text/plain'
con_type.json = 'text/json'
con_type.html = 'text/html'


class ValidationError(ValueError):
    """ Named type for accurate determination """


class DecorationError(TypeError):
    """ Named type for accurate determination """


def make_annotated(function, template):
    """ create replacement callable for function using template definition

    @param function callable to wrap
    @param template template source string to interpolate and exec
    @return function replacement
    """
    args, varargs, varkw, defaults = getargspec(function)
    name = function.func_name
    docstring = function.func_doc or ''
    signature = formatargspec(args, varargs, varkw, defaults)
    values = formatargspec(args, varargs, varkw)
    execmap = {}
    exec template % locals() in execmap
    return execmap[name]


def request_path(environ, query_string=True):
    """ reconstructs path portion of requested url from wsgi environment

    @param environ wsgi request environment
    @keyparam query_string include available query string if True (default)
    @return original url path path as string
    """
    get = environ.get
    url = quote(get('SCRIPT_NAME', ''))
    url += quote(get('PATH_INFO', ''))
    query = get('QUERY_STRING')
    if query_string and query:
        url += '?' + query
    return url


synchro_anno_template = """
def %(name)s%(signature)s:
    %(docstring)r
    return %(name)s.func_synchro%(values)s
"""


def synchronized(original):
    """ creates and returns a synchronized, thread-safe method

    @param original method to synchronized
    @return synchronized, thread-safe wrapper around original
    """
    def synchro_anno(self, *args, **kwds):
        try:
            lock = self.__lock
        except (AttributeError, ):
            lock = self.__lock = RLock()
        lock.acquire()
        try:
            return original(self, *args, **kwds)
        finally:
            lock.release()

    replacement = make_annotated(original, synchro_anno_template)
    replacement.func_synchro = synchro_anno
    return replacement


def is_iterator(obj):
    """ Returns True if obj supports the iterator protocol

    @param obj item to inspect for iterator protocol support
    @return True if obj supports iterator protocol, False if does not
    """
    return hasattr(obj, 'next') and hasattr(obj, '__iter__')


def import_wrapper(name):
    """ Loads and returns module indicated by dotted package name

    This function is copy+pasted from the python docs.  See Python
    Library Reference, section 2.1, `Built-in Functions`_.

    .. _`Built-in Functions`: http://docs.python.org/lib/built-in-funcs.html

    @param name module name in dotted string form
    @return module object
    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def import_attribute(name, separator=':'):
    """ Returns attribute indicated by dotted package name + ':attribute'.

    @param name package and attribute, in the form of pkg.subpkg.mod:attribute
    @param separator string used to split attribute from package name
    @return attribute from module
    """
    module_name, attr_name = name.split(separator)
    return getattr(import_wrapper(module_name), attr_name)


def headers_response_hook(original, sequence):
    """ Returns a closure around original that extends copy with headers

    @param original original start_response method
    @param sequence sequence to fill with headers
    @return function suitable to replace original
    """
    def hook(status, headers, exc_info=None):
        sequence.extend(headers)
        return original(status, headers, exc_info)
    return hook


def mapping_response_hook(original, mapping):
    """ Returns a closure around original that updates mapping with response

    @param original original start_response method
    @param mapping dictionary to fill with status and headers
    @return function suitable to replace original
    """
    mapping['status'] = mapping['headers'] = mapping['info'] = None
    
    def hook(status, headers, exc=None):
        mapping['status'] = status
        mapping['headers'] = headers[:]
        mapping['exc_info'] = exc
        return original(status, headers, exc)
    return hook


def header_match(key, value):
    """ Returns a closure to match key and value to headers

    @param key regular expression used to match header name
    @param value regular expression used to match header value
    @return function that will select specified header from sequence
    """
    key = re.compile(key, re.I).match
    value = re.compile(value, re.I).match
    
    def inner(headers):
        for name, setting in headers:
            if key(name) and value(setting):
                return (name, setting)
    return inner


def config_expression(value, prefix='python:'):
    """ evaluates string as an expression if prefixed 

    @param value string from paster config file
    @param prefix expression prefix; default is 'python:'
    @return value as string or evaluated expression
    """
    if isinstance(value, basestring) and value.startswith(prefix):
        value = value[len(prefix):]
        try:
            global_map = local_map = {}
            value = eval(value, global_map, local_map)
        except (SyntaxError, ):
            raise
    return value


def detect_config():
    """ locates reasonable default configuration filename

    @return project .ini file, first .ini file found, or ''
    """
    cwd = os.getcwd()
    proj_name = os.path.split(cwd)[-1]
    proj_ini = os.path.join(cwd, proj_name + '.ini')

    if os.path.exists(proj_ini):
        return proj_ini

    files = [name for name in os.listdir(cwd) if name.endswith('.ini')]
    if files:
        files.sort()        
        return os.path.join(cwd, files[0])


def detect_runtime_config():
    """ locates config filename specified on the command line

    @return project .ini file if present in sys.argv, or None
    """
    argv = getattr(sys, 'argv', [])
    files = [os.path.abspath(v) for v in argv]
    config = detect_config()
    if config in files:
        return config
