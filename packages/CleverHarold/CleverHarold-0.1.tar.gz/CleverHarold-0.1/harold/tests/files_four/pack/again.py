#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

def get():
    return 'again'

def get(x, y, z=6):
    return x, y, z

def bar(x, y, z=[]):
    return x, y, z

get.expose = True
bar.expose = True

