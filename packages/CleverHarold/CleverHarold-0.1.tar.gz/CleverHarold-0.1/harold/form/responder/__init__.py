#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Package of routines for responding to HTML form submission.
#
# Synopsis
# --------
#
# ::
#
#    from harold import form
#
#    @form.responder.json
#    def search(phrase):
#        """ on exception, will return json data """
#
#    @form.responder.redirect
#    def signup(name, password):
#        """ on exception, will redirect to originally requested page with error data """
# 
##

from formexc import redirect
from jsonexc import json

