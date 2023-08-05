#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

## an import of an extesion module will tickle the strange behavior
## of the import machinery if the module name isn't set nicely.
import socket, random

def get():
    return 'callables within modules (but not packages work), too'
get.expose = True


