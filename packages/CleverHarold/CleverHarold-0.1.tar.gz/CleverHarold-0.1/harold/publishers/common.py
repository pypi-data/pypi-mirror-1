#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
#
# This module provides support common to all harold publishers.
#
##

from inspect import getargspec, getfile, getsource, ismodule
from itertools import chain
from os import path
from sys import maxint
from threading import local
from xml.dom.minidom import parse as parse_dom
from xml.dom.minidom import parseString as parse_dom_string

from kid import load_template, enable_import, xml_sniff
from simplejson import dumps as jsonify

from paste.httpexceptions import HTTPException
from paste.request import parse_formvars as parse_form
from paste.request import get_cookies as parse_cookies
from paste.wsgiwrappers import WSGIRequest

from harold.lib import import_wrapper, keys, con_type
from harold.log import logger


## turn on the kid import hook for 'package.subpackage.template' style
## defaults, layouts, and views.
enable_import()


class Publisher:
    """ Type for associating WSGI requests with concrete template type
    instances.

    @param app contained WSGI application; called when no template matches request
    @param template_type class or factory function for creating template publishers
    @param dirs sequence of directories to search for template files
    @param layout named template for layout of publisher results
    @param defaults sequence of named templates for default publisher values
    @param debug publisher debug setting
    @param **kwds keyword arguments passed to template type
    """
    def __init__(self, app, template_type, dirs, layout, defaults, debug, **kwds):
        self.app = app
        self.template_type = template_type
        self.dirs = dirs
        self.layout = layout
        self.defaults = defaults
        self.debug = debug
        self.kwds = kwds
        self.log = logger(self.template_type)


    def __call__(self, environ, start_response):
        """ Called by server to process a WSGI request

        @param environ WSGI environment
        @param start_response callable to initiate response
        @return rendered template body or self.app(environ, start_response)
        """
        environ[keys.headers] = []
        call = self.template_type(self, environ, **self.kwds)
        try:
            try:
                body = call()
            except (HTTPException, ), exc:
                body = exc.html(environ)
                environ[keys.response_status] = '%s %s' % (exc.code, exc.title)
        except (StopRecursion, ):
            self.log.debug('no match for %s', environ['PATH_INFO'])
            return self.app(environ, start_response)
        return self.response(environ, start_response, body)


    def response(self, environ, responder, result, content_type=con_type.html):
        """ Post-process template results and start response.

        The content-type setting is not what I want, but this will do for now.

        @param environ WSGI environment
        @param responder callable to initiate response
        @param result results of template type instance
        @keyparam content_type default response content type; possibly
        overridden by environ
        """
        content_type = environ.get(keys.content_type, content_type)
        status = environ.get(keys.response_status, '200 OK')
        view = environ.get(keys.view, None)
        layout = environ.get(keys.layout, self.layout)
        defaults = environ.get(keys.defaults, self.defaults)

        ## explicit support for json content type.  this makes
        ## indicating results should be json encoded simple and
        ## intuitive.  this block should maybe set view=None, dunno.
        if content_type == con_type.json:
            if con_type.json not in environ.get('HTTP_ACCEPT', ''):
                content_type = con_type.plain
            result = jsonify(result)

        ## make and render a view for the response.  rely on the
        ## supplied content type (or the default).
        if view:
            if not isinstance(result, (dict, )):
                result = dict(result=result)
            result.update(dict(session=environ[keys.session], environ=environ))
            try:
                output = content_type.split('/')[1]
                if output.endswith('xml'):
                    output = 'xml'
            except (ValueError, IndexError, ):
                output = 'html'
            template = make_view(view, layout, defaults, cache=not self.debug)
            result = template.serialize(output=output, **result)

        ## TODO:  add content-length here
        headers = environ[keys.headers]
        headers.append(('content-type', content_type))
        responder(status, headers)
        return [result, ]


    def walk(self):
        environ = {}
        template = self.template_type(self, environ)
        iters = [template.walk(appdir) for appdir in self.dirs]
        pathiter = chain(*iters)
        return pathiter


class StopRecursion(StopIteration):
    """ Used by template types to indicate no match found """


