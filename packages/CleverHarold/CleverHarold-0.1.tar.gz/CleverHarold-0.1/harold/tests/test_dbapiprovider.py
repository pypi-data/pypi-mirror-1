#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
#
##

import os
import sys
import unittest

from harold.database import DBAPIProvider
from harold.lib import keys, config_expression, import_wrapper
from harold.tests.lib import (test_app, tests_home,
                              make_start_response, wsgi_env, )


class DBAPIProvider_Base(unittest.TestCase):
    def setUp(self):
        self.dsn = self.get_dsn()
        self.headers = []

    @classmethod
    def get_dsn(cls):
        dsn_file = os.path.join(tests_home, cls.dsn_filename)
        dsn = None
        if os.path.exists(dsn_file):
            dsn = config_expression(open(dsn_file).read())
        return dsn


    def run_app(self, app, path, query='', **kwds):
        environ = wsgi_env(PATH_INFO=path, QUERY_STRING=query)
        environ.update(kwds)
        results = app(environ, make_start_response(self.headers))
        return environ, results


    def connected(self):
        class ConnectedTester:
            ## test that a connection was open by creating a cursor
            ## from it
            def __init__(self, app):
                self.app = app
                self.was_connected = False
                
            def __call__(self, environ, start_response):
                conn = environ[keys.data_connection]
                cur = conn.cursor()
                self.was_connected = True
                return self.app(environ, start_response)

        app = DBAPIProvider(ConnectedTester(test_app), self.dsn, [], self.module, False)
        self.run_app(app, '/')
        self.failUnless(app.app.was_connected)


    def disconnected(self):
        app = DBAPIProvider(test_app, self.dsn, [], self.module, False)
        env, res = self.run_app(app, '/')
        conn = env[keys.data_connection]
        disco = False
        try:
            cur = conn.cursor() # for sqlite and postgresql
            conn.close() # for mysql
        except:
            disco = True
        self.failUnless(disco)


class DBAPIProvider_MySQL_Test(DBAPIProvider_Base):
    dsn_filename = 'mysql.dsn'
    module = 'MySQLdb'

    def test__0__connected(self):
        """ test mysql connected """
        self.connected()

    def test__0__disconnected(self):
        """ test mysql disconnected """
        self.disconnected()


class DBAPIProvider_PostgreSQL_Test(DBAPIProvider_Base):
    dsn_filename = 'postgresql.dsn'
    module = 'psycopg2'

    def test__0__connected(self):
        """ test postgresql connected """
        self.connected()

    def test__0__disconnected(self):
        """ test postgresql disconnected """
        self.disconnected()


class DBAPIProvider_SQLite_Test(DBAPIProvider_Base):
    dsn_filename = 'sqlite.dsn'
    module = 'pysqlite2.dbapi2'
        
    def test__0__connected(self):
        """ test sqlite connected """
        self.connected()

    def test__0__disconnected(self):
        """ test sqlite disconnected """
        self.disconnected()


if not DBAPIProvider_MySQL_Test.get_dsn():
    print >> sys.stderr, 'No dsn file found for MySQL; removing test case'
    del(DBAPIProvider_MySQL_Test)


if not DBAPIProvider_PostgreSQL_Test.get_dsn():
    print >> sys.stderr, 'No dsn file found for PostgreSQL; removing test case'
    del(DBAPIProvider_PostgreSQL_Test)


# sqlite.dsn is in the repository; no need to check for it or remove
# its test case.


if __name__ == '__main__':
    unittest.main()
