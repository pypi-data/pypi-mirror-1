#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# This module defines the ReStructuredTextTemplate class to pulish
# reStructuredText_ markup from the filesystem.  Requires Docutils_.
#
# .. _reStructuredText: http://docutils.sourceforge.net/rst.html
# .. _Docutils: http://docutils.sourceforge.net/index.html
#
##

from harold.publishers.common import (default_helper, make_view,
                                      TemplateMixin)

try:
    from docutils.core import publish_parts
except (ImportError, ):
    def publish_parts(value, **kwds):
        return {'body': docutils_not_installed % (value, )}


docutils_not_installed = """
<div>
<h1>Docutils Not Installed - Rendering Not Available</h1>
<p>Install docutils from
<a href="http://docutils.sourceforge.net"/>http://docutils.sourceforge.net</a>.
</p>
<h2>Raw File Contents</h2>
<pre>%s</pre>
</div>
"""


class ReStructuredTextTemplate(TemplateMixin):
    """ Class to publish reStructuredText files

    """
    ext = '.txt'
    index = 'index.txt'

    def render(self, filename, args):
        """ renders contents of restructured text file

        @param filename name of file as found by the publisher
        @param args trailing path arguments if any
        @return rendered file as html
        """
        app = self.app
        text = open(filename).read()
        markup = publish_parts(text, writer_name='html')['html_body']
        helper_template = self.kwds.get('helper_template', default_helper)
        source = helper_template % (markup, )
        module = make_view(source, layout=app.layout, defaults=app.defaults,
                           cache=not app.debug)
        output = self.kwds.get('output', 'html')
        context = self.context()()
        return module.serialize(output=output, **context)