class TemplateMixin:
    """ Mixin class that provides functionality common to all template
    types.

    Subclasses must provide attributes 'ext' and 'index' and also must
    implement the 'render(path, filename)' method.

    Ignoring SCRIPT_INFO, and given a url such as this::

        /alpha/beta/charlie/delta/echo

    The callable matches files on the file system by searching each
    directory specified in the self.app.dir sequence.  A file is
    selected for publishing with:

    1.  an exact match of app_dir + /alpha/beta/charlie/delta/echo +
        ext.  Example::

            /tmp/alpha/beta/charlie/delta/echo.kid

    2.  a partial match of app_dir + path_part + ext from left to
        right.  Examples::

            /tmp/alpha/beta.kid
            /tmp/alpha/beta/charlie.kid
            /tmp/alpha/beta/charlie/delta.kid

    3.  a match of app_dir + path_part + index from left to right.  Examples::

            /tmp/alpha/index.kid
            /tmp/alpha/beta/index.kid
            /tmp/alpha/beta/charlie/__init__.py

    In each of these examples the extra path arguments are passed to the
    subclass for use as method names and/or parameters.

    @param app parent application; should be a Publisher instance
    @param env WSGI environment
    @param **kwds additional keyword parameters
    """
    threadlocal = local()
    cache = threadlocal.cache = {}

    def __init__(self, app, env, **kwds):
        self.app = app
        self.env = env
        self.kwds = kwds
        self.log = logger(self)


    def __call__(self):
        """ Renders a template

        @return rendered template
        @exception StopRecursion when no match found
        """
        exists = path.exists
        join = path.join
        env = self.env
        file_ext = self.ext
        index_name = self.index

        path_parts = path_info = env['PATH_INFO']
        path_parts = [val for val in path_parts.split('/') if val]
        match = None

        if not path_parts:
            path_offsets = [0, ]
        else:
            path_offsets = range(len(path_parts), 0, -1)

        for app_dir in self.app.dirs:
            if match:
                break

            for path_idx in path_offsets:
                path_prefix = join(app_dir, *path_parts[0:path_idx])
                
                look_name = path_prefix + file_ext
                if exists(look_name):
                    match = (look_name, path_parts[path_idx:], )
                    break

                look_name = join(path_prefix, index_name)                
                if exists(look_name):
                    match = (look_name, path_parts[path_idx:], )
                    break
                    
        if match:
            self.log.debug('matched %s to %s',
                           env.get('SCRIPT_NAME', '') + path_info or '/',
                           match[0])
            return self.render(match[0], match[1])
        raise StopRecursion()


    def context(self):
        """ Creates a closure for lazy construction of request context

        @return callable to construct and return the actual context mapping
        """
        def opener():
            """ a small closure for the client to pop open for goodies """
            ctx = dict(
                application=self.app,
                cookies=self.cookies(),
                publisher=self,
                environ = self.env,
                form=self.form(),
                request=self.request(),
                session=self.session(),
            )
            return ctx
        return opener


    def cookies(self):
        """ Parses and returns cookies from environ

        """
        cookies = parse_cookies(self.env)
        return cookies


    def form(self):
        """ Parses and returns query string / posted form dictionary

        """
        form = parse_form(self.env)
        return form.mixed()


    def request(self):
        """ Creates and returns new WSGIRequest object 

        """
        request = WSGIRequest(self.env)
        return request


    def session(self):
        """ Returns session object from environ

        """
        key = keys.session
        try:
            session = self.env[key] = self.env[key]()
        except (TypeError, ):
            session = self.env[key]
        except (KeyError, ):
            session = {}
        return session


##
# String template that wraps text in a py:def

default_helper = """
<html xmlns:py='http://purl.org/kid/ns#'>
<div py:def='main()'>%s</div>
</html>
"""


def string_template_name(text):
    """ Creates a name for a given template as string

    @param text xml template source, module, or filename
    @return generated template name if text is xml, empty string otherwise
    """
    if xml_sniff(text):
        return 'template_%s' % (hash(text) + maxint + 1)
    else:
        return ''


def load_template_flex(source, encoding, cache):
    """ Loads a kid template flexibly

    @param source module object, module name, file name, or xml source
    @param encoding encoding value passed to load_template
    @param cache cache value passed to load_template
    @return template module or None
    """
    if not source:
        return None
    if ismodule(source):
        return source
    try:
        name = string_template_name(source)
        full = (name and 'kid.util.' + name or '')
        tmpl = load_template(source, name=full, encoding=encoding, cache=cache)
        if full:
            import kid.util
            setattr(kid.util, name, tmpl)
        return tmpl
    except (Exception, ):
        return import_wrapper(source)


