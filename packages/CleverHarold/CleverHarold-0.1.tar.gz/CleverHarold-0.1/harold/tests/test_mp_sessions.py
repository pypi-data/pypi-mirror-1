#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Testing python code running under mod_python isn't very simple.
# The mod_python distribution has a package to do it, but it might not
# be installed even if mod_python is on the target system.  In the interest
# of expediency, this test case uses a mod_python config like this::
#
#     <Location "/harold_mod_python_session_test">
#     SetHandler mod_python
#
#     PythonHandler harold.lib.mpwsgi::handler
#     PythonOption wsgi.app harold.tests.mpsession_app::handler
#     PythonOption wsgi.scr "/harold_mod_python_session_test"
#     </Location>
#
##

import unittest
from harold.tests.test_sessions import TestApp

session_url = 'http://localhost/harold_mod_python_session_test'


class ApacheModPythonSession_Test(unittest.TestCase):
    def setUp(self):
        import mechanize        
        self.url = session_url
        self.browser = mechanize.Browser()

    def test_session_counter(self):
        """ match mod_python session provider output """
        count = 3
        for i in range(count):
            response = self.browser.open(self.url)
            results = response.read()
        self.failUnless(TestApp.match(results, count))


if __name__ == '__main__':
    unittest.main()
    
