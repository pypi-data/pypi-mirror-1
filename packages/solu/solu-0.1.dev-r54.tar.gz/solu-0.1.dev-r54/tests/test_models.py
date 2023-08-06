#
# The Open Software License 3.0
#
# Copyright (c) 2008 Heikki Toivonen <My first name at heikkitoivonen.net>
#

import unittest, os

from werkzeug import Client, BaseResponse, Headers

from solu.application import Solu
from solu import manage, models, utils


class ModelTest(unittest.TestCase):
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
        
    def test_model(self):
        resources = models.Resource.query.all()
        self.assertEquals(len(resources), 14)

        resource = models.Resource(u'Foo Bar', u'a@example.org', None, 100, 20)
        utils.session.commit()
        resources = models.Resource.query.all()
        self.assertEquals(len(resources), 15)
        self.assertTrue(resource in resources)
        
        resource2 = models.Resource.query.filter(models.Resource.name==u'Foo Bar').one()
        self.assertEquals(resource, resource2)