def make_view(view, layout=None, defaults=(), encoding='utf-8', cache=False):
    """ Make a kid template from view, with optional layout and defaults

    @param view module object, module name, or file name
    @param layout template reference that, if provided, is extended with view
    @param defaults sequence of template references that, if provided, are extended by view
    @return template object
    """
    view_mod = load_template_flex(view, encoding, cache)
    layout_mod = load_template_flex(layout, encoding, cache)
    if layout_mod or defaults:
        view_mod = extend_view(view_mod, layout_mod, defaults, encoding, cache)
    return view_mod


def extend_view(view, layout, defaults, encoding, cache, key=u'py:extends'):
    """ Extends kid template module 'view' with layout and defaults

    @param view template module
    @param layout layout module
    @param defaults sequence of module objects, module names, and/or file names
    @return template object
    """
    if layout:
        dom = parse_dom_string(getsource(layout))
    else:
        dom = parse_dom_string(getsource(view))        

    attrs = dom.documentElement.attributes
    orig = attrs.get(key, None)
    try:
        orig = orig.value
    except (AttributeError, ):
        pass

    view_name = getfile(view)
    if view_name == '<string>':
        view_name = view.__name__
    else:
        view_name = "'%s'" % view_name
        
    if orig and layout:
        repl = "%s, %s" % (orig, view_name)
    elif orig:
        repl = orig
    elif layout:
        repl = view_name
    else:
        repl = None

    if defaults:
        extras = [load_template_flex(name, encoding, cache) for name in defaults]
        extras = str.join(', ', ["'%s'" % getfile(name) for name in extras])
        if repl:
            repl = "%s, %s" % (repl, extras)
        else:
            repl = extras
    if repl:
        attrs[key] = repl
    return load_template(dom.toxml(), encoding=encoding, cache=cache)


def publishable_items(module):
    """ Locates publishable items within a module

    This implementation filters out all objects that start with an
    underscore, and all objects without a true 'expose' attribute.

    @param module module object to scan for publishable attributes
    @return two-tuple of (publishable objects, default objects)
    """
    items = [(item, getattr(module, item)) for item in dir(module)
                                if not item.startswith('_')]
    items = [(item, obj) for item, obj in items
                                if getattr(obj, 'expose', False)]
    defaults = [(item, obj) for item, obj in items
                                if getattr(obj, 'default', None)]
    return items, defaults


##
# Some names are magic to harold.  These are them.

magic_arg_names = [
    'application',
    'environ',
    'publisher',
    'request',
    ]


