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

wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
from authprojectname import model as model
model.connect()

class TestModel(TestCase):
    def setUp(self):
        model.resync()
        model.create_all()
    def tearDown(self):
        model.drop_all()

class TestController(TestModel):
    def __init__(self, *args):
        self.app = paste.fixture.TestApp(wsgiapp)
        self.app.extra_environ['REMOTE_HOST'] = '127.0.0.1'
        TestModel.__init__(self, *args)
    def set_remote_user(self, user):
        self.app.extra_environ['REMOTE_USER'] = str(user.id)

__all__ = ['url_for', 'TestController', 'TestModel', 'model']
