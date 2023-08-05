#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

def get():
    return '__init__.py', 'get'

def post(a, b):
    return a, b

def head():
    return 'head test'

def delete():
    return 'delete test'

get.expose = True
post.expose = True
head.expose = True
delete.expose = True
