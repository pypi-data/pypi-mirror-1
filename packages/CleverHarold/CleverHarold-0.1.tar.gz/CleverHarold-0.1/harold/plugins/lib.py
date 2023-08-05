#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
#
# Common library for harold.plugins.
#
##
import os
import sys

from harold.lib import config_expression, detect_config, import_wrapper

from paste.deploy.converters import aslist
from paste.deploy.loadwsgi import ConfigLoader
from paste.script.command import Command

try:
    import sqlalchemy.mods.threadlocal
    import sqlalchemy
    import sqlalchemy.ext.activemapper as activemapper
except (ImportError, ):
    sqlalchemy = None

try:
    import sqlobject
except (ImportError, ):
    sqlobject = None


default_models_section = 'filter:data_provider_dev'


class HaroldCommandType(Command):
    """ Base type for paster commands implemented for Clever Harold

    """
    group_name = 'Clever Harold Commands'

    @staticmethod
    def db_handlers():
        return LinkCollector.types.items()

    @staticmethod
    def import_module(value):
        return import_wrapper(value)

    @staticmethod
    def as_list(value):
        return aslist(value)

    @staticmethod
    def as_expr(value):
        return config_expression(value)

    def named_handler(self, name, module):
        handlers = [v for k, v in self.db_handlers() if k in name]
        return handlers[0](module)

    def parse_args(self, args):
        """ extends Command.parse_args to include config file attributes

        """
        super(HaroldCommandType, self).parse_args(args)
        try:
            config_file = self.options.config
        except (AttributeError, ):
            pass
        else:
            self.config_loader = loader = ConfigLoader(config_file)
            self.config_parser = loader.parser


    @classmethod
    def standard_parser(cls, verbose=True, interactive=False,
                        no_interactive=False,
                        simulate=False,
                        quiet=False,
                        overwrite=False,
                        ## harold options
                        drop_first=False,
                        ignore_exc=False,
                        ini_file=False,
                        list_sections=False,
                        models_section=False):
        """ creates a pre-configured optparse parser instance

        @param verbose paste.script.command.Command option
        @param interactive paste.script.command.Command option
        @param no_interactive paste.script.command.Command option
        @param simulate paste.script.command.Command option
        @param quiet paste.script.command.Command option
        @param overwrite paste.script.command.Command option

        @param ini_file if true, adds -f --file option
        @param list_sections if true, adds -l --list option
        @param models_section if true, adds -m --models-section option

        @return optparse parser
        """
        parser = super(HaroldCommandType, cls).standard_parser(
            verbose=verbose,
            interactive=interactive,
            no_interactive=no_interactive,
            simulate=simulate,
            quiet=quiet,
            overwrite=overwrite)

        if drop_first:
            parser.add_option('-d', '--drop', dest='drop_first',
                              default=False, action='store_true',
                              help='Drop tables before create')

        if ignore_exc:
            parser.add_option('-i', '--ignore', dest='ignore_exc',
                              default=False, action='store_true',
                              help='Ignore database exceptions')
            
        if ini_file:
            default_file = detect_config() or ''
            default_filename = os.path.split(default_file)[-1]
            parser.add_option('-f', '--file', dest='config',
                              default=default_file, metavar='FILE', 
                              help=('use config FILE '
                                    '(local default is %s)' % default_filename))

        if models_section:
            parser.add_option('-s', '--section', dest='section',
                              default=default_models_section, metavar='SECTION',
                              help='Use the models named by SECTION'
                                   ' (default %s)' % default_models_section)

        if list_sections:
            parser.add_option('-l', '--list', dest='list_sections',
                              default=False, action='store_true',
                              help='print available database sections and exit')

        return parser


    def find_model_sections(self, config=None):
        """ locates all database provider sections

        """
        config = config or self.config_parser
        sections = config.sections()
        found = {}
        for section in sections:
            items = config.items(section)
            items = dict(items)
            has_key = items.has_key
            if has_key('dsn') and has_key('models') and has_key('use'):
                found[section] = items
        return found


    def show_model_sections(self, config=None, output=None):
        """ prints all database provider sections

        """
        config = config or self.config_parser
        if output is None:
            output = sys.stdout
        pad = ' ' * 4
        sections = self.find_model_sections(config).items()
        for section, entries in sorted(sections):
            print >> output
            print >> output, 'Section %s' % (section, )
            print >> output, pad, 'use = %s' % entries['use']
            print >> output, pad, 'dsn = %s' % self.as_expr(entries['dsn'])
            print >> output, pad, 'models = %s' % self.as_list(entries['models'])
            if entries.has_key('module'):
                print >> output, pad, 'module = %s' % entries['module']        


class LinkCollector(type):
    """ Metaclass to collect Link subclasses

    """
    types = {}

    def __init__(cls, name, bases, names):
        super(LinkCollector, cls).__init__(name, bases, names)
        if name != 'Link':
            LinkCollector.types[cls.entry_type] = cls


class Link(object):
    """ Base for other linkage types

    """
    __metaclass__ = LinkCollector

    
    def __init__(self, provider=None):
        if isinstance(provider, basestring):
            provider = import_wrapper(provider)
        self.provider = provider


    def scan(self, *modules):
        """ locates all table types in models

        @param modules one or more modules
        @return list of all tables in specified modules
        """
        tables = []
        for module in modules:
            contents = [getattr(module, k) for k in dir(module)]
            match = [self.table(v) for v in contents]
            match = [v for v in match if v]
            tables.extend(match)
        return tables


