#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import unittest
from harold.publishers.common import request_args, magic_arg_names

"""
This is a reference copied from basepub.RequestParameterParser.  Our
test function base names are given in the first column:

A : (True, True, True) : pos_args_extra_args_keyword_args
B : (True, True, False) : pos_args_extra_args

C : (True, False, True) : pos_args_keyword_args              
D : (True, False, False) : pos_args

E : (False, True, True) : extra_args_keyword_args
F : (False, True, False) : extra_args

G : (False, False, True) : keyword_args
H : (False, False, False) : no_args


The names are encoded starting with the above letter prefix, plus any
count qualifier, plus 'd' for defaults, plus 'env' for environ value
from the context.
"""


def A(x, *y, **w):
    return x, y, w

def A2(x, y, *z, **w):
    return x, y, z, w

def A2d(x, y=0, *z, **w):
    return x, y, z, w

def B(x, y, z, *d):
    return x, y, z, d

def Bd(x=1, y=2, z=3, *d):
    return x, y, z, d

def C(x, y, **w):
    return x, y, w

def Cenv(x, y, environ, **w):
    return x, y, environ, w

def Cdenv(x, y, environ={}, **w):
    return x, y, environ, w

def D(x):
    return x

def D2(x, y):
    return x, y

def D2env(x, y, environ):
    return x, y, environ

def D2denv(x, y, environ={}):
    return x, y, environ

def D3(x, y, z):
    return x, y, z

def D3env(x, y, z, environ):
    return x, y, z, environ

def E(*z, **d):
    return z, d

## Ed is really a variant of A, but it fits well here
def Ed(y=0, *z, **d):
    return y, z, d

def F(*z):
    return z

## Fd is really a variant of B, but it fits well here, too
def Fd(y=0, *z):
    return z

def G(**w):
    return w

def Gd(y=0, **w):
    return w


def H():
    return None


empty_args = ([], {})
static_context = dict([(name, name[0].upper()) for name
                       in magic_arg_names])
def MC():
    return static_context.copy()


