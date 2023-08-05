#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>


import re
import unittest
from harold.lib import con_type
from harold.publishers import cheetah_publisher
from harold.tests.lib import (test_app, make_start_response,
                              tmpl_template_dirs,
                              layout_template, default_templates, wsgi_env)


class CheetahTemplate__Test(unittest.TestCase):
    link = '<a href="http://en.wikipedia.org/wiki/Hyperlink"'.lower()
    content = '<p>This is content.\s*</p>'.lower()
    heading = '<h1>Titles Are Not Removed</h1>'.lower()
    subheading = '<h2>This is a subheading</h2>'.lower()
    item = '<li>\s*An Item\s*</li>'.lower()

    first_arg = '<p>First extra path arg is: 1</p>'
    second_arg = '<p>Second extra path arg is: 2</p>'

    query_a = '<p>Query key a is: 1</p>'
    query_b = '<p>Query key b is: 2</p>'

    def_content = 'This is the text of the inner method.\n1, 2, 3'
    
    def setUp(self):
        self.headers = []
        self.publisher = cheetah_publisher(
            app=test_app,
            dirs=tmpl_template_dirs,
            debug=True)


    def run_publisher(self, path, query='', **kwds):
        environ = wsgi_env(PATH_INFO=path, QUERY_STRING=query)
        environ.update(kwds)
        results = self.publisher(environ, make_start_response(self.headers))
        return ''.join(results)


    def check_results(self, txt):
        exprs = (self.link, self.content, self.item, self.heading,
                 self.subheading)
        for expr in exprs:
            expr = re.compile(expr)
            self.failUnless(expr.search(txt))

    def test__00__content_type(self):
        """ cheetah template with PATH_INFO='' """
        results = self.run_publisher('')
        expected = ('content-type', con_type.html)
        headers = [(h[0].lower(), h[1].lower()) for h in self.headers]
        self.failUnless(expected in headers)

        
    def test__01__index(self):
        """ cheetah template index """
        results = self.run_publisher('')
        self.check_results(results.lower())


    def test__02__alternate_index(self):
        """ cheetah template with PATH_INFO='/altindex' """
        results = self.run_publisher('/altindex')
        self.check_results(results.lower())

    def test__03__args(self):
        """ cheetah template with PATH_INFO='/requester' and extra path args """
        results = self.run_publisher('/requester/a/b')
        self.failUnless(self.first_arg in results)
        self.failUnless(self.second_arg in results)

    def test__03__args(self):
        """ cheetah template with PATH_INFO='/path_only' and extra path args """
        results = self.run_publisher('/path_only/1/2')
        self.failUnless(self.first_arg in results)
        self.failUnless(self.second_arg in results)

    def test__04__query(self):
        """ cheetah template with PATH_INFO='/query_only' and query string """
        results = self.run_publisher('/query_only', QUERY_STRING='a=1&b=2')
        self.failUnless(self.query_a in results)
        self.failUnless(self.query_b in results)

    def test__05__context(self):
        """ cheetah template with PATH_INFO='/context_full' and many extras """
        results = self.run_publisher('/context_full/1/2', QUERY_STRING='a=1&b=2')
        self.failUnless(self.first_arg in results)
        self.failUnless(self.second_arg in results)
        self.failUnless(self.query_a in results)
        self.failUnless(self.query_b in results)

    def test__06__def_path(self):
        """ cheetah template with PATH_INFO=/has_defs/inner/1/2/3 """
        results = self.run_publisher('/has_defs/inner/1/2/3')
        self.failUnless(self.def_content in results)

    def test__07_def_query(self):
        """ cheetah template with PATH_INFO=/has_defs/inner and query string """
        results = self.run_publisher('/has_defs/inner', QUERY_STRING='a=1&b=2&c=3')
        self.failUnless(self.def_content in results)

    def test__08_def_path_query(self):
        """ cheetah template with PATH_INFO=/has_defs/inner/1/2 and query string """
        results = self.run_publisher('/has_defs/inner/1/2', QUERY_STRING='c=3')
        self.failUnless(self.def_content in results)

        
if __name__ == '__main__':
    unittest.main()
