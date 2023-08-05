#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>


## import kid

## def add(names, *params):
##     def deco(original):
##         try:
##             fieldmap = original.func_formfields
##         except (AttributeError, ):
##             fieldmap = original.func_formfields = []

##         try:
##             fields = fieldmap[fieldmap.index(names)]
##         except (ValueError, ):
##             fields = []
##             fieldmap.append((names, fields))

##         fields.extend(params)
##         return original
        
##     return deco



## def html(func):
##     ser = kid.XMLSerializer()
##     fieldmap = func.func_formfields
##     for names, ctors in fieldmap:
##         ctor = ctors[0]
##         print names, ''.join( (ser.generate(ctor(names), fragment=1)) )

        
