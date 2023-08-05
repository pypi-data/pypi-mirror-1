#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import unittest
from harold.armor.basetypes import basetypes


class ValidtorBaseTypes__Test(unittest.TestCase):
    def test_bool(self):
        """ basetype bool wrapper """
        b = basetypes[bool]
        assert b() is bool()
        assert b(0) is bool(0)
        assert b(1) is bool(1)
        assert b('a') is bool('a')

    def test_buffer(self):
        """ basetype buffer wrapper """
        b = basetypes[buffer]
        assert b('a') == buffer('a')
        assert b('a', 1) == buffer('a', 1)
        assert b('a', 1, 1) == buffer('a', 1, 1)

    def test_classmethod(self):
        """ basetype classmethod wrapper """
        c = basetypes[classmethod]
        assert type(c(_bool)) == type(classmethod(bool))

    def test_classmethod(self):
        """ basetype classmethod wrapper """
        c = basetypes[complex]
        assert c(0) == complex(0)
        assert c(0, 1) == complex(0, 1)

    def test_dict(self):
        """ basetype dict wrapper """
        d = basetypes[dict]
        assert d() == dict()
        assert d(a=1, b=2) == dict(a=1, b=2)
        assert d({'x':'x'}) == dict({'x':'x'})
        assert d([(1,2)]) == dict([(1,2)])

    def test_enumerate(self):
        """ basetype enumerate wrapper """
        e = basetypes[enumerate]
        assert type(e('asdf')) == type(enumerate('asdf'))

    def test_file(self):
        """ basetype file wrapper """
        f = basetypes[file]
        assert type(f('/dev/null')) == type(file('/dev/null'))

    def test_float(self):
        """ basetype float wrapper """
        f = basetypes[float]
        assert f() == float()
        assert f(1.1) == float(1.1)

    def test_frozenset(self):
        """ basetype frozenset wrapper """
        f = basetypes[frozenset]
        assert f() == frozenset()
        assert f('asdf') == frozenset('asdf')

    def test_int(self):
        """ basetype int wrapper """
        i = basetypes[int]
        assert i() == int()
        assert i(1) == int(1)
        assert i('1') == int('1')
        assert i('12', 8) == int('12', 8)

    def test_list(self):
        """ basetype list wrapper """
        l = basetypes[list]
        assert l() == list()
        assert l('asdf') == list('asdf')

    def test_long(self):
        """ basetype long wrapper """
        l = basetypes[long]
        assert l() == long()
        assert l(1) == long(1)
        assert l('1') == long('1')
        assert l('12', 8) == l('12', 8)    

    def test_object(self):
        """ basetype object wrapper """
        o = basetypes[object]
        assert type(o()) == type(object())

    def test_property(self):
        """ basetype property wrapper """
        p = basetypes[property]
        assert type(p()) == type(property())

    def test_reversed(self):
        """ basetype reversed wrapper """
        r = basetypes[reversed]
        assert type(r('asdf')) == type(reversed('asdf'))

    def test_set(self):
        """ basetype set wrapper """
        s = basetypes[set]
        assert s() == set()
        assert s('asdf') == set('asdf')

    def test_slice(self):
        """ basetype slice wrapper """
        s = basetypes[slice]
        assert s(None, 0, None) == slice(None, 0, None)

    def test_super(self):
        """ basetype super wrapper """
        s = basetypes[super]
        assert type(s(object)) == type(super(object))
        assert type(s(object, object())) == type(super(object, object()))
        class x(object):pass
        assert type(s(object, x())) == type(super(object, x()))

    def test_tuple(self):
        """ basetype tuple wrapper """
        t = basetypes[tuple]
        assert t() == tuple()
        assert t('asdf') == tuple('asdf')

    def test_type(self):
        """ basetype type wrapper """
        t = basetypes[type]
        assert t('a') == type('a')
        assert type(t('a', (object, ), {})) == type(type('a', (object, ), {}))

    def test_unicode(self):
        """ basetype unicode wrapper """
        u = basetypes[unicode]
        assert u('a') == unicode('a')
        assert u('a', 'utf8') == unicode('a', 'utf8')
        assert u('a', 'utf8', 'strict') == unicode('a', 'utf8', 'strict')


if __name__ == '__main__':
    unittest.main()

