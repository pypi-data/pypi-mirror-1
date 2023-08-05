#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from inspect import getargspec
import unittest

from harold.lib import ValidationError, DecorationError
from harold.armor import (email_formatted, bound_len, safe_sniff,
                          alphanum_only, hostname_formatted,
                          add, fuse)



class ArmorTestBase:
    good_inputs = ()
    bad_inputs = ()
    format_calls = ()


    def run_good_inputs(self):
        for name in self.good_inputs:
            for call in self.format_calls:
                try:
                    call(name)
                except (Exception, ):
                    raise AssertionError('false negative', name)


    def run_bad_inputs(self):
        for name in self.bad_inputs:
            for call in self.format_calls:
                try:
                    call(name)
                except (Exception, ):
                    pass
                else:
                    raise AssertionError('false positive', name)


class ArmorEmailInput__Test(ArmorTestBase, unittest.TestCase):
    good_inputs = (
        'a@b.cd',
        'john@smith.com',
        'fred@example.com',
        'john.smith@example.com',
        'john__smith@e.net',
        't@b.ne',
        'troy@example.com',
        'base.base@gmail.com'
    )

    bad_inputs = (
        'troy',
        'www',
        'john smith@example.com', '$\\'
        'with a space@example.com',
        'nodomain@.tld',
        'notld@domain',
        '@example.com',
    )

    format_calls = (
        email_formatted,
    )

    def test_invalid_emails(self):
        """ invalid email input """
        self.run_bad_inputs()
        
    def test_valid_emails(self):
        """ valid email input """
        self.run_good_inputs()


class ArmorLengthInput__Test(ArmorTestBase, unittest.TestCase):
    good_inputs = (
        '4444', '5555', '666666'
    )

    bad_inputs = ('1', '22', '333', '7777777')

    format_calls = (
        bound_len(4, 6),
    )


    def test_invalid_length(self):
        """ invalid input length """
        self.run_bad_inputs()


    def test_valid_length(self):
        """ valid input length """
        self.run_good_inputs()


class ArmorSimpleInput__Test(ArmorTestBase, unittest.TestCase):
    good_inputs = (
        'one', 'two', 'three',
    )

    bad_inputs = ("fo'ur",
                  "fiv--e",
                  "si;x",
    )

    format_calls = (
        safe_sniff,
        alphanum_only,
    )

    def test_invalid_simple(self):
        """ invalid simple input """
        self.run_bad_inputs()


    def test_valid_simple(self):
        """ valid simple input """
        self.run_good_inputs()


class ArmorHostNameInput__Test(ArmorTestBase, unittest.TestCase):
    good_inputs = (
        'four',
        'five',        
        'six.seven',
    )

    bad_inputs = (
        'eight space',
    )

    format_calls = (
        hostname_formatted,
    )


    def test_invalid_hostname(self):
        """ invalid hostname input """
        self.run_bad_inputs()


    def test_valid_hostname(self):
        """ valid hostname input """
        self.run_good_inputs()


@fuse
@add('a',  lambda v:str(v), lambda v:int(v))
def fancy(a, b, *c, **d):
    return (a, b, c, d)


def plain(a, b, *c, **d):
    return (a, b, c, d)


@fuse
@add('a', lambda x:int(x))
@add('b', lambda x:int(x))
def twotuple(a, b):
    return (a, b)


class ArmorDecorator__Test(unittest.TestCase):
    def test_equal_results(self):
        """ armor decorated results equal to undecorated results """
        self.assertEqual(plain(1,2,3,4, e=5), fancy(1,2,3,4, e=5))

    def test_equal_argspecs(self):
        """ armor decorated argspec equal to undecorated argspec """
        self.assertEqual(getargspec(plain), getargspec(fancy))

    def test_fail_validate(self):
        """ armor decorated raises ValueError """
        self.assertRaises(ValueError, fancy, 'no int', 2)

    def test_fail_validate_error_values(self):
        """ armor decorated raises ValueError with errors values """
        try:
            twotuple('abc', 'def')
        except (ValueError, ), exc:
            errargs = [err[0] for err in exc.args[0]]
            assert errargs == ['a', 'b']

    def test_fail_validate_partial_values(self):
        """ armor decorated raises ValueError with error and valid values """        
        try:
            twotuple(1, 'def')
        except (ValueError, ), exc:
            errargs = [err[0] for err in exc.args[0]]
            valargs = [val[0] for val in exc.args[1]]
            assert errargs == ['b', ]
            assert valargs == ['a', ]


def toint(x):
    return int(x)

def toints(x, y):
    return int(x), int(y)

def tostr(x):
    return str(x)

def tostrs(x, y):
    return str(x), str(y)

neverworks_reason = 'none given'
def neverworks(*x, **y):
    raise Exception(neverworks_reason)

def alwaysworks(*x, **y):
    return x, y

def mkdbl(x):
    return x + x

def allints(s):
    for v in s:
        assert int(v) == v
    return s


