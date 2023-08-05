middlestorm
===========

.. contents:

Introduction
------------

`Storm <https://storm.canonical.com>`_ is a fast, small and powerful object-relational mapper.
Try it to use in web-aware applications.

WSGI application mainly miltithreaded, but Store object is `not thread safe <https://storm.canonical.com/Manual#head-87f6030209535be685673b258a552728a235a594>`_.

MiddleStorm middleware adds a thread safe Store object instance in ``environ`` `dictonary <http://www.python.org/dev/peps/pep-0333/#environ-variables>`_.
Each thread have self Store.

Simple example
--------------

There are 2 ways to create middleware:
 * class
 * decorator

Class middleware::

    from wsgiref.simple_server import make_server
    from storm.database import create_database
    
    from middlestorm import MiddleStorm
    
    def storm_app(environ, start_response):
        store = environ['storm.store']
        # ...
    
    db = create_database('postgres://user:password@host/base')
    app = MiddleStorm(storm_app, db) 
    
    make_server('', 8000, app).serve_forever()

Decorator middleware::

    from wsgiref.simple_server import make_server
    from storm.database import create_database
    
    import middlestorm
    
    @middlestorm.decorator(create_database('postgres://user:password@host/base'))
    def storm_app(environ, start_response):
        store = environ['storm.store']
        # ...
    
    make_server('', 8000, storm_app).serve_forever()

By default Store placed in in variable ``storm.store``. This can be customized::

    app = MiddleStorm(storm_app, db, key='custom.mystore')

or decorator style::

    @middlestorm.decorator(db, key='custom.mystore')
    def storm_app(environ, start_response):
        store = environ['custom.mystore']

Legal
-----

middlestorm is a part of
`storm support tools <http://vsevolod.balashov.name/code/storm/>`_
and distributed under terms of
`GNU LGPL v.2.1 <http://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt>`_.

Copyright 2007 - 2008 `Vsevolod Balashov <http://vsevolod.balashov.name/>`_.
