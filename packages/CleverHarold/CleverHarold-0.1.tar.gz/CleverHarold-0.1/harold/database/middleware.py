#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from harold.lib import keys, import_wrapper
from harold.log import logger

try:
    import sqlalchemy.mods.threadlocal
    import sqlalchemy
    import sqlalchemy.ext.activemapper as activemapper
    import sqlalchemy.ext.sessioncontext as sessioncontext
except (ImportError, ):
    sqlalchemy = None

try:
    import sqlobject
except (ImportError, ):
    sqlobject = None


class DataProvider(object):
    """ Base class for database middleware 

    Subclasses must implement:

    - connect(environ)
    - disconnect(environ, exception=None)
    
    @param app contained WSGI application
    @param dsn data source name
    @param models sequence of model modules
    @param dbapi optional module object or string
    @param debug flag for debug settings
    """
    def __init__(self, app, dsn, models, module=None, debug=True):
        self.app = app
        self.dsn = dsn
        self.models = models
        if isinstance(module, basestring):
            module = import_wrapper(module)
        self.module = module
        self.debug = debug
        self.log = logger(self)

    def __call__(self, environ, start_response):
        try:
            self.connect(environ)
            self.log.debug('connected')
        except (Exception, ), ex:
            self.log.error('exception connecting', exc_info=ex)
            raise

        try:
            results = self.app(environ, start_response)
        except (Exception, ), ex:
            self.log.error('application exception', exc_info=ex)
            try:
                self.disconnect(environ, ex)
            except (Exception, ), exc:
                self.log.error('exception disconnecting', exc_info=exc)
            raise

        try:
            self.disconnect(environ)
            self.log.debug('disconnected')
        except (Exception, ), exc:
            self.log.error('exception disconnecting', exc_info=exc)                
        return results


    def connect(self, environ):
        raise NotImplementedError


    def disconnect(self, environ, exception=None):
        raise NotImplementedError


    def __str__(self):
        return '<%s @ %s>' % (self.__class__.__name__, self.dsn, )


class SQLAlchemyProvider(DataProvider):
    """ SQLAlchemy data provider

    This type assumes that SQLAlchemy has been imported and an metadata
    instance of some kind has been made ready for connection.
    """
    def __init__(self, *args, **kwds):
        if sqlalchemy is None:
            raise RuntimeError('SQLAlchemy referenced but not installed')
        super(SQLAlchemyProvider, self).__init__(*args, **kwds)

        self.engine = sqlalchemy.create_engine(self.dsn)
        for model in self.models:
            try:
                md = getattr(model, '__metadata__', getattr(model, 'metadata'))
            except (AttributeError, ):
                pass
            else:
                md.connect(self.engine)


    def connect(self, environ):
        """ connects to database and stores connection in environment

        This method currently sucks because (1) we're not connecting
        the tables because that doesn't work, and (2) we're not
        estabilishing any session or transaction for the request.
        
        @param environ WSGI request environment
        @return None
        """
        session = environ[keys.data_session] = \
            sqlalchemy.create_session(self.engine)
        
        for model in self.models:
            try:
                os = model.objectstore
            except (AttributeError, ):
                pass
            else:
                os.context.current = session


    def disconnect(self, environ, exception=None):
        """ commits pending changes and closes connection


        @param environ WSGI request environment
        @return None
        """
        session = environ[keys.data_session]
        if exception:
            session.close()
            return
        
        try:
            session.flush()
        except (Exception, ), ex:
            self.log.error('exception during session flush', exc_info=ex)
            try:
                session.clear()
            except (Exception, ), ex:
                msg = 'second exception during session clear'
                self.log.error(msg, exc_info=ex)
            else:
                self.log.error('session cleared after exception')

        try:
            session.close()
        except (Exception, ), ex:
            self.log.error('exception during session close', exc_info=ex)
        else:
            self.log.info('session closed')


class ActiveMapperProvider(SQLAlchemyProvider):
    """ ActiveMapper data provider

    """
    def __init__(self, *args, **kwds):
        if sqlalchemy is None:
            raise RuntimeError('ActiveMapper referenced but SQLAlchemy not installed')
        super(ActiveMapperProvider, self).__init__(*args, **kwds)
        self.engine = sqlalchemy.create_engine(self.dsn)

    def connect(self, environ):
        """ connects to database and stores connection in environment

        """
        activemapper.objectstore.context.current = \
            environ[keys.data_session] = \
                sqlalchemy.create_session(self.engine)


class SQLObjectProvider(DataProvider):
    """ not implemented

    """
    def __init__(self, *args, **kwds):
        if sqlobject is None:
            raise RuntimeError('SQLObject referenced but not installed')
        super(SQLObjectProvider, self).__init__(*args, **kwds)
        #self.conn = sqlobject.dbconnection.ConnectionHub()
        
    def connect(self, environ):
        """ connects to database and stores connection in environment

        """
        if self.debug:
            print '%s opening %s' % (self, environ['PATH_INFO'], )
        environ[keys.data_connection] = \
            sqlobject.sqlhub.processConnection  = \
                sqlobject.connectionForURI(self.dsn)


    def disconnect(self, environ, exception=None):
        """ commits pending changes and closes connection

        @param environ WSGI request environment
        @return None
        """


class DBAPIProvider(DataProvider):
    """ 

    """
    def connect(self, environ):
        """ connects to database and stores connection in environment

        @param environ WSGI request environment
        @return None
        """
        dsn = self.dsn
        if isinstance(dsn, dict):
            con = self.module.connect(**dsn)
        else:
            con = self.module.connect(dsn)
        environ[keys.data_connection] = con


    def disconnect(self, environ, exception=None):
        """ commits pending changes and closes connection

        @param environ WSGI request environment
        @return None
        """
        con = environ[keys.data_connection]
        if exception:
            con.rollback()
        else:
            con.commit()
        con.close()


    def __str__(self):
        args = (self.__class__.__name__, self.module.__name__,
                self.dsn, abs(id(self)))
        return '<%s (%s @ %s) at 0x%x>' % args
