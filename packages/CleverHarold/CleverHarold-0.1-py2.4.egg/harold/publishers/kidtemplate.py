#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
#
# This module defines the KidTemplate class to publish `Kid
# Templates`_ from the filesystem.  See the `Kid User's Guide`_ and
# the `Kid Language Specification`_ for more information.
#
# .. _Kid Templates: http://kid.lesscode.org/guide.html
# .. _Kid User's Guide: http://kid.lesscode.org/index.html
# .. _Kid Language Specification: http://kid.lesscode.org/language.html
#
##

from os import walk
from os.path import join, splitext

from kid import load_template
from kid.serialization import XMLSerializer

from harold.publishers.common import (make_view, request_args, publishable_items,
                                      TemplateMixin, )


class KidTemplate(TemplateMixin):
    """ Instances of this template type import kid templates and
    render them.

    This type can publish entire templates, Named Template Functions
    with them, and also callables defined within the template that are
    publishable (i.e., marked as 'expose=True').

    In addition to rendering, instances of this class also support
    layout templates and default templates.  In the case of layout
    templates, the layout is parsed and extended with the template
    itself.  This is a reversal of the normal behavior of kid
    templates, and allows the template author to forgo the repetitious
    inclusion of common site-wide templates for layout.  In a similar
    fashion, instances will extend a view with the named default
    templates to provide a pool of pre-defined template functionality.

    Special note: Named Template Functions are always considered
    publishable because there is no simple or elegant way (that I know
    of) to add attributes to them after the are defined.  This may
    change if a better technique is found.
    """
    ext = '.kid'
    index = 'index.kid'    


    ##
    # Instances need to know what symbols are present in every kid
    # template. we provide that by creating, loading and
    # introspecting this single-element.
    
    class ref:
        src = '<x xmlns:py="http://purl.org/kid/ns#" />'
        module = load_template(src, cache=False)
        module_names = set(dir(module.Template))
        disallow = set(dir(module)) | module_names


    def render(self, filename, args):
        """ After a template is located, the mixin calls this method
        to complete the rendering process.

        @param filename name of template module to import
        @param args sequence of additional items from the request
        @return rendered template
        """
        app, env, cache = self.app, self.env, not self.app.debug
        try:
            method_name = args.pop(0)
        except (IndexError, ):
            method_name = ''

        def simple():
            context = self.context()
            view_mod = make_view(view=filename, layout=app.layout,
                                 defaults=app.defaults, cache=cache)
            output = self.kwds.get('output', 'html')
            return view_mod.serialize(output=output, **context())

        if not method_name:
            return simple()
        
        view_mod = make_view(filename, cache=cache)
        pub_items, discard = publishable_items(view_mod)
        pub_names = [item[0] for item in pub_items]

        view_names = set(dir(view_mod.Template)) - self.ref.module_names

        if (method_name not in pub_names) and (method_name not in view_names):
            args.insert(0, method_name)
            return simple()

        try:
            call = getattr(view_mod.Template(), method_name)
        except (AttributeError, ):
            call = getattr(view_mod, method_name)
            
        cargs, ckwds = request_args(call, args, self.form(), self.context())
        body = call(*cargs, **ckwds)
        
        if hasattr(body, '__iter__'):
            serializer = XMLSerializer
            body = serializer().serialize(body, fragment=1)
        return body


    def walk(self, dirname):
        for (dirpath, dirnames, filenames) in walk(dirname):
            for filename in filenames:
                namepart, ext = splitext(filename)
                if ext == self.ext:
                    filename = join(dirpath, filename)
                    template = make_view(filename)
                    items = set(dir(template.Template)) - self.ref.module_names
                    yield (filename, items)
                    
