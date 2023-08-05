#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
#
# This module defines the CodeTemplate class to publish
# callable code from the fileystem.
#
##

import imp
import os
import sys
import types

from harold.lib import import_wrapper, keys
from harold.log import logger
from harold.publishers.common import (request_args, publishable_items,
                                      TemplateMixin, )


class CodeTemplate(TemplateMixin):
    """ Publishs python code modules

    Instances of this template type execute code within python modules
    by importing their files and mapping the request parameters to the
    module contents.  Instances of this class can publish functions and
    classes.  In the cases of classes, instances are first created, and
    either the instances __call__ method or other named method will be
    used.

    Callables within modules can be refered to directly by name, for
    example::

        /path/to/module/function

    If no function or class name is specified in the path, the REQUEST_METHOD is
    used to determine the callable, for example::

       GET /path/to/module
       POST /path/to/module

    Would map to 'get' and 'post' callables within 'module', respectively.

    Finally, if a module is refered to directly (i.e., without trailing
    path parts), instances of this class will attempt to use the first
    callable within a module with a 'default' attribute.
    """
    ext = '.py'
    index = '__init__.py'
    pub_exc = TypeError('item not publishable')


    def render(self, filename, args):
        """ Renders filename with args

        After a module is located, the mixin calls this method to
        complete the rendering process.
        
        @param filename name of file to import
        @param args sequence of additional items from the reqeust
        @return results of executed code
        @exception Exception when filename cannot be opened for reading
        """
        env = self.env
        call = results = None        
        req_method = env['REQUEST_METHOD'].lower()
        mod_inst = self.import_file(filename)
        pub_items, pub_defaults = publishable_items(mod_inst)
        
        # with no extra path arguments, the request method determines
        # the item to fetch from the module.  if the request method is
        # not named, we instead use the first default.
        if not args:
            if req_method in [key for key, val in pub_items]:
                call = getattr(mod_inst, req_method)
            elif pub_defaults:
                call = pub_defaults[-1][-1]

        # otherwise the first item in the path may refer to a callable
        # in the module, or it the entire path can be parameters to
        # one of the default functions.
        else:
            try:
                call = [val for key, val in pub_items if key == args[0]][0]
                args = args[1:]                
            except (IndexError, ):
                if req_method in [key for key, val in pub_items]:
                    call = getattr(mod_inst, req_method)
                elif pub_defaults:
                    call = pub_defaults[-1][-1]

        query = self.form()
        context = self.context()
        if isinstance(call, (types.ClassType, types.TypeType, )):
            results = self.execute_class(call, args, query, context)
        else:
            results = self.execute_plain(call, args, query, context)
        self.report_callable(call, env)
        return results


    def execute_class(self, cls, args, query, context):
        """ Creates and calls an instance of cls

        This implementation isn't the best.
        
        @param cls class object
        @param args positional (path) arguments to function
        @param query mapping with query string keywords
        @param context extra contextual values
        @return results of executing call with arguments
        @exception TypeError if callable cannot be inspected for arguments
        """
        init = getattr(cls, '__init__', None)
        meth = meth_name = None
        exposed = cls.expose
        
        if init:
            init_args, init_kwds = request_args(init, args, query, context,
                                                ignore_additional_args=True)
            args = args[len(init_args):]
            if args and getattr(cls, args[0], None) and args[0] not in exposed:
                raise self.pub_exc
            obj = cls(*init_args, **init_kwds)
        else:
            if args and args[0] not in exposed:
                raise self.pub_exc
            obj = cls()

        check_meth = getattr(obj, '__call__', None)
        if check_meth:
            meth_name = '__call__'
            meth = check_meth

        if args:
            check_meth = getattr(obj, args[0], None)
            if check_meth:
                meth_name = args.pop(0)
                meth = check_meth

        if meth:
            if not meth_name in cls.expose:
                raise self.pub_exc
            meth_args, meth_kwds = request_args(meth, args, query, context,
                                                ignore_additional_args=True)
            result = meth(*meth_args, **meth_kwds)
        else:
            result = obj
        return result


    def execute_plain(self, call, args, query, context):
        """ Executes call with args, query and context
        
        @param call method or function object
        @param args positional (path) arguments to function
        @param query mapping with query string keywords
        @param context extra contextual values
        @return results of executing call with arguments
        @exception TypeError if callable cannot be inspected for arguments
        """
        try:
            cargs, ckwds = request_args(call, args,
                                        query=query, context=context,
                                        ignore_additional_args=False)
        except (TypeError, ):
            raise self.pub_exc
        return call(*cargs, **ckwds)


    def report_callable(self, call, environ):
        """ Decorates a WSGI environment with call attributes

        @param call class, type, method, or function
        @param environ WSGI request environment
        @return None
        """
        class marker:
            pass
        pairs = (('content_type', keys.content_type),
                 ('view', keys.view),
                 ('layout', keys.layout),
                 ('defaults', keys.defaults))
        for name, key in pairs:
            value = getattr(call, name, marker)
            if value is not marker:
                environ[key] = value


    def import_file(self, filename):
        """ imports a module by filename

        @param filename name of module to import
        @return module instance
        """
        mod_inst = None
        verbose = self.app.debug
        try:
            mod_inst = self.cache[filename]
            self.log.debug('cached module %s', mod_inst)
        except (KeyError, ):
            mod_parts = filename[:-len(self.ext)].split(os.path.sep)
            mod_parts = [part for part in mod_parts if part]
            mod_name = os.path.split(filename[:-3])[1] + '_0x%x' % hash(filename)

            try:
                mod_inst = sys.modules[mod_name]
                self.log.debug('module %s from sys.modules', mod_name)
            except (KeyError, ):
                pass

            while mod_parts and not mod_inst:
                try:
                    imp_name = str.join('.', mod_parts)
                    mod_inst = import_wrapper(imp_name)
                    self.log.debug('imported %s', imp_name)
                except (ImportError, ):
                    mod_parts.pop(0)

            if not mod_inst:
                mod_inst = imp.new_module(mod_name)
                execfile(filename, mod_inst.__dict__)
                mod_inst.__file__ = filename
                sys.modules[mod_name] = mod_inst
                self.log.debug('execfile %s into %s', filename, mod_name)

            self.cache[filename] = mod_inst
        return mod_inst


    def walk(self, dirname):
        for (dirpath, dirnames, filenames) in os.walk(dirname):
            for filename in filenames:
                namepart, ext = os.path.splitext(filename)
                if ext == self.ext:
                    filename = os.path.join(dirpath, filename)

                    try:
                        mod_fh = open(filename, 'r')
                    except (IOError, ):
                        raise Exception('iofault')

                    try:
                        ## something nicer for mod_name ?
                        mod_inst = self.import_file(filename)
                    finally:
                        mod_fh.close()

                    items, pub_defaults = publishable_items(mod_inst)
                    yield (filename, items)

