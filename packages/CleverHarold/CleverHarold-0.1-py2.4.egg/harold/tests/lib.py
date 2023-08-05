#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from os.path import abspath, dirname, join
from StringIO import StringIO

import harold.log
harold.log.disable()

class TestApp:
    value = 'application complete'
    def __call__(self, environ, start_response):
        start_response('200 OK', [])
        return self.value

test_app = TestApp()

basic_env = {
        'REQUEST_METHOD': 'GET',
        'SCRIPT_NAME': '',
        'PATH_INFO': '',
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.0',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.input': StringIO(''),
        'wsgi.errors': StringIO(''),
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        }


def wsgi_env(**kwds):
    env = basic_env.copy()
    env.update(kwds)
    return env


def make_start_response(seq):
    def start_response(status, headers, exc=None):
        seq.extend(headers)
    return start_response

tests_home = dirname(abspath(__file__))

kid_template_dirs = [join(tests_home, name) for name in ('files_one',
                                                         'files_two',
                                                         'files_mixed')]

mod_template_dirs = [join(tests_home, name) for name in ('files_three',
                                                         'files_four',
                                                         'files_mixed',
                                                         'files_five')]

mdn_template_dirs = [join(tests_home, 'files_mdn'), ]
rst_template_dirs = [join(tests_home, 'files_rst'), ]
txt_template_dirs = [join(tests_home, 'files_txt'), ]
tmpl_template_dirs = [join(tests_home, 'files_tmpl'), ]

layout_template = join(tests_home, 'files_common/layout.kid')
default_templates= [join(tests_home, name) for name in ('files_common/default.kid', )]


