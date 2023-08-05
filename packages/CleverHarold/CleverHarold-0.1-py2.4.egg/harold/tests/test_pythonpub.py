#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>


##
#
# This is the newer test case for the python module publisher.  The
# other case, test_codepub, focuses on function calls and has only
# minimal tests for objects.  This module focuses on
# tests for publishing class instances.
#
##

import unittest
from harold.publishers import code_publisher
from harold.tests.lib import (wsgi_env, test_app, make_start_response,
                              mod_template_dirs, )


class ClassObjPub__Test(unittest.TestCase):
    def setUp(self):
        self.headers = []
        self.publisher = code_publisher(
            app = test_app,
            dirs=mod_template_dirs,
            debug=True)

    def run_publisher(self, path, query='', **kwds):
        environ = wsgi_env(PATH_INFO=path, QUERY_STRING=query)
        environ.update(kwds)
        results = self.publisher(environ, make_start_response(self.headers))
        return results


    def test_a_a(self):
        """ __init__ sig. a, method sig. a """
        results = self.run_publisher('/pypub/a_a', '')
        self.failUnless(results)

        results = self.run_publisher('/pypub/a_a/meth', '')
        self.assertEqual(results, [None])
        

    def test_a_b(self):
        """ __init__ sig. a, method sig. b """        
        results = self.run_publisher('/pypub/a_b', '')
        self.failUnless(results)

        results = self.run_publisher('/pypub/a_b/meth', '')
        self.assertEqual(results, [1]) # int default, int out

        results = self.run_publisher('/pypub/a_b/meth/2', '')
        self.assertEqual(results, ['2'])

        results = self.run_publisher('/pypub/a_b/meth', 'x=3')
        self.assertEqual(results, ['3'])


    def test_a_c(self):
        """ __init__ sig. a, method sig. c """
        results = self.run_publisher('/pypub/a_c', '')
        self.failUnless(results)

        results = self.run_publisher('/pypub/a_c/meth', '')
        self.assertEqual(results, [()])

        results = self.run_publisher('/pypub/a_c/meth/2', '')
        self.assertEqual(results, [('2', )])

        results = self.run_publisher('/pypub/a_c/meth/2/3', '')
        self.assertEqual(results, [('2', '3', )])

        results = self.run_publisher('/pypub/a_c/meth', 'v=3')
        self.assertEqual(results, [('3', )])

        results = self.run_publisher('/pypub/a_c/meth', 'v=3&v=4')
        self.assertEqual(results, [('3', '4')])


    def test_a_d(self):
        """ __init__ sig. a, method sig. d """        
        results = self.run_publisher('/pypub/a_d', '')
        self.failUnless(results)

        results = self.run_publisher('/pypub/a_d/meth', '')
        self.assertEqual(results, [(1, ())])

        results = self.run_publisher('/pypub/a_d/meth/2', '')
        self.assertEqual(results, [('2', ())])

        results = self.run_publisher('/pypub/a_d/meth/2/3', '')
        self.assertEqual(results, [('2', ('3',))])

        results = self.run_publisher('/pypub/a_d/meth', 'v=3')
        self.assertEqual(results, [(1, ('3', ))])

        results = self.run_publisher('/pypub/a_d/meth', 'v=3&v=4')
        self.assertEqual(results, [(1, ('3', '4'))])
        
        results = self.run_publisher('/pypub/a_d/meth/2', 'v=3&v=4')
        self.assertEqual(results, [('2', ('3', '4'))])

        results = self.run_publisher('/pypub/a_d/meth/2/2', 'v=3&v=4')
        self.assertEqual(results, [('2', ('2', '3', '4'))])


    def test_a_e(self):
        """ __init__ sig. a, method sig. e """
        results = self.run_publisher('/pypub/a_e', '')
        self.failUnless(results)

        self.assertRaises(TypeError, self.run_publisher, '/pypub/a_e/meth')

        self.assertRaises(TypeError, self.run_publisher, '/pypub/a_e/meth/1')

        results = self.run_publisher('/pypub/a_e/meth/2/3', '')
        self.assertEqual(results, [('2', '3')])

        results = self.run_publisher('/pypub/a_e/meth', 'x=2&y=3')
        self.assertEqual(results, [('2', '3')])

        results = self.run_publisher('/pypub/a_e/meth/2', 'y=3')
        self.assertEqual(results, [('2', '3')])


    def test_a_f(self):
        """ __init__ sig. a, method sig. f """
        results = self.run_publisher('/pypub/a_f', '')
        self.failUnless(results)

        self.assertRaises(TypeError, self.run_publisher, '/pypub/a_f/meth')

        results = self.run_publisher('/pypub/a_f/meth/1', '')
        self.assertEqual(results, [('1', 0)])

        results = self.run_publisher('/pypub/a_f/meth', 'x=1')
        self.assertEqual(results, [('1', 0)])

        results = self.run_publisher('/pypub/a_f/meth/2/3', '')
        self.assertEqual(results, [('2', '3')])

        results = self.run_publisher('/pypub/a_f/meth', 'x=2&y=3')
        self.assertEqual(results, [('2', '3')])

        results = self.run_publisher('/pypub/a_f/meth/2', 'y=3')
        self.assertEqual(results, [('2', '3')])


    def test_a_g(self):
        """ __init__ sig. a, method sig. g """
        results = self.run_publisher('/pypub/a_g', '')
        self.failUnless(results)

        self.assertRaises(TypeError, self.run_publisher, '/pypub/a_g/meth')

        results = self.run_publisher('/pypub/a_g/meth/2', '')
        self.assertEqual(results, [('2', ())])

        results = self.run_publisher('/pypub/a_g/meth/2/3', '')
        self.assertEqual(results, [('2', ('3',))])

        self.assertRaises(TypeError, self.run_publisher, '/pypub/a_g/meth', 'v=3')
        self.assertRaises(TypeError, self.run_publisher, '/pypub/a_g/meth', 'v=3&v=4')
        
        results = self.run_publisher('/pypub/a_g/meth/2', 'v=3&v=4')
        self.assertEqual(results, [('2', ('3', '4'))])

        results = self.run_publisher('/pypub/a_g/meth/2/2', 'v=3&v=4')
        self.assertEqual(results, [('2', ('2', '3', '4'))])


    def test_a_h(self):
        """ __init__ sig. a, method sig. h """
        results = self.run_publisher('/pypub/a_h', '')
        self.failUnless(results)

        self.assertRaises(TypeError, self.run_publisher, '/pypub/a_h/meth')

        results = self.run_publisher('/pypub/a_h/meth/1', '')
        self.assertEqual(results, [('1', 0, ())])

        results = self.run_publisher('/pypub/a_h/meth', 'x=1')
        self.assertEqual(results, [('1', 0, ())])

        results = self.run_publisher('/pypub/a_h/meth/2/3', '')
        self.assertEqual(results, [('2', '3', ())])

        results = self.run_publisher('/pypub/a_h/meth', 'x=2&y=3')
        self.assertEqual(results, [('2', '3', ())])

        results = self.run_publisher('/pypub/a_h/meth/2', 'y=3')
        self.assertEqual(results, [('2', '3', ())])

        results = self.run_publisher('/pypub/a_h/meth/1/2/3', '')
        self.assertEqual(results, [('1', '2', ('3', ))])
        
        results = self.run_publisher('/pypub/a_h/meth/1/2/3', 'v=4')
        self.assertEqual(results, [('1', '2', ('3', '4'))])



    def test_b_a(self):
        """ __init__ sig. b, method sig. a """
        self.assertRaises(TypeError, self.run_publisher, '/pypub/b_a')
        
        results = self.run_publisher('/pypub/b_a/1')
        self.failUnless(results)

        results = self.run_publisher('/pypub/b_a/1/meth')
        self.assertEqual(results, ['1'])

        results = self.run_publisher('/pypub/b_a/3/meth')
        self.assertEqual(results, ['3'])

    def test_b_b(self):
        """ __init__ sig. b, method sig. b """
        results = self.run_publisher('/pypub/b_b/1/meth')
        self.assertEqual(results, [('1', 0)])

        results = self.run_publisher('/pypub/b_b/1/meth/2')
        self.assertEqual(results, [('1', '2')])

    def test_b_c(self):
        """ __init__ sig. b, method sig. c """
        results = self.run_publisher('/pypub/b_c/1/meth')
        self.assertEqual(results, [('1', ())])

        results = self.run_publisher('/pypub/b_c/1/meth/2')
        self.assertEqual(results, [('1', ('2', ))])
        

        
if __name__ == '__main__':
    unittest.main()

