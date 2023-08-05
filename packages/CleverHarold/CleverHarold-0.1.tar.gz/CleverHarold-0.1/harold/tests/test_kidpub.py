#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import unittest
from harold.lib import con_type
from harold.publishers import kid_publisher
from harold.tests.lib import (test_app, make_start_response,
                              kid_template_dirs,
                              layout_template, default_templates, wsgi_env)


class FsPublisher_FsKidTemplate__Test(unittest.TestCase):
    def setUp(self):
        self.headers = []
        self.publisher = kid_publisher(
            app=test_app,
            dirs=kid_template_dirs,
            layout=layout_template,
            defaults=default_templates,
            debug=True)


    def run_publisher(self, path, query='', **kwds):
        environ = wsgi_env(PATH_INFO=path, QUERY_STRING=query)
        environ.update(kwds)
        results = self.publisher(environ, make_start_response(self.headers))
        return ''.join(results)


    def test__00__content_type(self):
        """ kid template with PATH_INFO='' """
        results = self.run_publisher('')
        expected = ('content-type', con_type.html)
        headers = [(h[0].lower(), h[1].lower()) for h in self.headers]
        self.failUnless(expected in headers)


    def test__01__index(self):
        """ kid template default functions """
        results = self.run_publisher('')
        keys = ['default D', 'default C', 'index B', 'index A']
        pos = [results.index(key) for key in keys]
        self.assertEqual(sorted(pos), pos)


    def test__02__alternate_index(self):
        """ kid template default functions with PATH_INFO='/altindex' """
        results = self.run_publisher('/altindex')
        keys = ['default D', 'default C', 'default B', 'alternate A']
        pos = [results.index(key) for key in keys]
        self.assertEqual(sorted(pos), pos)

        
    def test__03__subdirectory_index(self):
        """ kid template default functions with PATH_INFO='/sub' """
        results = self.run_publisher('/sub')
        keys = ['default D', 'default C', 'subdir B', 'subdir A']
        pos = [results.index(key) for key in keys]
        self.assertEqual(sorted(pos), pos)


    def test__04__subdirectory_empty(self):
        """ kid template default functions with PATH_INFO-'/sub/empty' """
        results = self.run_publisher('/sub/empty')
        keys = ['default D', 'default C', 'default B', 'default A']
        pos = [results.index(key) for key in keys]
        self.assertEqual(sorted(pos), pos)


    def test__05__named_template_whole_file(self):
        """ kid template default and named functions with PATH_INFO='/funcs' """
        results = self.run_publisher('/funcs')
        keys = ['default D', 'default C', 'default B', 'ntf A']
        pos = [results.index(key) for key in keys]
        self.assertEqual(sorted(pos), pos)


    def test__06__ntf_no_args(self):
        """ named template function with no args """
        results = self.run_publisher('/funcs/E')
        self.assertEqual(results, '<div>ntf E</div>')


    def test__07__ntf_args_query_posargs(self):
        """ named template function with query args """
        results = self.run_publisher('/funcs/F', 'a=1&b=2')
        self.assertEqual(results, '<div>ntf F 1 2</div>')


    def test__08__ntf_query_keyargs(self):
        """ named template function with defaults and query args """
        results = self.run_publisher('/funcs/G', 'a=1&b=2')
        self.assertEqual(results, '<div>ntf G 1 2</div>')


    def test__09__ntf_args_query_posargs_keyargs(self):
        """ named template function with defaults and query args """
        results = self.run_publisher('/funcs/H', 'a=1&b=2')
        self.assertEqual(results, '<div>ntf H 1 2</div>')

        results = self.run_publisher('/funcs/H', 'a=2')
        self.assertEqual(results, '<div>ntf H 2 0</div>')


    def test__10__ntf_path_only(self):
        """ named template function with path args """
        results = self.run_publisher('/funcs/I/2/3')
        self.assertEqual(results, '<div>ntf I 2 3</div>')


    def test__11__ntf_path_query_mix(self):
        """ named template function with path and query mixed """
        results = self.run_publisher('/funcs/J/0', 'b=1')
        self.assertEqual(results, '<div>ntf J 0 1</div>')


    def test__12__ntf_path_query_mix(self):
        """ named template function with defaults, path and query """
        results = self.run_publisher('/funcs/K/0', 'b=1')
        self.assertEqual(results, '<div>ntf K 0 1</div>')


    def test__13__ntf_keyargs(self):
        """ named template function with keyword args """
        results = self.run_publisher('/funcs/L', 'a=slug')
        for key in ['slug', 'cookies', 'environ', 'publisher', 'form']:
            self.failUnless(key in results)


    def test__14__ntf_posargs_keyargs_query(self):
        """ named template function with positional and keyword args """
        results = self.run_publisher('/funcs/M', 'a=slug')
        self.failUnless('slug' in results)
        for key in ['cookies', 'environ', 'publisher', 'form']:
            self.failUnless(key in results)


    def test__15__ntf_posargs_keyargs_defaults_query(self):
        """ named template function with positional, defaults, and keyword args """
        results = [
            self.run_publisher('/funcs/N/snail/slug'),
            self.run_publisher('/funcs/N/slug', 'b=snail'),
            self.run_publisher('/funcs/N/snail', 'b=slug'),
            self.run_publisher('/funcs/N', 'a=snail&b=slug'),
        ]

        keys = [
            'juice', 'snail', 'slug', 'cookies', 'environ',
            'publisher', 'form'
        ]
        for key in keys:
            for result in results:
                self.failUnless(key in result)


    def test__16__nmf_noargs(self):
        """ named module function with no args """
        results = self.run_publisher('/funcs/P')
        self.assertEqual(results, 'P')


    def test__17__nmf_posarg(self):
        """ named module function with positional arg """
        results = [
            self.run_publisher('/funcs/Q', 'a=1'),
            self.run_publisher('/funcs/Q/1'),
            ]
        for result in results:
            self.assertEqual(result, 'Q 1')
        

    def test__18__nmf_posargs(self):
        """ named module function with two positional args """
        results = [
            self.run_publisher('/funcs/R', 'a=1&b=2'),
            self.run_publisher('/funcs/R/1', 'b=2'),            
            self.run_publisher('/funcs/R/1/2'),
            ]
        for result in results:
            self.assertEqual(result, 'R 1 2')


    def test__19__nmf_defaults(self):
        """ named module function with default positional args """
        results = [
            self.run_publisher('/funcs/S/1'),
            self.run_publisher('/funcs/S', 'a=1'),
            ]
        for result in results:
            self.assertEqual(result, 'S 1 0')
        
        results = [
            self.run_publisher('/funcs/S', 'a=1&b=2'),
            self.run_publisher('/funcs/S/1', 'b=2'),            
            self.run_publisher('/funcs/S/1/2'),
            ]
        for result in results:
            self.assertEqual(result, 'S 1 2')


    def test__20__nmf_kwargs(self):
        """ named module function with positional and keyword args """
        results = [
            self.run_publisher('/funcs/T', 'a=slug&b=snail'),
            self.run_publisher('/funcs/T/slug', 'b=snail'),
            self.run_publisher('/funcs/T/snail', 'b=slug'),
            ]
        for result in results:
            self.failUnless('slug' in result)
            self.failUnless('snail' in result)


    def test__21__nmf_extraposargs(self):
        """ named module function with extra positional arg """
        results = [
            self.run_publisher('/funcs/U', 'b=slug&b=snail'),
            ]
        for result in results:
            self.failUnless('slug' in result)
            self.failUnless('snail' in result)


    def test__22__nmf_posargs_extraposargs(self):
        """ named module function with positional and extra positional arg """
        results = [
            self.run_publisher('/funcs/V/sloth', 'b=slug&b=snail'),
            self.run_publisher('/funcs/V/sloth/slug/snail', ''),
            self.run_publisher('/funcs/V/', 'a=sloth&b=slug&b=snail'),
            ]
        for result in results:
            self.failUnless('sloth' in result)            
            self.failUnless('slug' in result)
            self.failUnless('snail' in result)


    def test__23__nmf_posargs_extraposargs_keywordargs(self):
        """ named module function with positional, extra positional, and keyword args """
        run = self.run_publisher
        results = [
            run('/funcs/W/sloth', 'b=slug&b=snail'),
            run('/funcs/W/sloth/slug/snail', ''),
            run('/funcs/W/', 'a=sloth&b=slug&b=snail'),
            run('/funcs/W/sloth', 'c=slug&d=snail'),
            run('/funcs/W/sloth/slug', 'b=snail'),
            ]
        for result in results:
            self.failUnless('sloth' in result)            
            self.failUnless('slug' in result)
            self.failUnless('snail' in result)


if __name__ == '__main__':
    unittest.main()
