# Don't remove
import uuid
import fix_path

from flaskext.testing import TestCase

from yaka_crm import app, db
from config import TestConfig

import os


BASEDIR = os.path.dirname(__file__)

class IntegrationTestCase(TestCase):

  def create_app(self):
    app.config.from_object(TestConfig())
    app.config['WHOOSH_BASE'] = os.path.join(BASEDIR, "whoosh", str(uuid.uuid4()))
    return app

  def setUp(self):
    db.create_all()
    self.session = db.session

  def tearDown(self):
    db.session.remove()
    db.drop_all()

  def assert_302(self, response):
    self.assertStatus(response, 302)
