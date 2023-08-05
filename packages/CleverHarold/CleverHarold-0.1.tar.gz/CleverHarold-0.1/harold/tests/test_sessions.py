#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

import unittest

from harold.lib import keys, header_match
from harold.sessions import Session
from harold.sessions.lib import FlupSession, PasteSession
from harold.tests.lib import test_app, make_start_response, wsgi_env


def name_selector(name):
    def selector(seq):
        for cls in seq:
            if cls.__name__.lower().count(name):
                return cls
    return selector

flup_selector = name_selector('flup')
paste_selector = name_selector('paste')

flup_set_cookie_match = header_match('set-cookie', '_sid_.+')
paste_set_cookie_match = header_match('set-cookie', '_sid_.+')


class TestApp:
    format = 'session counter : %s'

    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        session = environ[keys.session]()
        count = session.get('count', 0)
        count += 1
        session['count'] = count
        start_response('200 OK', [])
        return self.format % (count, )

    @classmethod
    def match(cls, value, count):
        return (cls.format % count) == value


class SessionFactory_Test(unittest.TestCase):
    def setUp(self):
        self.headers = []
        self.app = TestApp()

    def test_select_first(self):
        """ select first session provider """
        self.failUnless(Session(self.app))

    def test_select_second(self):
        """ select second session provider """
        self.failUnless(Session(self.app, lambda x:x[1] ) )

    def test_select_flup(self):
        """ select flup session provider """
        self.assertEqual(Session(self.app, flup_selector).type, FlupSession)

    def test_select_paste(self):
        """ select paste session provider """
        self.assertEqual(Session(self.app, paste_selector).type, PasteSession)

    def test_run_flup(self):
        """ match flup session provider output """
        self.run_and_match(flup_selector, flup_set_cookie_match)

    def test_run_paste(self):
        """ match paste session provider output """
        self.run_and_match(paste_selector, paste_set_cookie_match)

    def run_and_match(self, selector, matcher, count=10):
        app = Session(self.app)

        for i in range(count):
            env = wsgi_env()
            for k, v in self.headers:
                if k == 'Set-Cookie':
                    env['HTTP_COOKIE'] = '%s' % (v.split(';')[0], )
            res = app(env, make_start_response(self.headers))
            res.close()
            self.failUnless(matcher(self.headers))
            self.headers[:] = dict(self.headers).items()
            res = ''.join([d for d in res])
        self.failUnless(TestApp.match(res, count))


if __name__ == '__main__':
    unittest.main()
