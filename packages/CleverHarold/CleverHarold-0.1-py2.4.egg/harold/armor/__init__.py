#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Package to protect callables with argument validation and transformation.
#
# Synopsis
# --------
#
# ::
#
#    from harold import armor
#    from mypackage import valid_part, lookup_store, valid_part_at_store
#
#    @armor.fuse
#    @armor.add('part_id', int, valid_part)
#    @armor.add('store_id', lookup_store)
#    @armor.add(('part_id', 'store_id'), valid_part_at_store)
#
#    def inventory(part_id, store_id):
#        return inventory_lookup(part_id, store_id)
#
#    inventory.expose = True
#
##
from validatorexc import add, fuse
from validatorlib import *

