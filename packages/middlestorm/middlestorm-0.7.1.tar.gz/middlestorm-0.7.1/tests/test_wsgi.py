#!/usr/bin/env python
# vim:ts=4:sw=4:et

from storm.store import Store
from storm.database import create_database
from storm.properties import Int
from unittest import TestCase
from threading import Thread

import middlestorm

def threaded(func):
    """threaded decorator"""
    def proxy(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return proxy

fake_db = create_database('sqlite:///:memory:')

class TestWsgi(TestCase):
    
    def test_environ(self):
        """Put Store instance in environ dict"""
        
        def fake_app(environ, start_response):
            self.assertTrue(environ.has_key('storm.store'))
            self.assertEquals(environ['storm.store'].__class__, Store)
        
        m = middlestorm.MiddleStorm(fake_app, fake_db)
        
        e = {}
        m(e, None)
    
    def test_decorator(self):
        """Decorator put Store instance in environ dict"""
        
        @middlestorm.decorator(fake_db)
        def fake_app(environ, start_response):
            self.assertTrue(environ.has_key('storm.store'))
            self.assertEquals(environ['storm.store'].__class__, Store)
        
        e = {}
        fake_app(e, None)
    
    def test_paste_config_default(self):
        """Put Store instance in environ dict"""
        
        def fake_app(environ, start_response):
            self.assertTrue(environ.has_key('storm.store'))
            self.assertEquals(environ['storm.store'].__class__, Store)
        
        m = middlestorm.make_middleware(fake_app, {},
                                        db_uri='sqlite:///:memory:')
        
        e = {}
        m(e, None)
    
    def test_custom_key(self):
        """Decorator put Store instance in environ dict as custom key"""
        
        @middlestorm.decorator(fake_db, 'custom.key_test')
        def fake_app(environ, start_response):
            self.assertTrue(environ.has_key('custom.key_test'))
            self.assertEquals(environ['custom.key_test'].__class__, Store)
        
        e = {}
        fake_app(e, None)
    
    def test_paste_config_default_custom_key(self):
        """Put Store instance in environ dict"""
        
        def fake_app(environ, start_response):
            self.assertTrue(environ.has_key('custom.key_test'))
            self.assertEquals(environ['custom.key_test'].__class__, Store)
        
        m = middlestorm.make_middleware(fake_app, {},
                                        db_uri='sqlite:///:memory:',
                                        key='custom.key_test')
        
        e = {}
        m(e, None)
    
    def test_cache_store(self):
        """single thread already get single Store instance"""
        stores = []
        
        def fake_app(environ, start_response):
            stores.append(environ['storm.store'])
        
        m = middlestorm.MiddleStorm(fake_app, fake_db)
        
        e = {}
        m(e, None)
        e = {}
        m(e, None)
        
        self.assertEquals(stores[0], stores[1])
    
    def test_thread_store(self):
        """each thread have self Store instance"""
        stores = []
        
        def fake_app(environ, start_response):
            stores.append(environ['storm.store'])
        
        m = middlestorm.MiddleStorm(fake_app, fake_db)
        
        @threaded
        def mt():
            e = {}
            m(e, None)
        
        mt().join()
        mt().join()
        
        self.assertNotEquals(stores[0], stores[1])

	def test_clear_store(self):
		class FakeTable(object):
			__storm_table__ = 'fake_table'
			id = Int(primary = True)
		
		ft = FakeTable()
		
		def fake_app(environ, start_response):
			assert environ['storm.store'].of(ft) == None, 'not clean store after call app'
			environ['storm.store'].add(ft)
		
		m = middlestorm.MiddleStorm(fake_app, fake_db)

		e = {}
		m(e, None)
		e = {}
		m(e, None)