class ValidatorConversion__Test(unittest.TestCase):
    def test_simple(self):
        """ armor decorated single parameter """
        @fuse
        @add('a', toint)
        def simple(a):
            return a

        self.assertEqual(simple('123'), 123)


    def test_mixed(self):
        """ armor decorated one single parameter, one mixed, one undecorated """
        @fuse
        @add('q', toint)
        @add('r', tostr)
        @add(('q', 's'), toints)
        def mixed(q, r, s):
            return q, r, s

        self.assertEqual(mixed('10', 11, '12'), (10, '11', 12))


    def test_more_mixed(self):
        """ armor decorated two parameter pairs """
        @fuse
        @add(('a', 'b'), toints)
        @add(('c', 'd'), tostrs)
        def again(a, b, c, d):
            return a, b, c, d

        self.assertEqual(again('1', '2', 3, 4), (1, 2, '3', '4'))


    def test_odd_mixed(self):
        """ armor decorated two parameter pairs non-adjacent """
        @fuse
        @add(('a', 'c'), toints)
        @add(('b', 'd'), tostrs)
        def again(a, b, c, d):
            return a, b, c, d

        self.assertEqual(again('1', 2, '3', 4), (1, '2', 3, '4'))


class ValidatorParameter__Test(unittest.TestCase):
    def test_simple(self):
        """ armor decorated three simple conversions """
        @fuse
        @add('a', toint)        
        @add('b', toint)        
        @add('c', toint)
        def simple(a, b, c):
            return a, b, c

        self.assertEqual(simple('1', '2', '3'), (1, 2, 3))


    def test_exception(self):
        """ armor decorated raises exception """
        @fuse
        @add('a', neverworks)
        def simple(a, b):
            return a, b

        self.assertRaises(Exception, simple, 1, 2)


    def test_some_valid(self):
        """ armor decorated function exception valid and error values """
        @fuse
        @add('a', toint)
        @add('b', neverworks)
        @add('c', tostr, mkdbl)
        @add('d', neverworks)
        def some(a, b, c, d):
            return a, b, c, d

        try:
            some(1, 2, 3, 4)
        except (ValidationError, ), exc:
            invalids, valids = exc.args
            self.failUnless('a' in valids)
            self.failUnless('c' in valids)
            self.assertEqual(valids['a'], [(1, ), ])
            self.assertEqual(valids['c'], [('33', ), ('3', ) ])

            self.failUnless('b' in invalids)
            self.failUnless('d' in invalids)

            self.failUnless(invalids['b'], [(neverworks_reason, )])
            self.failUnless(invalids['d'], [(neverworks_reason, )]) 
        else:
            raise Exception('function worked when it should not have')


    def test_mulitple_parameters(self):
        """ armor decorated multiple-parameter valid and error values """
        @fuse
        @add(('a', 'b'), neverworks)
        def multi(a, b):
            return a, b

        try:
            multi(1, 2)
        except (ValidationError, ), exc:
            invalids, valids = exc.args
            self.failUnless('a' in invalids)
            self.failUnless('b' in invalids)
            self.assertEqual(invalids['a'], [(neverworks_reason, )])
            self.assertEqual(invalids['b'], [(neverworks_reason, )])


    def test_chained_messages(self):
        """ armor decorated chained conversions """
        @fuse
        @add('a', toint, tostr, mkdbl, neverworks)
        @add('b', tostr, toint, mkdbl, neverworks)
        @add('c', alwaysworks)
        def simple(a, b, c):
            return x, y

        try:
            simple(1, 2, 3)
        except (ValidationError, ), exc:
            invalids, valids = exc.args
            self.failUnless('a' in invalids) # because neverworks was last
            self.failUnless('a' in valids) # because the others came first
            self.assertEqual(valids['a'], [('11', ), ('1', ), (1, )]) # toint, tostr, mkdbl

            self.failUnless('b' in invalids) # because neverworks was last
            self.failUnless('b' in valids) # because the others came first
            self.assertEqual(valids['b'], [(4,), (2,), ('2',)]) # tostr, toint, mkdbl


    def test_extra_positionals(self):
        """ armor decorated extra positional parameter conversion """
        @fuse
        @add('a', toint)
        def thing(a, *b):
            return (a, ) + b

        self.assertEqual(thing('1', 2, 3), (1, 2, 3))


    def test_default_parameters(self):
        """ armor decorated default value conversion """
        @fuse
        @add('a', tostr)
        @add('b', tostr)
        def simple(a=1, b=2):
            return a, b

        self.assertEqual(simple(3, 4), ('3', '4'))
        ## whoa, this works without explict support      
        self.assertEqual(simple(), ('1', '2'))


    def test_keyword_parameters(self):
        """ armor decorated keyword parameters """
        @fuse
        @add('a', tostr)
        @add('b', tostr)
        def multi(a, b, **c):
            return a, b, c

        assert multi(3, 4, w=5) == ('3', '4', {'w':5})


    def test_deco_requires_existing_argname(self):
        """ armor decorated exception on missing name in function definition """
        try:
            @add('a', toint)
            def simple(b):
                return b
        except (DecorationError, ):
            ## defining the function produces the exception, so this
            ## is what we want
            pass
        else:
            raise Exception('name mismatch accepted but should not have been')


if __name__ == '__main__':
    unittest.main()
