#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# This module defines the RecreateModels command for the paster script.
#
# Three database providers are supported:  DBAPI, SQLAlchemy and SQLObject.
#
# The command uses the same sections as the database middlware in a
# configuration file.  The keys "use", "dsn", and "models" are
# expected in each section.  For the DBAPI provider, the "module" key
# is respected.
#
# I tried to make the checks for 'is-a-table' use attribute lookup
# only (duck typing), but the orm implementations use too much
# __getattr__ magic to make it suitable.
#
##
from harold.plugins.lib import HaroldCommandType


class RecreateModels(HaroldCommandType):
    """ Creates or recreates the database tables from models in configuration

    """
    min_args = max_args = 0
    summary = 'Create or recreate database model'
    description = ('This command creates or recreates the model specified in the '
                   'configuration file.')

    parser = HaroldCommandType.standard_parser(
        quiet=True,
        drop_first=True,
        ini_file=True,
        ignore_exc=True,
        list_sections=True,
        models_section=True)

    parser.add_option('-n', '--no-populate', dest='populate',
                      default=True, action='store_false',
                      help='Skip populating models.')
    
    def command(self):
        """ recreates tables specified in models from configuration file

        @return None
        """
        loader = self.config_loader
        parser = self.config_parser
        options = self.options

        ignore_exc = options.ignore_exc
        section = options.section
        quiet = options.quiet

        dropped = created = excs = 0
        pad = ' ' * 4
        notables = '(no tables found)'

        if options.list_sections:
            self.show_model_sections()
            return 0

        try:
            parser.items(section)
        except (Exception, ), ex:
            print '%s. Aborting.' % ex.args[0]
            return 1
        else:
            section_map = dict(parser.items(section))

        try:
            use =  section_map['use']
            dsn = section_map['dsn']
            models = section_map['models']
            dbapi_module = section_map.get('module', None)
        except (KeyError, ), exc:
            args = (section, exc.args[0], )
            print 'Section "%s" missing key "%s".  Aborting.' % args
            return 2
        else:
            dsn = self.as_expr(dsn)
            models = self.as_list(models)
            if dbapi_module:
                dbapi_module = self.import_module(dbapi_module)

        if not quiet:
            print 'Values from section "%s":' % section
            print pad, 'use = "%s"' % use
            print pad, 'dsn = "%s"' % dsn
            print pad, 'models = %s' % ', '.join(['"%s"' % m for m in models])
            if dbapi_module:
                print pad, 'dbapi = "%s"' % dbapi_module.__name__

        try:
            models = [self.import_module(m) for m in self.as_list(models)]
        except (ImportError, ), exc:
            print 'Exception "%s" importing model.' % (exc, )
            return 3

        try:
            handler = self.named_handler(use, dbapi_module)
        except (IndexError, ):
            print 'No handler found for use = "%s".  Aborting.' % (use, )
            return 4
        else:
            if not quiet:
                args = (handler.__class__.__name__, use, )
                print
                print 'Selected handler "%s" for use = "%s"' % args

        for model in models:
            tables = handler.scan(model)

            if not quiet:
                print
                print 'Model: "%s"' % (model.__name__, )
                print 'Table%s:' % (len(tables) != 1 and 's' or '')
                for table in tables:
                    print pad, '"%s"' % handler.name(table)
                if not tables:
                    print pad, notables

            for table in tables:
                try:
                    connection = handler.connect(table, dsn)
                except (Exception, ), ex:
                    args = (ex.args[0], dsn, )
                    errors = 'Exception "%s" connecting to "%s".  Aborting.'
                    print errors % args
                    return 5

            if not quiet:
                print 'Actions:'
                if not tables:
                    print pad, notables
                    
            if options.drop_first:
                for table in tables:
                    name = handler.name(table)
                    try:
                        handler.drop(table, connection)
                    except (Exception, ), exc:
                        excs += 1
                        if not ignore_exc:
                            raise
                        elif not quiet:
                            args = (exc, name, )
                            error = 'Ignoring exception "%s" during "DROP %s"'
                            print pad, error % args
                    else:
                        dropped += 1
                        if not quiet:
                            print pad, 'dropped "%s"' % name

            for table in tables:
                name = handler.name(table)
                try:
                    handler.create(table, connection)
                except (Exception, ), exc:
                    excs += 1
                    if not ignore_exc:
                        raise
                    elif not quiet:
                        args = (exc, name, )
                        error = 'Ignoring exception "%s" during "CREATE %s"'
                        print pad, error % args
                else:
                    created += 1
                    if not quiet:
                        print pad, 'created "%s"' % name

            if hasattr(model, 'populate'):
                if options.populate:
                    if not quiet:
                        print 'Populating model...',
                    model.populate()
                    if not quiet:
                        print 'populated.'
                elif not quiet:
                    print 'Skipped populating model.'
            elif not quiet:
                print "No 'populate' callable found."


        warning = (excs > 0 and created == 0)
        if not quiet or warning:
            print '\n',
            if warning:
                print '*WARNING* ',
            print 'Dropped %i table%s,' % (dropped, (dropped != 1 and 's' or '')),
            print 'created %i table%s,' % (created, (created != 1 and 's' or '')),
            print 'ignored %i exception%s.' % (excs, (excs != 1 and 's' or ''))
