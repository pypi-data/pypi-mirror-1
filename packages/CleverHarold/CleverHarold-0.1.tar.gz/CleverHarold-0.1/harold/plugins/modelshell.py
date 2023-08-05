#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
#
# Command to start an interactive shell with models and database
# connections pre-loaded.
#
##

import code
import os
import site
import sys

import harold
from harold.plugins.lib import HaroldCommandType

try:
    import IPython
except (ImportError, ), ex:
    IPython = ipinfo = ''
else:
    ipinfo = ('\nSee IPython.Revision module for '
              'IPython copyright, credits and license.')


intro = """%s %s %s
%s on %s
Type "help", "copyright", "credits" or "license" for more information

See __builtin__ module for Python copyright, credits, and license.%s

Important:  commit your changes before you exit.  You will not be prompted.
""" % (harold.name,
       harold.version,
       harold.date,
       sys.version.split('\n')[1],
       sys.platform,
       ipinfo)


def shell_namespace(initial):
    """ constructs locals for a ModelInterp

    """
    mapping = {}
    keys = ('license', 'copyright', 'credits')
    printer = site._Printer
    mapping.update([(k, printer(k, getattr(harold, k))) for k in keys])
    mapping.update(initial)
    return mapping


class ModelInterp(code.InteractiveConsole):
    """ Default ModelInterp type

    """
    def __init__(self, ns):
        code.InteractiveConsole.__init__(self, shell_namespace(ns))

    def run(self, banner):
        return self.interact(banner)


if IPython:
    class ModelInteractive(IPython.iplib.InteractiveShell):
        """ Wrapper for the internal IP shell

        """
        def __init__(self, name, **kwds):
            name = 'ipython_harold'
            IPython.iplib.InteractiveShell.__init__(self, name, **kwds)

    class ModelInterp(IPython.Shell.IPShell):
        """ IPython-powered ModelInterp type

        """
        def __init__(self, ns):
            user_ns = shell_namespace(ns)
            IPython.Shell.IPShell.__init__(self, argv=[], user_ns=user_ns,
                                           shell_class=ModelInteractive)

        def run(self, banner):
            return self.mainloop(banner=banner)


class ModelShell(HaroldCommandType):
    """ Starts shell

    """
    min_args = max_args = 0
    summary = 'Run interactive interpreter with models'
    description = ('Run interactive interpreter preloaded with '
                   'database models and connections.')

    parser = HaroldCommandType.standard_parser(
        quiet=True,
        ini_file=True,
        list_sections=True,
        models_section=True)

    def command(self):
        """ starts interactive interpreter with models and connections

        @return None
        """
        options = self.options
        config_loader = self.config_loader
        
        if not options.config:
            print 'Config file not found or not specified.  Aborting.'
            return 1
        if not os.path.exists(options.config):
            print 'Could not read %s.  Aborting.'  % (options.config, )
            return 2

        if options.list_sections:
            self.show_model_sections()
            return 0

        model_sections = self.find_model_sections()
        try:
            section = model_sections[options.section]
        except (KeyError, ):
            print 'Could not load section %s.  Aborting.' % (options.section, )
            return 3

        use = section['use']
        dsn = self.as_expr(section['dsn'])
        models = self.as_list(section['models'])
        dbapi_module = section.get('module', None)

        try:
            models = [self.import_module(m) for m in models]
        except (ImportError, ), exc:
            print 'Exception "%r" importing model.' % (exc, )
            return 3
            
        try:
            handler = self.named_handler(use, dbapi_module)
        except (IndexError, ):
            print 'No handler found for use = "%s".  Aborting.' % (use, )
            return 4

        tables = handler.scan(*models)
        for table in tables:
            handler.connect(table, dsn)

        config_ns = {}
        config_ns.update([(handler.name(tbl), tbl) for tbl in tables])
        
        shell = ModelInterp(config_ns)
        shell.run(intro)
