#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import unittest
from harold.lib import con_type
from harold.publishers import code_publisher
from harold.tests.lib import wsgi_env, test_app, make_start_response, mod_template_dirs


ntf = 'named template function'
nmf = 'named module function'


class FsPublisher_FsCodeModule__Test(unittest.TestCase):
    def setUp(self):
        self.headers = []
        self.publisher = code_publisher(
            app=test_app,
            dirs=mod_template_dirs,
            debug=True)


    def run_publisher(self, path, query='', **kwds):
        environ = wsgi_env(PATH_INFO=path, QUERY_STRING=query)
        environ.update(kwds)
        results = self.publisher(environ, make_start_response(self.headers))
        return results


    def test_path_info_empty(self):
        """ test PATH_INFO='' GET result and header """
        results = self.run_publisher('')
        expected_header = ('content-type', con_type.html)
        headers = [(h[0].lower(), h[1].lower()) for h in self.headers]
        self.failUnless(expected_header in headers)
        self.assertEqual(results, [('__init__.py', 'get')])
        

    def test_path_info_slash(self):
        """ test PATH_INFO='/' GET result and header """
        results = self.run_publisher('/')
        expected = ('content-type', con_type.html)
        headers = [(h[0].lower(), h[1].lower()) for h in self.headers]
        self.failUnless(expected in headers)
        self.assertEqual(results, [('__init__.py', 'get')])


    def test_path_info_slash_post_empty(self):
        """ test PATH_INFO='/' POST raises TypeError without parameters """
        self.assertRaises(TypeError, self.run_publisher, '/', REQUEST_METHOD='POST')


    def test_path_info_slash_post(self):
        """ test PATH_INFO='/' POST """
        results = self.run_publisher('/', 'a=1&b=2', REQUEST_METHOD='POST')
        expected = [('1', '2')]
        self.assertEqual(results, expected)


    def test_path_info_slash_head(self):
        """ test PATH_INFO='/' HEAD """
        results = self.run_publisher('/', REQUEST_METHOD='HEAD')
        expected = ['head test']
        self.assertEqual(results, expected)


    def test_path_info_slash_delete(self):
        """ test PATH_INFO='/' DELETE """
        results = self.run_publisher('', REQUEST_METHOD='DELETE')
        expected = ['delete test']
        self.assertEqual(results, expected)        


    def test_path_other(self):
        """ test PATH_INFO='/other' GET result and header """
        results = self.run_publisher('/other')
        expected = ('content-type', con_type.plain)
        headers = [(h[0].lower(), h[1].lower()) for h in self.headers]
        self.failUnless(expected in headers)

    def test_path_class_callable_simple(self):
        """ test PATH_INFO='/other/AudioFile' result """
        expected = ['filename=heyjude; length=420']
        results = self.run_publisher('/other/AudioFile/heyjude/420')
        self.assertEqual(results, expected)
        results = self.run_publisher('/other/AudioFile', 'length=420&filename=heyjude')
        self.assertEqual(results, expected)        

    def test_path_class_callable_empty_init(self):
        """ test PATH_INFO='/other/AudioDisc' result """
        expected = ['id=3; name=white_album']
        results = self.run_publisher('/other/AudioDisc/white_album')
        self.assertEqual(results, expected)
        results = self.run_publisher('/other/AudioDisc', 'name=white_album')
        self.assertEqual(results, expected)


    def test_path_class_callable_mixed_init_call(self):
        """ test PATH_INFO='/other/AudioRack' result """
        expected = ['id=12; status=active']
        ## mixed __init__ and __call__ signatures must use query parameters, not path!
        results = self.run_publisher('/other/AudioRack', 'id=12&status=active')
        self.assertEqual(results, expected)


    def test_path_class_callable_empty_call(self):
        """ test PATH_INFO='/other/AudioTrack' result """
        expected = ['id=3; name=drums']
        results = self.run_publisher('/other/AudioTrack', 'id=3&name=drums')
        self.assertEqual(repr(results[0]), expected[0])
        results = self.run_publisher('/other/AudioTrack/3/drums')
        self.assertEqual(repr(results[0]), expected[0])        


    def test_path_class_callable_context_param(self):
        """ test PATH_INFO='/other/AudioClip' result """
        expected = [wsgi_env()['wsgi.version']]
        results = self.run_publisher('/other/AudioClip',)
        self.assertEqual(results, expected)


    def test_path_class_callable_context_app_mixed(self):
        """ test PATH_INFO='/other/AudioDevice' result """
        expected = [(wsgi_env()['wsgi.version'], self.publisher)]
        results = self.run_publisher('/other/AudioDevice')
        self.assertEqual(results, expected)


    def test_module_no_package(self):
        """ test PATH_INFO='/nopackage' result """
        results = self.run_publisher('/nopackage')
        self.failUnless('callables within modules' in results[0])


    def test_module_no_package_sub_again(self):
        """ test PATH_INFO='/sub/again' result """
        expected = [('1', '2')]
        results = self.run_publisher('/sub/again/1/2')
        self.assertEqual(results, expected)
        results = self.run_publisher('/sub/again/1', 'y=2')
        self.assertEqual(results, expected)
        results = self.run_publisher('/sub/again', 'x=1&y=2')
        self.assertEqual(results, expected)        



    def test_module_with_package(self):
        """ test PATH_INFO='/pack' result """
        expected = [('1', '2', 0), ]
        results = self.run_publisher('/pack/1/2')
        self.assertEqual(results, expected)

        results = self.run_publisher('/pack/1', 'y=2')
        self.assertEqual(results, expected)

        results = self.run_publisher('/pack', 'y=2&x=1')
        self.assertEqual(results, expected)


    def test_module_with_package_submodule_get(self):
        """ test PATH_INFO='/pack/again' result """
        expected = [('2', '4', 6), ]
        results = self.run_publisher('/pack/again/2/4')
        self.assertEqual(results, expected)

        results = self.run_publisher('/pack/again/2', 'y=4')
        self.assertEqual(results, expected)

        results = self.run_publisher('/pack/again', 'y=4&x=2')
        self.assertEqual(results, expected)

        
    def test_module_with_package_submodule_named_call(self):
        """ test PATH_INFO='/pack/again/bar' result """
        expected = [('1', '2', []), ]
        results = self.run_publisher('/pack/again/bar/1/2')
        self.assertEqual(results, expected)

        results = self.run_publisher('/pack/again/bar/1', 'y=2')
        self.assertEqual(results, expected)

        results = self.run_publisher('/pack/again/bar', 'y=2&x=1')
        self.assertEqual(results, expected)
    

    def __test__1__index(self):
        results = self.run_publisher('')
        keys = ['default D', 'default C', 'index B', 'index A']
        pos = [results.index(key) for key in keys]
        self.assertEqual(sorted(pos), pos,
                        'index')


    def __test__2__alternate_index(self):
        results = self.run_publisher('/altindex')
        keys = ['default D', 'default C', 'default B', 'alternate A']
        pos = [results.index(key) for key in keys]
        self.assertEqual(sorted(pos), pos,
                        'alt index')

        
    def __test__3__subdirectory_index(self):
        results = self.run_publisher('/sub')
        keys = ['default D', 'default C', 'subdir B', 'subdir A']
        pos = [results.index(key) for key in keys]
        self.assertEqual(sorted(pos), pos,
                        'subdir index')


    def __test__4__subdirectory_empty(self):
        results = self.run_publisher('/sub/empty')
        keys = ['default D', 'default C', 'default B', 'default A']
        pos = [results.index(key) for key in keys]
        self.assertEqual(sorted(pos), pos,
                        'subdir empty template')


    def __test__5__named_template_whole_file(self):
        results = self.run_publisher('/funcs')
        keys = ['default D', 'default C', 'default B', 'ntf A']
        pos = [results.index(key) for key in keys]
        self.assertEqual(sorted(pos), pos,
                        'template with ' + ntf)


    def __test__6__ntf_no_args(self):
        results = self.run_publisher('/funcs/E')
        self.assertEqual(results, '<div>ntf E</div>',
                        'no-arg ' + ntf)


    def __test__7__ntf_args_query_posargs(self):
        results = self.run_publisher('/funcs/F', 'a=1&b=2')
        self.assertEqual(results, '<div>ntf F 1 2</div>',
                        'query posarg ' + ntf)

    def __test__8__ntf_query_keyargs(self):
        results = self.run_publisher('/funcs/G', 'a=1&b=2')
        self.assertEqual(results, '<div>ntf G 1 2</div>',
                        'query+keyarg named template function ')


    def __test__9__ntf_args_query_posargs_keyargs(self):
        results = self.run_publisher('/funcs/H', 'a=1&b=2')
        self.assertEqual(results, '<div>ntf H 1 2</div>',
                        'query+posarg+defaults ' + ntf)


    def __test__10__ntf_path_only(self):
        results = self.run_publisher('/funcs/I/2/3')
        self.assertEqual(results, '<div>ntf I 2 3</div>',
                        'path ' + ntf)


    def __test__11__ntf_path_query_mix(self):
        results = self.run_publisher('/funcs/J/0', 'b=1')
        self.assertEqual(results, '<div>ntf J 0 1</div>',
                        'path+query ' + ntf)

    def __test__12__ntf_path_query_mix(self):
        results = self.run_publisher('/funcs/K/0', 'b=1')
        self.assertEqual(results, '<div>ntf K 0 1</div>',
                         'path+query+defaults ' + ntf)


    def __test__13__ntf_keyargs(self):
        results = self.run_publisher('/funcs/L', 'a=slug')
        for key in ['slug', 'cookies', 'environ', 'context', 'form']:
            self.failUnless(key in results,
                            'kwarg ' + ntf)


    def __test__14__ntf_posargs_keyargs_query(self):
        results = self.run_publisher('/funcs/M', 'a=slug')
        self.failUnless('slug' in results,
                        'query+posarg+kwarg ' + ntf)
        for key in ['cookies', 'environ', 'context', 'form']:
            self.failUnless(key in results,
                            'query+posarg+kwarg ' + ntf)


    def __test__15__ntf_posargs_keyargs_defaults_query(self):
        results = [
            self.run_publisher('/funcs/N/snail/slug'),
            self.run_publisher('/funcs/N/slug', 'b=snail'),
            self.run_publisher('/funcs/N/snail', 'b=slug'),
            self.run_publisher('/funcs/N', 'a=snail&b=slug'),
        ]

        keys = [
            'juice', 'snail', 'slug', 'cookies', 'environ',
            'context', 'form'
        ]
        
        for key in keys:
            for result in results:
                self.failUnless(key in result,
                                'query+posarg+kwarg ' + ntf)


    def __test__16__nmf_noargs(self):
        results = self.run_publisher('/funcs/P')
        self.assertEqual(results, 'P',
                         'no arg ' + nmf)

    def __test__17__nmf_posarg(self):
        results = [
            self.run_publisher('/funcs/Q', 'a=1'),
            self.run_publisher('/funcs/Q/1'),
            ]
        for result in results:
            self.assertEqual(result, 'Q 1',
                             ' pos arg ' + nmf)        
        

    def __test__18__nmf_posargs(self):
        results = [
            self.run_publisher('/funcs/R', 'a=1&b=2'),
            self.run_publisher('/funcs/R/1', 'b=2'),            
            self.run_publisher('/funcs/R/1/2'),
            ]
        for result in results:
            self.assertEqual(result, 'R 1 2',
                             ' pos args ' + nmf)        

    def __test__19__nmf_defaults(self):
        results = [
            self.run_publisher('/funcs/S/1'),
            self.run_publisher('/funcs/S', 'a=1'),
            ]
        for result in results:
            self.assertEqual(result, 'S 1 0',
                             ' default args ' + nmf)
        
        results = [
            self.run_publisher('/funcs/S', 'a=1&b=2'),
            self.run_publisher('/funcs/S/1', 'b=2'),            
            self.run_publisher('/funcs/S/1/2'),
            ]
        for result in results:
            self.assertEqual(result, 'S 1 2',
                             ' default args ' + nmf)


    def __test__20__nmf_kwargs(self):
        results = [
            self.run_publisher('/funcs/T', 'a=slug&b=snail'),
            self.run_publisher('/funcs/T/slug', 'b=snail'),
            self.run_publisher('/funcs/T/snail', 'b=slug'),
            ]
        for result in results:
            self.failUnless('slug' in result,
                             ' kw args ' + nmf)
            self.failUnless('snail' in result,
                             ' kw args ' + nmf)


    def __test__21__nmf_extraposargs(self):
        results = [
            self.run_publisher('/funcs/U', 'b=slug&b=snail'),
            ]
        for result in results:
            self.failUnless('slug' in result,
                             ' extra pos args ' + nmf)
            self.failUnless('snail' in result,
                             ' extra pos args ' + nmf)


    def __test__z__22__nmf_posargs_extraposargs(self):
        results = [
            self.run_publisher('/funcs/V/1', 'b=slug&b=snail'),
            ]

        for result in results:
            self.failUnless('slug' in result,
                             ' pos args + extra pos args ' + nmf)
            self.failUnless('snail' in result,
                             ' pos args + extra pos args ' + nmf)


    ## still need more tests for funcs/V and funcs/W


if __name__ == '__main__':
    unittest.main()

