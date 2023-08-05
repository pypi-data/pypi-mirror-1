#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# This module defines the MarkdownTemplate class to pulish
# markdown_ markup from the filesystem.  Requires markdown.py_
#
# .. _markdown: http://daringfireball.net/projects/markdown/
# .. _markdown.py: http://www.freewisdom.org/projects/python-markdown/
#
##

from harold.publishers.common import (default_helper, make_view,
                                      TemplateMixin)

try:
    from markdown import markdown
except (ImportError, ):
    def markdown(value):
        return markdown_not_installed % (value, )


markdown_not_installed = """
<div>
<h1>Markdown Not Installed - Rendering Not Available</h1>
<p>Install markdown.py from
<a href="http://www.freewisdom.org/projects/python-markdown/">
http://www.freewisdom.org/projects/python-markdown/
</a>.
</p>
<h2>Raw File Contents</h2>
<pre>%s</pre>
</div>
"""


class MarkdownTemplate(TemplateMixin):
    """ Class to publish text files with Markdown markup

    """
    ext = '.txt'
    index = 'index.txt'

    def render(self, filename, args):
        """ renders contents of Markdown text file

        @param filename name of file as found by the publisher
        @param args trailing path arguments if any
        @return rendered file as html
        """
        app = self.app
        text = open(filename).read()
        markup = markdown(text)
        helper_template = self.kwds.get('helper_template', default_helper)
        source = helper_template % (markup, )
        module = make_view(source, layout=app.layout, defaults=app.defaults,
                           cache=not app.debug)
        output = self.kwds.get('output', 'html')
        context = self.context()()
        return module.serialize(output=output, **context)