class ActiveMapperLink(Link):
    """ Provides recreating linkage for ActiveMapper user modules

    """
    entry_type = 'activemapper_provider'

    
    def table(self, table):
        """ returns table object if it looks like an ActiveMapper subclass

        @param table any object
        @return table if ActiveMapper as one of its base classes, or None
        """
        try:
            bases_names = [cls.__name__ for cls in table.__bases__]
        except (AttributeError, TypeError, ):
            link = SQLAlchemyLink()
            return link.table(table)
        else:
            return 'ActiveMapper' in bases_names and table

    def connect(self, table, dsn):
        """ connects to specified dsn

        @param table ActiveMapper subclass
        @param dsn data connection string or dictionary
        @return database engine
        """
        if sqlalchemy is None:
            raise Exception('ActiveMapper from SQLAlchemy not installed')
        engine = sqlalchemy.create_engine(dsn)
        try:
            table.table.metadata.connect(engine)
        except (AttributeError, ):
            link = SQLAlchemyLink()
            return link.connect(table, dsn)
        return engine


    def name(self, table):
        """ gets friendly table name

        @param table instance
        @return table name
        """
        try:
            return table.__name__
        except (AttributeError, ):
            link = SQLAlchemyLink()
            return link.name(table)


    def create(self, table, connection):
        """ creates specified table

        @param table ActiveMapper subclass
        @param connection ignored
        @return None
        """
        try:
            ## TODO:  this should be once per model, not for every table            
            activemapper.create_tables()
        except (AttributeError, ):
            link = SQLAlchemyLink()
            return link.create(table, connection)


    def drop(self, table, connection):
        """ drops specified table 

        @param table ActiveMapper subclass
        @param connection ignored
        @return None
        """
        try:
            activemapper.drop_tables()
        except (AttributeError, ):
            link = SQLAlchemyLink()
            return link.drop(table, connection)


class DBAPILink(Link):
    """ Provides recreating linkage for dbapi user modules

    """
    entry_type = 'dbapi_provider'
    

    def table(self, table):
        """ returns table object if it has create and drop strings

        @param table any object
        @return table if table has create and drop strings, or None
        """
        create = getattr(table, 'create', None)
        drop = getattr(table, 'drop', None)
        if create and drop and isinstance(create, basestring) \
               and isinstance(drop, basestring):
            return table


    def connect(self, table, dsn):
        """ connects to specified dsn

        @param table ignored
        @param dsn data connection string or dictionary
        @return database connection
        """
        if hasattr(dsn, 'keys'):
            return self.provider.connect(**dsn)
        else:
            return self.provider.connect(dsn)


    def name(self, table):
        """ gets friendly table name

        @param table instance
        @return table name
        """
        return '%s' % table.__name__


    def create(self, table, connection):
        """ creates specified table using connection

        @param table instance
        @param connection previously established dbapi connection
        @return None
        """
        cursor = connection.cursor()
        try:
            cursor.execute(table.create)
        except (Exception, ), ex:
            connection.rollback()
            raise Exception(ex.args[0])
        else:
            connection.commit()


    def drop(self, table, connection):
        """ drops specified table using connection

        @param table instance
        @param connection previously established dbapi connection
        @return None
        """
        cursor = connection.cursor()
        try:
            cursor.execute(table.drop)
        except (Exception, ), ex:
            connection.rollback()
            raise Exception(ex.args[0])            
        else:
            connection.commit()


class SQLAlchemyLink(Link):
    """ Provides recreating linkage for SQLAlchemy user modules

    """
    entry_type = 'sqlalchemy_provider'

    
    def table(self, table):
        """ returns table if it looks like a SQLAlchemy table

        @param table any object
        @return table if class name is Table, or None
        """
        try:
            is_table = table.__class__.__name__ == 'Table'
            return is_table and table
        except (AttributeError, ):
            pass


    def connect(self, table, dsn):
        """ connects to specified dsn

        @param table SQLAlchemy table
        @param dsn database connection string
        @return database engine
        """
        if sqlalchemy is None:
            raise Exception('SQLAlchemy not installed')
        engine = sqlalchemy.create_engine(dsn)
        table.metadata.connect(engine)
        return engine


    def name(self, table):
        """ gets friendly table name

        @param table SQLAlchemy Table
        @return tables displayname attribute
        """
        return table.displayname


    def create(self, table, connection):
        """ creates specified table

        @param table SQLAlchemy Table instance
        @param connection ignored
        @return None
        """
        ## TODO:  this should be once per model, not for every table
        table.metadata.create_all()


    def drop(self, table, connection):
        """ drops specified table

        @param table SQLAlchemy Table
        @param connection ignored
        @return None
        """
        table.drop()


class SQLObjectLink(Link):
    """ Provides recreating linkage for SQLObject user modules

    """
    entry_type = 'sqlobject_provider'


    def table(self, table):
        """ returns table if it looks like a SQLObject table

        @param table any object
        @return table if one base class name is SQLObject, or None
        """
        try:
            is_sqlobject = 'SQLObject' in [cls.__name__ for cls in table.__bases__]
            return is_sqlobject and table
        except (AttributeError, TypeError, ):
            pass


    def connect(self, table, dsn):
        """ connects to specified dsn

        @param table ignored
        @param dsn database connection string
        @return database connection
        """
        if sqlobject is None:
            raise Exception('SQLObject not installed')
        conn = sqlobject.connectionForURI(dsn)        
        sqlobject.sqlhub.processConnection = conn
        return conn


    def name(self, table):
        """ gets friendly table name

        @param table SQLObject
        @return table's __name__ attribute
        """
        return table.__name__


    def create(self, table, connection):
        """ creates specified table

        @param table SQLObject table
        @param connection ignored
        @return None
        """
        table.createTable()


    def drop(self, table, connection):
        """ drops specified table

        @param table SQLObject table
        @param connection ignored
        @return None
        """
        table.dropTable()

