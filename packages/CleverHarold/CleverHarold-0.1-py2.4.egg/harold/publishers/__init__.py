#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# The harold.publishers package provides WSGI middleware for
# publishing templates and markup from the filesystem.
#
# Synopsis
# --------
#
# Use like this in a python module::
#
#    from harold.publishers import code_pubilsher, kid_publisher
#    from mypackage import my_app
#    from paste import httpserver
#
#    app = my_app()
#
#    app = kid_publisher(app, ['/path', '/otherpath'],
#                        layout='mypackage.views.layout',
#                        defaults=('mypackage.views.defaults',
#                                  'mypackage.views.extras'))
#
#    app = code_publisher(app, ['/path', '/codepath'],
#                         layout='mypackage.views.altlayout',
#                         defaults=('mypackage.views.altdefaults',
#                                   'mypackage.views.altextras'))
#
#    if __name__ == '__main__':
#        httpserver.serve(app)
#
#
# Or use like this in a paster configuration (other required sections
# omitted)::
#
#    [filter:my_kid_templates]
#    use = egg:CleverHarold#kid_publisher
#    dirs = /path /otherpath
#    layout = mypackage.views.layout
#    defaults = mypackage.views.defaults mypackage.views.extras
#
#    [filter:my_code_modules]
#    use = egg:CleverHarold#code_publisher
#    dirs = /path /codepath
#    layout = mypackage.views.altlayout
#    defaults = mypackage.views.altdefaults mypackage.views.altextras
# 
##

from harold.publishers.common import Publisher
from harold.publishers.cheetahtemplate import CheetahTemplate
from harold.publishers.kidtemplate import KidTemplate
from harold.publishers.markdowntext import MarkdownTemplate
from harold.publishers.pythonmodule import CodeTemplate
from harold.publishers.rstext import ReStructuredTextTemplate


def cheetah_publisher(app, dirs, debug=True):
    """ Factory function to create a new Publisher with a
    CheetahTemplate template type.

    @param app contained WSGI application; called when no template matches request
    @param dirs sequence of file system directories to search for templates
    @keyparam debug publisher debug setting
    @return Publisher with CheetahTemplate template type
    """
    return Publisher(
        app=app,
        template_type=CheetahTemplate,
        dirs=dirs,
        layout='',
        defaults='',
        debug=debug)


def code_publisher(app, dirs, layout='', defaults=(), debug=True):
    """ Factory function to create a new Publisher with a CodeTemplate
    template type.

    @param app contained WSGI application; called when no template matches request
    @param dirs sequence of file system directories to search for templates
    @keyparam layout named layout template
    @keyparam defaults sequence of named default templates
    @keyparam debug publisher debug setting
    @return Publisher with CodeTemplate template type
    """
    return Publisher(
        app=app,
        template_type=CodeTemplate,
        dirs=dirs,
        layout=layout,
        defaults=defaults,
        debug=debug)


def kid_publisher(app, dirs, layout='', defaults=(), debug=True, output='html'):
    """ Factory function to create a new Publisher with a KidTemplate
    template type.

    @param app contained WSGI application; called when no template matches request
    @param dirs sequence of file system directories to search for templates
    @keyparam layout named layout template
    @keyparam defaults sequence of named default templates
    @keyparam debug publisher debug setting
    @keyparam output kid template output type; specify 'html' (default) or 'xml'
    @return Publisher with KidTemplate template type
    """
    return Publisher(
        app=app,
        template_type=KidTemplate,
        dirs=dirs,
        layout=layout,
        defaults=defaults,
        debug=debug,
        output=output)


def markdown_publisher(app, dirs, layout='', defaults=(), debug=True, output='html'):
    """ Factory function to create a new Publisher with a
    MarkdownTemplate template type.

    @param app contained WSGI application; called when no template matches request
    @param dirs sequence of file system directories to search for templates
    @keyparam layout named layout template
    @keyparam defaults sequence of named default templates
    @keyparam debug publisher debug setting
    @keyparam output template output type; specify 'html' (default) or 'xml'
    @return Publisher with MarkdownTemplate template type
    """
    return Publisher(
        app=app,
        template_type=MarkdownTemplate,
        dirs=dirs,
        layout=layout,
        defaults=defaults,
        debug=debug,
        output=output)


def rest_publisher(app, dirs, layout='', defaults=(), debug=True, output='html'):
    """ Factory function to create a new Publisher with a
    ReStructuredTextTemplate template type.

    @param app contained WSGI application; called when no template matches request
    @param dirs sequence of file system directories to search for templates
    @keyparam layout named layout template
    @keyparam defaults sequence of named default templates
    @keyparam debug publisher debug setting
    @keyparam output template output type; specify 'html' (default) or 'xml'
    @return Publisher with ReStructuredTextTemplate template type
    """
    return Publisher(
        app=app,
        template_type=ReStructuredTextTemplate,
        dirs=dirs,
        layout=layout,
        defaults=defaults,
        debug=debug,
        output=output)
