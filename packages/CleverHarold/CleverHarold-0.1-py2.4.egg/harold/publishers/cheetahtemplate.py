#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
#
# This module defines the CheetahTemplate class to publish kid
# templates from the filesystem.
#
##

from Cheetah.Template import Template as CT
from harold.publishers.common import TemplateMixin, request_args


class CheetahTemplate(TemplateMixin):
    """ Instances read Cheetah templates and render them.

    """
    ext = '.tmpl'
    index = 'index.tmpl'

    class ref:
        src = 'non-empty string to supress warnings'
        module = CT(src)
        disallow = set(dir(module))


    def render(self, filename, args):
        """ After a template is located, the mixin calls this method
        to complete the rendering process.

        @param filename name of template module to import
        @param args sequence of additional items from the request
        @return rendered template
        """
        try:
            method_name = args.pop(0)
        except (IndexError, ):
            method_name = ''

        def simple():
            context = self.context()()
            search = [dict(args=args, form=self.form(), context=context), context]
            template = CT(file=filename, searchList=search)
            return str(template)

        if not method_name:
            return simple()

        context = self.context()
        search = [dict(args=args, form=self.form(), context=context()), context()]
        template = CT(file=filename, searchList=search)
        view_names = set(dir(template)) - self.ref.disallow

        if method_name not in view_names:
            args.insert(0, method_name)
            return simple()

        call = getattr(template, method_name)
        cargs, ckwds = request_args(call, args, self.form(), context)
        return call(*cargs, **ckwds)
