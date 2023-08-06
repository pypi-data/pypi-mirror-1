#!/usr/bin/env python
# vim:ts=4:sw=4:et

'''
WSGI middleware for web app with Storm ORM db interface.

This is the database access inteface for WSGI enabled (PEP 333) web applications.

Simple usage:

    from wsgiref.simple_server import make_server
    from storm.database import create_database
    
    from middlestorm import MiddleStorm
    
    def storm_app(environ, start_response):
        # thread safe Store object instance
        store = environ['storm.store']
        # application logic
        # ...
    
    db = create_database('postgres://user:password@host/base')
    app = MiddleStorm(storm_app, db)
    
    make_server('', 8000, app).serve_forever()

Copyright (c) 2007-2008 Vsevolod S. Balashov under terms of GNU LGPL v.2.1

TODO more docstrings
'''

__author__ = "Vsevolod Balashov"
__email__ = "vsevolod at balashov dot name"
#TODO __version__ = "$Revision$"

from storm.database import Database, create_database
from storm.store import Store
from threading import local
from functools import wraps

__all__ = ["MiddleStorm"]

class MiddleStorm(object):
    """WSGI middleware.
    Add Store object in environ['storm.store']. Each thread contains own store.
    """
    
    def __init__(self, app, database, key = 'storm.store'):
        """Create WSGI middleware.
        @param app: top level application or middleware.
        @param database: instance of Database returned create_database.
        @param key: environ[key] has Store instance. by default 'storm.store'
        """
        assert isinstance(database, Database), \
            'database must be subclass of storm.database.Database'
        self._key = key
        self._database = database
        self._app = app
        self._local = local()
    
    def __call__(self, environ, start_response):
        try:
            environ[self._key]  = self._local.store
        except AttributeError:
            environ[self._key]  = \
                self._local.__dict__.setdefault('store', Store(self._database))
        try:
            return self._app(environ, start_response)
        finally:
            environ[self._key].rollback()    

def decorator(database, key = 'storm.store'):
    """WSGI middleware decorator.
    Example:
    
    @middlestorm.decorator(create_database('dburi://'))
    def app(environ, start_response):
        store = environ['storm.store']
        ....
    """
    def func(app):
        wsgi = MiddleStorm(app, database, key)
        @wraps(app)
        def proxy(*args, **kwargs):
            return wsgi(*args, **kwargs)
        return proxy
    return func

def make_middleware(app,
                    global_conf,
                    db_uri,
                    key = 'storm.store'
                    ):
    """ Paste filter-app converter """
    database = create_database(db_uri)
    return MiddleStorm(app, database, key)
