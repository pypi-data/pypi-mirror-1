# -*- coding: utf-8 -*-
#
# The Open Software License 3.0
#
# Copyright (c) 2008 Heikki Toivonen <My first name at heikkitoivonen.net>
#

import unittest, os

from werkzeug import Client, BaseResponse, Headers

from solu.application import Solu
from solu import manage, models, utils


class SoluTest(unittest.TestCase):
    def setUp(self):
        tests_dir = os.path.abspath(os.path.dirname(__file__))
        inifile = os.path.join(tests_dir, 'deploy.ini')
        app = Solu(inifile)
        app.init_database()
        manage.generate_demo_data()
        self.client = Client(app, BaseResponse)
        
    def tearDown(self):
        # XXX how to just delete the db?
        delete = models.resource_table.delete()
        utils.session.execute(delete)
        utils.session.commit()
        
    def test_index(self):
        resp = self.client.get('/')
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers, Headers([('Content-Type', 'text/html; charset=utf-8')]))
        self.assertTrue('Solu: Home' in resp.data)

    def test_search_results(self):
        resp = self.client.get('/search_results')
        self.assertEquals(resp.status_code, 301)

        resp = self.client.get('/search_results/')
        self.assertEquals(resp.status_code, 200)
        
        resp = self.client.get('/search_results/?name=')
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers, Headers([('Content-Type', 'text/html; charset=utf-8')]))
        self.assertTrue('Solu: Search Results' in resp.data)
        self.assertTrue('Grunt Seven' in resp.data)

        resp = self.client.get('/search_results/2/')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Printer 1.2.3.4' in resp.data)
        
        resp = self.client.get('/search_results/3/')
        self.assertEquals(resp.status_code, 404)

    def test_add(self):
        resp = self.client.get('/add')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Solu: Add' in resp.data)

        resp = self.client.post('/add', data={'name': 'Foobar',
                                              'check': '3',
                                              'x': 'not a number',
                                              'y': 'yaha'})
        self.assertEquals(resp.status_code, 400)
        resp = self.client.post('/add', data={'name': 'Foobar',
                                              'check': '3',
                                              'x': '-1',
                                              'y': '100000000000000000000'})
        self.assertEquals(resp.status_code, 400)
        resp = self.client.post('/add', data={'name': 'Foobar',
                                              'check': '2',
                                              'x': '50',
                                              'y': '50'})
        self.assertEquals(resp.status_code, 400)

        resp = self.client.post('/add', data={'name': 'Foobar',
                                              'check': '3',
                                              'x': '101',
                                              'y': '202'})
        self.assertEquals(resp.status_code, 302)
        self.assertTrue('show/15' in resp.data) # XXX can we follow redirect?
        
        resp = self.client.get('/show/15')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Solu: Show Foobar' in resp.data)
        self.assertTrue('top: -430' in resp.data)
        self.assertTrue('left: 69' in resp.data)

        # make sure we can deal with apostrophes
        resp = self.client.post('/add', data={'name': "John O'Neill",
                                              'check': '3',
                                              'x': '101',
                                              'y': '202'})
        self.assertEquals(resp.status_code, 302)
        self.assertTrue('show/16' in resp.data) # XXX can we follow redirect?
        resp = self.client.get('/show/16')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue("Solu: Show John O'Neill" in resp.data)

        # and non-ascii
        resp = self.client.post('/add', data={'name': "首页",
                                              'check': '3',
                                              'x': '101',
                                              'y': '202'})
        self.assertEquals(resp.status_code, 302)
        self.assertTrue('show/17' in resp.data) # XXX can we follow redirect?
        resp = self.client.get('/show/17')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue("Solu: Show 首页" in resp.data)

    def test_show(self):
        resp = self.client.get('/show')
        self.assertEquals(resp.status_code, 404)

        resp = self.client.get('/show/1')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Solu: Show John Doe' in resp.data)
        self.assertTrue('top: -532' in resp.data)
        self.assertTrue('left: 68' in resp.data)

    def test_edit(self):
        resp = self.client.get('/edit')
        self.assertEquals(resp.status_code, 404)

        resp = self.client.get('/edit/1')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Solu: Edit John Doe' in resp.data)
        
        resp = self.client.post('/edit/1', data={'name': 'Able Abe',
                                              'check': 'Foo',
                                              'x': '101',
                                              'y': '202'})
        self.assertEquals(resp.status_code, 400)

        resp = self.client.post('/edit/1', data={'name': 'Able Abe',
                                              'check': 'John Doe',
                                              'x': '101',
                                              'y': '202'})
        self.assertEquals(resp.status_code, 302)
        self.assertTrue('show/1' in resp.data) # XXX can we follow redirect?

        resp = self.client.get('/show/1')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Solu: Show Able Abe' in resp.data)

    def test_delete(self):
        resp = self.client.get('/delete')
        self.assertEquals(resp.status_code, 404)

        resp = self.client.get('/delete/1')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Solu: Delete John Doe' in resp.data)
        
        resp = self.client.post('/delete/1', data={'check': 'Foo'})
        self.assertEquals(resp.status_code, 400)

        resp = self.client.post('/delete/1', data={'check': 'John Doe'})
        self.assertEquals(resp.status_code, 302) # XXX can we follow redirect?

        resp = self.client.get('/show/1')
        self.assertEquals(resp.status_code, 404)

    def test_static(self):
        resp = self.client.get('/favicon.ico')
        self.assertEquals(resp.status_code, 200)

        resp = self.client.get('/maps/map.png')
        self.assertEquals(resp.status_code, 200)

        resp = self.client.get('/static/crosshair.png')
        self.assertEquals(resp.status_code, 200)
        