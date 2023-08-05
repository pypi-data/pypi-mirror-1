#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# This module defines two plugins for the paster script that do
# essentially the same thing.
#
# The HaroldTemplate type plugs into paster so you can type::
#
#    $ paster create -t harold
#
# The HaroldCreate type plugs into paster so you can do the same thing
# with less finger movement::
#
#    $ paster init-harold
#
# Which one you use is entirely a matter of your own preference.
#
##

from paste.script.command import Command
from paste.script.create_distro import CreateDistroCommand
from paste.script.templates import Template


class HaroldTemplate(Template):
    """ Creates a Clever Harold project via 'paste create -t harold'

    """
    summary = 'A Clever Harold project'
    _template_dir = '../project/'
    egg_plugins = ['CleverHarold']
    required_templates = ['basic_package']
    use_cheetah = True


class HaroldCreate(Command):
    """ Creates a Clever Harold project via 'paste init-harold'

    """
    min_args = 0
    max_args = 1
    usage = 'NAME'
    summary = 'Create a new Clever Harold project'

    parser = Command.standard_parser(verbose=True)
    parser.add_option('-o', '--orm-type',
                      dest='orm_type',
                      metavar='ORM',
                      help='Add initial models using specified ORM package.')

    def command(self):
        """ create a Clever Harold project

        """
        if self.verbose:
            print 'Creating new Clever Harold project...'
        c = CreateDistroCommand('harold')
        args = self.args
        args.append('-t CleverHarold#harold')
        c.parse_args(args)
        c.run(args)
        if self.verbose:
            print 'Clever Harold project created.'
