#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
#
# Top-level command for paste to serve harold project without
# specifying config file.
#
##

from harold.lib import detect_config
from paste.script.serve import ServeCommand


class ServeHarold(ServeCommand):
    min_args = 0
    max_args = 2
    takes_config_file = 0

    def command(self):
        if len(self.args) > 1:
            pass
        else:
            config = detect_config()
            if config:
                self.args.insert(0, config)
        app_name = self.options.app_name
        if app_name is None:
            self.options.reload = True
        ServeCommand.command(self)
