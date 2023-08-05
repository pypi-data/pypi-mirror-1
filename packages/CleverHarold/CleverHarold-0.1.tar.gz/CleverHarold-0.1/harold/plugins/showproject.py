#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from harold.plugins.lib import HaroldCommandType


class ShowProject(HaroldCommandType):
    """ Shows a Clever Harold project configuration and more.

    This isn't finished.  Ideas:

    - ini file summary, server, database, connection, but not all middleware
    - code metrics, number of files, lines, classes, functions
    
    """
    min_args = 1
    max_args = 1
    summary = 'Show Clever Harold project setup'

    parser = HaroldCommandType.standard_parser(verbose=True)

    def command(self):
        if self.verbose:
            print 'Verbose show'
        print 'Nothing yet to show'
