#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Package to decouple applications from various available session implementations.
#
# Synopsis
# --------
#
# Client code::
#
#    def get(name, session):
#        count = session.get('count', 0) + 1
#        session['count'] = count
#        return 'Hello, %s, you have been here %s times' % (name, count)
#
#    get.expose = True
#
# Application code::
#
#    from harold.sessions import Session
#    from mypackage import myapp
#
#    app = Session(myapp)
#
##

from harold.sessions.lib import Session
