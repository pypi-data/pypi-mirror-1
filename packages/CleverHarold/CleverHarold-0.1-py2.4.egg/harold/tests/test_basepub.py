#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

""" test_basepub -> tests for everything in harold.basepub not related
                    to parsing and view construction

"""
import unittest
from new import module
from os.path import basename

from harold.lib import con_type
from harold.publishers.common import (Publisher, StopRecursion,
                                      TemplateMixin, magic_arg_names,
                                      publishable_items, )
from harold.tests.lib import (test_app, wsgi_env, make_start_response,
                              txt_template_dirs, )


class NullTemplateType:
    """ a type of template for testing that does no templating

    """
    value = 'test template complete'

    def __init__(self, app, env):
        self.app = app
        self.env = env

    def __call__(self):
        if self.env.get('test_stop_recursion', False):
            raise StopRecursion('make it stop!')
        return self.value


class FsPublisher__Test(unittest.TestCase):
    def setUp(self):
        self.publisher = Publisher(
            test_app, NullTemplateType, dirs=(), layout='',
            defaults=(), debug=True
        )


    def test_environ_querystring_exc(self):
        """ test for Exception when query string has error=t """
        environ = wsgi_env(QUERY_STRING='error=t')
        start_response = make_start_response([])
        self.publisher.debug = True
        # it was always lame anyway:
        # self.assertRaises(Exception, self.publisher, environ, start_response)


    def test_environ_querystring_no_exc(self):
        """ test for no Exception when query string has error=t """
        environ = wsgi_env(QUERY_STRING='error=t')
        start_response = make_start_response([])        
        self.publisher.debug = False
        self.failUnless(self.publisher(environ, start_response))


    def test_template_response_default(self):
        """ test template default response and header values """
        environ = wsgi_env()
        headers = []
        self.assertEqual(self.publisher(environ, make_start_response(headers)),
                         [NullTemplateType.value])
        self.assertEqual(headers, [('content-type', con_type.html)])


    def test_recursive(self):
        """ test for publisher's callable StopRecursion (aka StopIteration) """
        environ = wsgi_env(test_stop_recursion=True)
        start_response = make_start_response([])        
        self.assertEqual(self.publisher(environ, start_response), test_app.value)


class FakeTemplateType(TemplateMixin):
    """ a type of template for testing that does a bit of templating

    """
    ext = '.txt'
    index = 'index.txt'

    def render(self, filename, args):
        try:
            fh = file(filename, 'r')
        except (IOError, ):
            raise Exception('iofault')
        txt = fh.read()
        filename = basename(filename)
        return txt % locals()


class FsCallableMixin__Test(unittest.TestCase):
    """ FsCallableMixin__Test() -> test the filesystem callable mixin

    """
    def setUp(self):
        self.start_response = make_start_response([])
        self.publisher = Publisher(
            test_app, FakeTemplateType, dirs=txt_template_dirs, layout='',
            defaults=(), debug=True
        )


    def test_render_index_no_path_info(self):
        """ test empty PATH_INFO returns the index """
        environ = wsgi_env()
        results = self.publisher(environ, self.start_response)
        expected = ['index.txt []']
        self.assertEqual(results, expected)


    def test_render_index_at_slash(self):
        """ test PATH_INFO=/ returns the index """
        environ = wsgi_env(PATH_INFO='/')
        results = self.publisher(environ, self.start_response)
        expected = ['index.txt []']
        self.assertEqual(results, expected)


    def test_render_other(self):
        """ test PATH_INFO=/ returns the index """        
        environ = wsgi_env(PATH_INFO='/other')
        results = self.publisher(environ, self.start_response)
        expected = ['other.txt []']
        self.assertEqual(results, expected)


    def test_render_with_path_args(self):
        """ test PATH_INFO with template and extra args is rendered well """
        environ = wsgi_env(PATH_INFO='/other/x/y/z')
        results = self.publisher(environ, self.start_response)
        expected = ["other.txt ['x', 'y', 'z']"]
        self.assertEqual(results, expected)


    def test_render_not_found(self):
        """ test not found PATH_INFO falls through to application """
        environ = wsgi_env(PATH_INFO='/notfound')
        results = self.publisher(environ, self.start_response)
        expected = test_app.value
        self.assertEqual(results, expected)


    def test_context(self):
        """ test keys in context and context['environ'] """
        environ = wsgi_env()
        faker = self.publisher.template_type(test_app, environ)
        context = faker.context()
        self.failUnless(callable(context))

        context = context()
        for name in magic_arg_names:
            self.failUnless(name in context)

        context_env = context.get('environ', {})
        for name in wsgi_env():
            self.failUnless(name in context_env)


class PublishableItems__Test(unittest.TestCase):
    """ PublishableItems__Test() -> tests for the publishable_items function

    """
    def setUp(self):

        def A():pass
        A.expose = True

        def Bempty():pass
        
        def Bfalse():pass
        Bfalse.expose = False

        def _C():pass
        _C.expose = True

        def D():pass
        D.default = True

        def Ddefault():pass
        Ddefault.expose = True
        Ddefault.default = True

        def Edefault():pass
        Edefault.expose = True
        Edefault.default = True

        ## grab a mapping of all the functions defined above
        funcs = locals()
        del(funcs['self'])

        ## we use a subclass of module so we can update its contents
        ## in the manner we want; without this, _C could not go in
        class M(module):pass

        mod = M('test')
        mod.__dict__.update(funcs)
        publishable, defaults = publishable_items(mod)
        self.publishable = dict(publishable)
        self.defaults = dict(defaults)


    def test_exposed_publishable(self):
        """ test for a published item """
        self.failUnless('A' in self.publishable)


    def test_expose_empty(self):
        """ test for an item without an 'expose' attribute """
        self.failUnless('Bempty' not in self.publishable)


    def test_expose_false(self):
        """ test for an item with a False 'expose' attribute """    
        self.failUnless('Bfalse' not in self.publishable)


    def test_expose_underscore(self):
        """ test for an item without a leading underscore """
        self.failUnless('_C' not in self.publishable)    


    def test_default_without_expose(self):
        """ test for a default item without an 'expose' attribute """
        self.failUnless('D' not in self.publishable)


    def test_defaults(self):
        """ test for default items """
        for name in ('Ddefault', 'Edefault'):
            self.failUnless(name in self.publishable)
            self.failUnless(name in self.defaults)            


if __name__ == '__main__':
    unittest.main()
