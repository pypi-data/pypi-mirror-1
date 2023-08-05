#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# This module defines the function 'config_dict' that turns an
# .ini file for paste into a nested dictionary.  We use this to expose
# the run-time configuration to a Harold application.  It also allows
# us to keep the application configuration centralized in the .ini
# file.  DRY!

import os
import ConfigParser
from harold.lib import config_expression


class HaroldConfigParser(ConfigParser.SafeConfigParser):
    """ Parser type for reading Clever Harold application .ini files

    There isn't much here yet, but it's where we'll build out template
    string handling and expression handling.
    """
    def as_dict(self):
        sections = [ConfigParser.DEFAULTSECT] + self.sections()
        config = {}
        for section in sections:
            normname = str.join(':', [s.strip() for s in section.split(':')])
            config[normname] = items = {}
            entries = dict(self.items(section))
            for key, value in entries.items():
                entries[key] = config_expression(value)
            items.update(entries)
        return config

    @classmethod
    def parse_file(cls, filename, defaults=None):
        if defaults is None:
            defaults = {}
        defaults['here'] = os.path.dirname(os.path.abspath(filename))
        defaults['__file__'] = os.path.abspath(filename)
        parser = cls(defaults=defaults)
        parser.read(filename)
        return parser.as_dict()


config_dict = HaroldConfigParser.parse_file