class RequestParameterParser__Test(unittest.TestCase):
    """ RequestParameterParser__Test() -> just like the name implies

    """
    def test__A__0(self):
        """ test path-only to args and extra args """
        expected = ([1, 2, 3], static_context)
        results = request_args(A, [1, 2, 3], {}, context=MC)
        self.assertEqual(results, expected)

    def test__A__1(self):
        """ test path and query to args and extra args """
        expected = ([1, 2, 3, 4], static_context)
        results = request_args(A, [1, 2, 3], {'y':4}, context=MC)
        self.assertEqual(results, expected)        

    def test__A__2(self):
        """ test path and query sequence value to args and extra args """
        expected = ([1, 2, 3, 4, 5], static_context)
        results = request_args(A, [1, 2, 3], {'y':[4, 5]}, context=MC)
        self.assertEqual(results, expected)        

    def test__A__3(self):
        """ test path and query string value to args and extra args """
        expected = ([1, 2, 3, 'slug'], static_context)
        results = request_args(A, [1, 2, 3], {'y':'slug'}, context=MC)
        self.assertEqual(results, expected)

    def test__A__4(self):
        """ test path and mixed query value to args and extra args

        (same as test__A__2)
        """
        expected = ([1, 2, 3, 'slug', 4], static_context)
        results = request_args(A, [1, 2, 3], {'y':('slug', 4)}, context=MC)
        self.assertEqual(results, expected)

    def test__A__5(self):
        """ test path, mixed query and keywords to args, extra args, and kwds """
        d = MC()
        d.update(e=4, f=5, g='snail')
        expected = ([1, 2, 3, 'slug', 4], d)
        results = request_args(A, [1, 2, 3], {'y':('slug', 4), 'e':4, 'f':5, 'g':'snail'}, context=MC)
        self.assertEqual(results, expected)        


    def test__A2__0(self):
        """ test path-only to args and extra args """
        expected = ([1, 2, 3], static_context)
        results = request_args(A2, [1, 2, 3], {}, context=MC)
        self.assertEqual(results, expected)

    def test__A2__1(self):
        """ test path and query value to args and extra args """
        expected = ([1, 2, 3, 4], static_context)
        results = request_args(A2, [1, 2, 3], {'z':4}, context=MC)
        self.assertEqual(results, expected)        

    def test__A2__2(self):
        """ test path and query sequence to args and extra args """
        expected = ([1, 2, 3, 4, 5], static_context)
        results = request_args(A2, [1, 2, 3], {'z':[4, 5]}, context=MC)
        self.assertEqual(results, expected)        

    def test__A2__3(self):
        """ test path and query string value to args and extra args """
        expected = ([1, 2, 3, 'slug'], static_context)
        results = request_args(A2, [1, 2, 3], {'z':'slug'}, context=MC)
        self.assertEqual(results, expected)

    def test__A2__4(self):
        """ test path and mixed query value to args and extra args

        (same as test__A2__2)
        """
        expected = ([1, 2, 3, 'slug', 4], static_context)
        results = request_args(A2, [1, 2, 3], {'z':('slug', 4)}, context=MC)
        self.assertEqual(results, expected)

    def test__A2__5(self):
        """ test path, mixed query and keywords to args, extra args, and kwds

        """
        d = MC()
        d.update(e=4, f=5, g='snail')
        expected = ([1, 2, 3, 'slug', 4], d)
        query = {'z':('slug', 4), 'e':4, 'f':5, 'g':'snail'}
        results = request_args(A2, [1, 2, 3], query, context=MC)
        self.assertEqual(results, expected)        


    def test__A2d__0(self):
        """ test path and query value to args with defaults and keywords """
        expected = ([1, 0, 3], static_context)
        results = request_args(A2d, [1, ], {'z':3}, context=MC)
        self.assertEqual(results, expected)

    def test__A2d__1(self):
        """ test path and query sequence to args with defaults and keywords """
        expected = ([1, 0, 3, 4, 5], static_context)
        results = request_args(A2d, [1, ], {'z':[3, 4, 5]}, context=MC)
        self.assertEqual(results, expected)

    def test__A2d__2(self):
        """ test path and query string value to args with defaults

        (same as test__A2d__0)
        """
        expected = ([1, 0, 'slug'], static_context)
        results = request_args(A2d, [1, ], {'z':'slug'}, context=MC)
        self.assertEqual(results, expected)
        self.assertEqual(results, expected)        


    def test__B__0(self):
        """ test path to args and extra args """
        expected = ([1, 2, 3], {})
        results = request_args(B, [1, 2, 3], {}, context=MC)
        self.assertEqual(results, expected)

    def test__B__1(self):
        """ test path and query value to args and extra args """
        expected = ([1, 2, 3, 4], {})
        results = request_args(B, [1, 2, 3], {'d':4}, context=MC)
        self.assertEqual(results, expected)        

    def test__B__2(self):
        """ test path and query sequence to args and extra args """
        expected = ([1, 2, 3, 4, 5], {})
        results = request_args(B, [1, 2, 3], {'d':[4, 5]}, context=MC)
        self.assertEqual(results, expected)        

    def test__B__3(self):
        """ test path and query value string to args and extra args """
        expected = ([1, 2, 3, 'slug'], {})
        results = request_args(B, [1, 2, 3], {'d':'slug'}, context=MC)
        self.assertEqual(results, expected)

    def test__B__4(self):
        """ test path and mixed query value to args and extra args

        (same as test__B__2)
        """
        expected = ([1, 2, 3, 'slug', 4], {})
        results = request_args(B, [1, 2, 3], {'d':('slug', 4)}, context=MC)
        self.assertEqual(results, expected)

    def test__B__5(self):
        """ test for TypeError on extra query values """
        query = {'d':('slug', 4), 'e':4}
        self.assertRaises(TypeError, request_args,
                          B, [1, 2, 3], query)

    def test__B__6(self):
        """ test for no exception when set to ignore additional args """
        query = {'d':('slug', 4), 'e':4}        
        expected = ([1, 2, 3, 'slug', 4], {})
        self.assertEqual(request_args(B, [1, 2, 3], query,
                                      ignore_additional_args=True),
                         expected)

    def test__B__7(self):
        """ test for long path to args and extra args """
        self.assertEqual(request_args(B, [1, 2, 3, 4, 5], {}),
                          ([1, 2, 3, 4, 5], {}))

    def test__B__8(self):
        """ test for path and long query sequence to args and extra args """
        self.assertEqual(request_args(B, [1, 2, 3], {'d':[4, 5, 6]}),
                         ([1, 2, 3, 4, 5, 6], {}))


    def test__Bd__0(self):
        """ test for empty path and query to default values and no extra args """
        expected = ([1, 2, 3], {})
        results = request_args(Bd, [], {})
        self.assertEqual(results, expected)

    def test__Bd__1(self):
        """ test for first path value to first arg with remaining
            defaults and no extra args
        """
        expected = ([4, 2, 3], {})
        results = request_args(Bd, [4], {})
        self.assertEqual(results, expected)

    def test__Bd__2(self):
        """ test for first two path values to first two args with remaining
            defaults and no extra args
        """
        expected = ([4, 5, 3], {})
        results = request_args(Bd, [4, 5], {})
        self.assertEqual(results, expected)

    def test__Bd__3(self):
        """ test for three path values to three args with no defaults
            and no extras
        """
        expected = ([4, 5, 6], {})
        results = request_args(Bd, [4, 5, 6], {})
        self.assertEqual(results, expected)        


    def test__C__0(self):
        """ test for path arg with query arg of same name raises TypeError """
        self.assertRaises(TypeError, request_args, C, [1], {'x':3, 'y':2})

    def test__C__1(self):
        """ test for path arg with query arg of same name does not
            raise TypeError when set to ignore additional args
        """
        expected = ([1, 4], {})
        self.assertEqual(request_args(C, [1], {'x':3, 'y':4},
                                      ignore_additional_args=True),
                         expected)


    def test__C__2(self):
        """ test for path arguments and empty keywords """
        self.assertEqual(request_args(C, [1, 2], {}), ([1, 2], {}))

    def test__C__3(self):
        """ test for path and query values and query keywords """
        self.assertEqual(request_args(C, [1, ], {'y':2, 'z':3}),
                         ([1, 2], {'z':3}))
    def test__C__4(self):
        """ test for empty path and query values and query values """
        self.assertEqual(request_args(C, [], {'x':1, 'y':2, 'z':3}),
                         ([1, 2], {'z':3}))


    def test__Cenv__0(self):
        """ test for context value as argument and remaining context
            as keyword args
        """
        results = request_args(Cenv, [1, 2], {}, context=MC)
        expected = ([1, 2, 'E'], {'publisher':'P', 'application':'A', 'request':'R'})
        self.assertEqual(results, expected)


    def test__Cdenv__0(self):
        """ test for context value as argument instead of default and
            remaining context values as keyword args
        """
        results = request_args(Cdenv, [1, 2], {}, context=MC)
        expected = ([1, 2, 'E'],
                    {'publisher':'P', 'application':'A', 'request':'R'})
        self.assertEqual(results, expected)


    def test__D__0(self):
        """ test single positional value from path """
        self.assertEqual(request_args(D, [1, ], {}), ([1], {}))

    def test__D__1(self):
        """ test single positional value from query """
        self.assertEqual(request_args(D, [], {'x':1}), ([1], {}))

    def test__D__2(self):
        """ test single positional value from path ignoring extra
            path values """
        self.assertEqual(request_args(D, [1, 2, 3], {}, ignore_additional_args=True),
                         ([1], {}))

    def test__D__3(self):
        """ test single positional value from query """
        self.assertEqual(request_args(D, [1], {'x':2}, ignore_additional_args=True),
                         ([1], {}))


    def test__D2__0(self):
        """ test two positional values from path """
        self.assertEqual(request_args(D2, [1, 2], {}),
                         ([1, 2], {}))

    def test__D2__1(self):
        """ test two positional values from query """
        self.assertEqual(request_args(D2, [], {'x':1, 'y':2}),
                         ([1, 2], {}))

    def test__D2__2(self):
        """ test one positional value from path and one from query """
        self.assertEqual(request_args(D2, [1, ], {'y':2}),
                         ([1, 2], {}))

    def test__D2__3(self):
        """ test two positional values and ignored context """
        self.assertEqual(request_args(D2, [], {'x':1, 'y':2}, context=MC),
                         ([1, 2], {}))


    def test__D2denv__0(self):
        """ test two positional values from path and context value
            default override without keywords
        """
        results = request_args(D2denv, [1, 2], {}, context=MC)
        expected = ([1, 2, 'E'], {})
        self.assertEqual(results, expected) 

    def test__D2env__2(self):
        """ test two positional values from path and context value
            without keywords
        """
        results = request_args(D2env, [1, 2], {}, context=MC)
        expected = ([1, 2, 'E'], {})
        self.assertEqual(results, expected)


    def test__D3__0(self):
        """ test three positional values from path """
        self.assertEqual(request_args(D3, [1, 2, 3], {}),
                         ([1, 2, 3], {}))

    def test__D3__1(self):
        """ test three positional values from query """
        self.assertEqual(request_args(D3, [], {'x':1, 'y':2, 'z':3}),
                         ([1, 2, 3], {}))

    def test__D3__2(self):
        """ test one positional value from path and two from query """
        expected = ([1, 2, 3], {})
        self.assertEqual(request_args(D3, [1, ], {'y':2, 'z':3}),
                         expected)

    def test__D3__3(self):
        """ test two positional values from path and one from query """
        expected = ([1, 2, 3], {})
        self.assertEqual(request_args(D3, [1, 2], {'z':3}),
                         expected)


    def test__D3env__0(self):
        """ test three positional values from path with context value """
        expected = ([1, 2, 3, 'E'], {})
        results = request_args(D3env, [1, 2, 3], {}, context=MC)
        self.assertEqual(results, expected)

    def test__D3env__1(self):
        """ test three positional values from query with context value """
        expected = ([1, 2, 3, 'E'], {})
        results = request_args(D3env, [], {'x':1, 'y':2, 'z':3}, context=MC)
        self.assertEqual(results, expected)        

    def test__D3env__2(self):
        """ test two positional values path and one from query with context value """
        expected = ([1, 2, 3, 'E'], {})
        results = request_args(D3env, [1, 2], {'z':3}, context=MC)
        self.assertEqual(results, expected)        


    def test__E__0(self):
        """ test emtpy path and query with extra positional and keyword args """
        expected = empty_args
        results = request_args(E, [], {})
        self.assertEqual(results, expected)

    def test__E__1(self):
        """ test path values and empty query with extra positional and keyword args """
        expected = ([1, 2, 3], {})
        results = request_args(E, [1, 2, 3], {})
        self.assertEqual(results, expected)

    def test__E__2(self):
        """ test path and keyword values with extra positional and keyword args """
        expected = ([1, 2, 3], {'u':3})
        results = request_args(E, [1, 2, 3], {'u':3})
        self.assertEqual(results, expected)

    def test__E__3(self):
        """ test path and query value with extra positional and emtpy keyword args """
        expected = ([1, 2, 3, 4, 5], {})
        results = request_args(E, [1, 2, 3, 4], {'z':5})
        self.assertEqual(results, expected)

    def test__E__4(self):
        """ test path and query values with extra positional and keyword args """
        expected = ([1, 2, 3, 4, 5], {'u':3})
        results = request_args(E, [1, 2, 3, 4], {'z':5, 'u':3})
        self.assertEqual(results, expected)        

    def test__E__5(self):
        """ test path and query sequence with extra positional and empty keyword args """
        expected = ([1, 2, 3, 4, 5, 6], {})
        results = request_args(E, [1, 2, 3, 4], {'z':(5,6)})
        self.assertEqual(results, expected)

    def test__E__6(self):
        """ test path and mixed query with extra positional and keyword args """
        expected = ([1, 2, 3, 4, 5, 6], {'u':3})
        results = request_args(E, [1, 2, 3, 4], {'z':(5,6), 'u':3})
        self.assertEqual(results, expected)

    def test__E__7(self):
        """ test path and query string value with extra positional and keyword args """
        expected = ([1, 2, 3, 4, 'slug'], {'u':3})
        results = request_args(E, [1, 2, 3, 4], {'z':'slug', 'u':3})
        self.assertEqual(results, expected)        


    def test__Ed__0(self):
        """ test empty path with default positional arg and empty extra args """
        expected = ([0], {})
        args, kwds = request_args(Ed, [], {})
        self.assertEqual((args, kwds), expected)
        self.assertEqual(Ed(*args, **kwds), (0, (), {}))

    def test__Ed__1(self):
        """ test path values with default positional arg and extra args """
        expected = ([1, 2, 3], {})
        args, kwds = request_args(Ed, [1, 2, 3], {})
        self.assertEqual((args, kwds), expected)
        self.assertEqual(Ed(*args, **kwds), (1, (2, 3), {}))
                         
    def test__Ed__2(self):
        """ test path values with default positional arg from query """
        expected = (['slug', 1, 2, 3], {})
        args, kwds = request_args(Ed, [1, 2, 3], {'y':'slug'})
        self.assertEqual((args, kwds), expected)
        self.assertEqual(Ed(*args, **kwds), ('slug', (1, 2, 3), {}))
        
    def test__Ed__3(self):
        """ test path values with default positional arg from query and extra args """
        expected = (['slug', 1, 2, 3, 4, 5], {})
        args, kwds = request_args(Ed, [1, 2, 3, 4], {'z':5, 'y':'slug'})
        self.assertEqual((args, kwds), expected)
        self.assertEqual(Ed(*args, **kwds), ('slug', (1, 2, 3, 4, 5), {}))
        
    def test__Ed__4(self):
        """ test path values with default positional arg from query
            and extra args and keywords
        """
        expected = (['slug', 1, 2, 3, 4, 5], {'u':3})
        args, kwds = request_args(Ed, [1, 2, 3, 4], {'z':5, 'u':3, 'y':'slug'})
        self.assertEqual((args, kwds), expected)        
        self.assertEqual(Ed(*args, **kwds), ('slug', (1, 2, 3, 4, 5), {'u':3}))
        
    def test__Ed__5(self):
        """ test path values with default positional arg from query
            and extra args from query sequence and empty keywords
        """
        expected = (['slug', 1, 2, 3, 4, 5, 6], {})
        args, kwds = request_args(Ed, [1, 2, 3, 4], {'z':(5,6), 'y':'slug'})
        self.assertEqual((args, kwds), expected)
        self.assertEqual(Ed(*args, **kwds), ('slug', (1, 2, 3, 4, 5, 6), {}))

    def test__Ed__6(self):
        """ test path values with default positional arg from query
            and extra args from query sequence and keywords from query
        """        
        expected = (['slug', 1, 2, 3, 4, 5, 6], {'u':3})
        args, kwds = request_args(Ed, [1, 2, 3, 4], {'z':(5,6), 'u':3, 'y':'slug'})
        self.assertEqual((args, kwds), expected)
        self.assertEqual(Ed(*args, **kwds), ('slug', (1, 2, 3, 4, 5, 6), {'u':3}))
        
    def test__Ed__7(self):
        """ test path values with default positional arg from query
            and extra args from query string value and keywords from
            query values
        """        
        expected = (['slug', 1, 2, 3, 4, 'slug'], {'u':3})
        args, kwds = request_args(Ed, [1, 2, 3, 4], {'z':'slug', 'u':3, 'y':'slug'})
        self.assertEqual((args, kwds), expected)        
        self.assertEqual(Ed(*args, **kwds), ('slug', (1, 2, 3, 4, 'slug'), {'u':3}))


    def test__F__0(self):
        """ test for TypeError on extra query values """
        self.assertRaises(TypeError, request_args, F, [], {'x':1})

    def test__F__1(self):
        """ test for no TypeError on extra query values when set to
            ignore additional args """
        results = request_args(F, [], {'x':1}, ignore_additional_args=True)
        self.assertEqual(results, empty_args)

    def test__F__2(self):
        """ test for empty path and query with extra positional args """
        self.assertEqual(request_args(F, [], {}), empty_args)

    def test__F__3(self):
        """ test for single path value and extra positional args """
        expected = ([1], {})
        self.assertEqual(request_args(F, [1], {}), expected)

    def test__F__4(self):
        """ test for two path values and extra positional args """
        expected = ([1, 2], {})
        self.assertEqual(request_args(F, [1, 2], {}), expected)

    def test__F__5(self):
        """ test for path value and query value with extra positional args """
        expected = ([1, 2], {})
        self.assertEqual(request_args(F, [1], {'z':2}), expected)

    def test__F__6(self):
        """ test for path value and query string value with extra positional args """
        expected = ([1, 'slug'], {})
        self.assertEqual(request_args(F, [1], {'z':'slug'}), expected)

    def test__F__7(self):
        """ test for query sequence value with extra positional args """
        expected = ([1, 2], {})
        self.assertEqual(request_args(F, [], {'z':(1,2)}), expected)


    def test__Fd__0(self):
        """ test for TypeError on additional query value with default
            positional and extra positional args
        """
        self.assertRaises(TypeError, request_args, Fd, [], {'x':1})

    def test__Fd__1(self):
        """ test for no TypeError on additional query value with
            default positional and extra positional args (when set to
            ignore additional args).
        """
        results = request_args(Fd, [], {'x':1}, ignore_additional_args=True)
        self.assertEqual(results, ([0], {}))

    def test__Fd__2(self):
        """ test for empty path and query with default positional and
            extra positional args
        """
        self.assertEqual(request_args(Fd, [], {}), ([0], {}))

    def test__Fd__3(self):
        """ test for single path value and empty query with default
            positional and extra positional args
        """
        expected = ([1], {})
        self.assertEqual(request_args(Fd, [1], {}), expected)

    def test__Fd__4(self):
        """ test for multiple path values and empty query with default
            positional and extra positional args
        """
        expected = ([1, 2], {})
        self.assertEqual(request_args(Fd, [1, 2], {}), expected)

    def test__Fd__5(self):
        """ test for path value and query value as default positional
            and extra positional args
        """
        expected = ([1, 2], {})
        self.assertEqual(request_args(Fd, [1], {'z':2}), expected)

    def test__Fd__6(self):
        """ test for path value as default positional and query string
            value as extra positional args
        """
        expected = ([1, 'slug'], {})
        self.assertEqual(request_args(Fd, [1], {'z':'slug'}), expected)

    def test__Fd__7(self):
        """ test for empty path and query sequence as default
            positional and extra positional args
        """
        expected = ([0, 1, 2], {})
        self.assertEqual(request_args(Fd, [], {'z':(1, 2)}), expected)


    def test__G__0(self):
        """ test for TypeError on path with only keyword args """
        self.assertRaises(TypeError, request_args, G, [1], {})

    def test__G__1(self):
        """ test for no TypeError on path with only keyword args when
            set to ignore additional args
        """
        results = request_args(G, [1], {}, ignore_additional_args=True)
        self.assertEqual(results, empty_args)

    def test__G__2(self):
        """ test for empty path and query with keyword args """
        self.assertEqual(request_args(G, [], {}), empty_args)

    def test__G__3(self):
        """ test for query with keywords """
        d = {'x':1, 'y':2}
        self.assertEqual(request_args(G, [], d), ([], d))

    ## TODO:  Gd tests

    def test__H__0(self):
        """ test for empty path and query with no positional, extra,
            or keyword args
        """
        self.assertEqual(request_args(H, [], {}), empty_args)

    def test__H__1(self):
        """ test for TypeError on path with no positional, extra, or
            keyword args
        """
        self.assertRaises(TypeError, request_args, H, [1, 2, 3], {})

    def test__H__2(self):
        """ test for TypeError on query with no positional, extra, or
            keyword args
        """        
        self.assertRaises(TypeError, request_args, H, [], {'x':1})

    def test__H__3(self):
        """ test for no TypeError on path with no positional, extra,
            or keyword args when set to ignore additional args
        """
        self.assertEqual(request_args(H, [1], {}, ignore_additional_args=True), empty_args)

    def test__H__4(self):
        """ test for no TypeError on query with no positional, extra,
            or keyword args when set to ignore additional args
        """        
        self.assertEqual(request_args(H, [], {'x':1}, ignore_additional_args=True), empty_args)        


if __name__ == '__main__':
    unittest.main()
