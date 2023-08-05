#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Synopsis
# --------
#
# Create Clever Harold projects with the paster script::
#
#    $ paster init-harold
#    $ paster create -t harold
#
# (Other commands in are in development).
#
# Include Clever Harold applications and middleware in paste config
# files::
#
#    [filter:my_kid_templates]
#    use = egg:CleverHarold#kid_publisher
#    dirs = /some/path/to/templates
#
#    [filter:my_python_modules]
#    use = egg:CleverHarold#code_publisher
#    dirs = /some/path/to/code
#
##
