import os
import sys
from unittest import TestCase

here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

sys.path.insert(0, conf_dir)

import pkg_resources

pkg_resources.working_set.add_entry(conf_dir)

pkg_resources.require('Paste')
pkg_resources.require('PasteScript')

from paste.deploy import loadapp
import paste.fixture
import paste.script.appinstall

from authprojectname.config.routing import *
from routes import request_config, url_for

test_file = os.path.join(conf_dir, 'test.ini')
cmd = paste.script.appinstall.SetupCommand('setup-app')
cmd.run([test_file])

from authprojectname.lib import fixtures

wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
from authprojectname import model as model
model.connect()

class TestModel(TestCase):
    __fixtures__ = {}
    
    def setUp(self):
        model.resync()
        model.create_all()
        self.fixtures = {}
        for fixture, klass in self.__fixtures__.iteritems():
            self.fixtures[fixture]=self.loadData(klass)

    def tearDown(self):
        model.drop_all()

    def loadData(self, klass, filename=None):
        return fixtures.load_data(klass, filename, base_dir=here_dir)

class TestController(TestModel):
    def __init__(self, *args):
        self.app = paste.fixture.TestApp(wsgiapp)
        TestModel.__init__(self, *args)
    def login_user(self, username, password):
        "Logs in user with given username and password, adding that user to session"
        resp = self.app.post(url_for(controller='/login', action='signin'), 
            dict(username=username, password=password)) 
    def tearDown(self):
        TestModel.tearDown(self)
        self.app.reset()

__all__ = ['url_for', 'TestController', 'TestModel', 'model']
