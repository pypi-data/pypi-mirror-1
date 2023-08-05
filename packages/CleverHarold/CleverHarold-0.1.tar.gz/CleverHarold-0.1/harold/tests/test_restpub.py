#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import unittest
from harold.lib import con_type
from harold.publishers import rest_publisher
from harold.tests.lib import (test_app, make_start_response,
                              rst_template_dirs,
                              layout_template, default_templates, wsgi_env)


class FsPublisher_FsReStructuredText__Test(unittest.TestCase):
    link = '<a href="http://en.wikipedia.org/wiki/Hyperlink"'.lower()
    content = '<p>This is content.</p>'.lower()
    heading = 'id="titles-are-not-removed"'.lower()
    subheading = 'id="this-is-a-subheading"'.lower()
    item = '<li>An Item</li>'.lower()
    
    def setUp(self):
        self.headers = []
        self.publisher = rest_publisher(
            app=test_app,
            dirs=rst_template_dirs,
            layout=layout_template,
            defaults=default_templates,
            debug=True)


    def run_publisher(self, path, query='', **kwds):
        environ = wsgi_env(PATH_INFO=path, QUERY_STRING=query)
        environ.update(kwds)
        results = self.publisher(environ, make_start_response(self.headers))
        return ''.join(results)


    def check_results(self, txt):
        self.failUnless(self.link in txt)
        self.failUnless(self.content in txt)
        self.failUnless(self.item in txt)        
        self.failUnless(self.heading in txt)
        self.failUnless(self.subheading in txt)


    def test__00__content_type(self):
        """ rest template with PATH_INFO='' """
        results = self.run_publisher('')
        expected = ('content-type', con_type.html)
        headers = [(h[0].lower(), h[1].lower()) for h in self.headers]
        self.failUnless(expected in headers)

        
    def test__01__index(self):
        """ rest template index """
        results = self.run_publisher('')
        self.check_results(results.lower())


    def test__02__alternate_index(self):
        """ rest template with PATH_INFO='/altindex' """
        results = self.run_publisher('/altindex')
        self.check_results(results.lower())


if __name__ == '__main__':
    unittest.main()