class RequestParameterParser:
    """ Parsers request for (args, kwds) applicable to a callable.

    This class derives positional arguments and keywords arguments for
    the supplied function 'func'.  The arguments are based on path,
    query, context, and default values.

    To use the class, create and instance and call it.  The 'parse'
    method is provided for one-step convenience, and that method is
    bound to a module global for even easier use.

    Straight from the inspect docs (almost):
       
        - posarg_names is a list of positional args and default positional args
        - vararg_name is the name of the excess positional argument (or None)
        - kwarg_name is the name of the excess keyword argument (or None)
        - default_vals is a list with default values of the right-most posarg_names

    The general approach is to consume the path, assign its values to
    function formal arguments left-to-right, and fill in any extra
    positional parameters and keyword parameters as approprite.

    Default values are respected when values aren't given, but extra
    values in the path or in the query raise a TypeError by default.
    This behavior can be changed by passing a true value for
    'ignore_additional_args' during instance construction.

    This class makes no attempt at dealing with implict tuples in
    formal arguments, i.e., you're on your own for functions like this
    one::

        F(a, (b, c), d)

    @param func callable target to inspect for argument mapping

    @param path request path

    @param query additional query string or posted form arguments

    @keyparam context if supplied, called to provide additional
    argument mapping

    @keyparam ignore_additional_args if False (the default), will
    cause TypeErrors with too many arguments supplied

    @keyparam ignore_self_arg if True (the default), will treat not
    map leading self argument
    """
    def __init__(self, func, path, query, context=None,
                 ignore_additional_args=False,
                 ignore_self_arg=True):
        self.path = path[:]
        self.query = query.copy()
        self.context = (context or dict)

        posarg_names, vararg_name, kwarg_name, default_vals = getargspec(func)
        if ignore_self_arg and posarg_names and posarg_names[0] == 'self':
            posarg_names.pop(0)

        self.posarg_names = posarg_names
        self.vararg_name = vararg_name
        self.kwarg_name = kwarg_name
        self.default_vals = default_vals

        self.ignore_additional_args = ignore_additional_args
        self.ignore_self_arg = ignore_self_arg

        self.arg_sig = (bool(posarg_names), bool(vararg_name), bool(kwarg_name))


    def __call__(self):
        """ Locates evaluation method and calls it

        @return two-tuple of (arguments, keyword arguments)
        """
        return self.arg_sig_map[self.arg_sig](self)


    @classmethod
    def parse(cls, func, path, query, context=None,
              ignore_additional_args=False, ignore_self_arg=True):
        """ Creates a request argument parser and calls it

        Parameters are the same as for the __init__ method.

        @return two-tuple of (arguments, keyword arguments)    
        """
        obj = cls(func, path, query, context, ignore_additional_args,
                  ignore_self_arg)
        return obj()


    def defaults(self):
        """ Constructs mapping of self.func defaults

        @return dictionary of default parameter values
        """
        posarg_names = self.posarg_names
        defaults = self.default_vals or ()
        return dict(zip(reversed(posarg_names), reversed(defaults)))


    def no_args(self):
        """ Called when self.func has no parameters

        This function ignores context and doesn't reference the
        (empty) defaults.

        @return two-tuple of ([], {})
        @exception TypeError if the instance has any path or query
        (and not set to ignore additional arguments).
        """
        if (self.path or self.query) and not self.ignore_additional_args:
            raise TypeError('Too many arguments')
        return [], {}


    def keyword_args(self):
        """ Called when self.func has only keyword parameters

        This function prefers query args over context values, and
        ignores the (empty) defaults.
       
        @return two-tuple of ([], keyword arguments)    
        @exception TypeError if the instance has any path and is not
        set to ignore additional arguments.
        """
        if self.path and (not self.ignore_additional_args):
            raise TypeError('Path arguments not allowed')
        kwds = {}
        kwds.update(self.context())
        kwds.update(self.query)
        return [], kwds


    def extra_args(self):
        """ Called when self.func has only extra positional parameters

        This function ignores the (empty) defaults, and it ignores the
        context values because mapping them in doesn't make much sense.

        The full path is always used as the arguments.
 
        @return two-tuple of (arguments, {})
        @exception TypeError if query is non-empty and if if the
        instance isn't set to ignore additional arguments.
        """
        args = self.path
        kwds = self.query
        vararg_name = self.vararg_name

        if vararg_name in kwds.keys():
            extras = kwds.pop(vararg_name)
            if isinstance(extras, (list, tuple)):
                extras = list(extras)
            else:
                extras = (extras, )
            args.extend(extras)
        if kwds and not self.ignore_additional_args:
            raise TypeError('Additional keywords not allowed')
        return args, {}


    def extra_args_keyword_args(self):
        """ Called when self.func has extra positional and keyword parameters

        This function ignores the (empty) defaults, and gives preference
        to the query values over the context values.
        
        @return two-tuple of (arguments, keyword arguments)
        """
        args = self.path
        context = self.context()
        kwds = {}
        query = self.query
        vararg_name = self.vararg_name

        if vararg_name in query:
            extras = query.pop(vararg_name)
            if isinstance(extras, (list, tuple)):
                extras = list(extras)
            else:
                extras = (extras, )
            args.extend(extras)
            
        kwds.update(context)
        kwds.update(query)
        return args, kwds


    def pos_args(self):
        """ Called when self.func has positional parameters only

        Path values are given priority over query values, query values
        are preferred over context values, and context values are
        favored over defaults.

        @return two-tuple of (arguments, {})
        @exception TypeError if missing parameter or if too many
        arguments given
        """
        args = []
        context = self.context()
        defaults = self.defaults()
        path = self.path
        posarg_names = self.posarg_names
        query = self.query

        for name in posarg_names:
            try:
                args.append(path.pop(0))
            except (IndexError, ):
                pass

        if path and (not self.ignore_additional_args):
            raise TypeError('Too many path arguments')

        trailing = posarg_names[len(args):]
        for name in trailing:
            if name in query:
                args.append(query[name])
                query.pop(name)
            elif name in context:
                args.append(context[name])
                context.pop(name)                
            elif name in defaults:
                args.append(defaults[name])
            else:
                raise TypeError('Missing argument')

        if query and not self.ignore_additional_args:
            raise TypeError('Too many query arguments')
        return args, {}


    def pos_args_keyword_args(self):
        """ Called when self.func has positional and keyword parameters

        Path values are given priority over query values, query values
        are preferred over context values, and context values are
        favored over defaults.

        @return two-tuple of (arguments, keyword arguments)
        @exception TypeError if missing argument, if argument given
        multiple times, or if too many arguments given
        """
        args = []
        context = self.context()
        defaults = self.defaults()
        path = self.path
        posarg_names = self.posarg_names
        query = self.query

        for name in posarg_names:
            try:
                args.append(path.pop(0))
                if name in query and self.ignore_additional_args:
                    query.pop(name)
                elif name in query:
                    raise TypeError('Multiple arguments')
            except (IndexError, ):
                if name in query:
                    args.append(query.pop(name))
                

        if path and (not self.ignore_additional_args):
            raise TypeError('Too many path arguments')

        trailing = posarg_names[len(args):]
        for name in trailing:
            if name in query:
                args.append(query[name])
                query.pop(name)
            elif name in context:
                args.append(context[name])
                context.pop(name)
            elif name in defaults:
                args.append(defaults[name])
            else:
                raise TypeError('Missing argument')

        query.update(context)
        return args, query


    def pos_args_extra_args(self):
        """ Called when self.func has positional and extra positional parameters

        Path values are given priority over query values, query values
        are preferred over context values, and context values are
        favored over defaults.

        @return two-tuple of (arguments, {})
        @exception TypeError if the query cannot be completely
        consumed and the instance is set to not ignore additional
        parameters
        """
        args = []
        context = self.context()
        defaults = self.defaults()
        path = self.path
        posarg_names = self.posarg_names
        query = self.query
        vararg_name = self.vararg_name
        
        for name in posarg_names:
            try:
                args.append(path.pop(0))
            except (IndexError, ):
                pass

        trailing = posarg_names[len(args):]
        for name in trailing:
            if name in query:
                args.append(query[name])
                query.pop(name)
            elif name in context:
                args.append(context[name])
                context.pop(name)
            elif name in defaults:
                args.append(defaults[name])
            else:
                raise TypeError('Missing argument')

        if path:
            args.extend(path)

        if vararg_name in query:
            extras = query.pop(vararg_name)
            if isinstance(extras, (list, tuple)):
                extras = list(extras)
            else:
                extras = (extras, )
            args.extend(extras)
            
        if query and not self.ignore_additional_args:
            raise TypeError('Too many query arguments')
        return args, {}


    def pos_args_extra_args_keyword_args(self):
        """ Called when self.func has positional, extra positional,
        and keyword parameters

        Path values are given priority over query values, query values
        are preferred over context values, and context values are
        favored over defaults.

        @return two-tuple of (arguments, keyword arguments)
        @exception TypeError if missing argument
        """
        args = []
        context = self.context()
        defaults = self.defaults()
        path = self.path
        posarg_names = self.posarg_names
        query = self.query
        vararg_name = self.vararg_name
        
        for name in posarg_names:
            if name in query:
                args.append(query.pop(name))
                continue
            try:
                args.append(path.pop(0))
            except (IndexError, ):
                pass

        trailing = posarg_names[len(args):]
        for name in trailing:
            if name in query:
                args.append(query[name])
                query.pop(name)
            elif name in context:
                args.append(context[name])
                context.pop(name)
            elif name in defaults:
                args.append(defaults[name])
            else:
                raise TypeError('Missing argument')

        if path:
            args.extend(path)

        if vararg_name in query:
            extras = query.pop(vararg_name)
            if isinstance(extras, (list, tuple)):
                extras = list(extras)
            else:
                extras = (extras, )
            args.extend(extras)

        query.update(context)
        return args, query

    ##
    # Argument signature map; used to associate the signature of
    # self.func with a method to map arguments to it.
    arg_sig_map = {
        #pos, extra, kwds
        (True, True, True) : pos_args_extra_args_keyword_args,
        (True, True, False) : pos_args_extra_args,

        (True, False, True) : pos_args_keyword_args,              
        (True, False, False) : pos_args,

        (False, True, True) : extra_args_keyword_args,
        (False, True, False) : extra_args,

        (False, False, True) : keyword_args,
        (False, False, False) : no_args,
    }


##
# Module-level callable for parsing request arguments.
request_args = RequestParameterParser.parse
