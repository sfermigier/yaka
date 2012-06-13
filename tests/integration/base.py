# Don't remove
import fix_path

from flaskext.testing import TestCase
from tests.integration import util

from yaka.application import Application
from yaka.extensions import db

from .config import TestConfig

import os
import uuid


BASEDIR = os.path.dirname(__file__)

class IntegrationTestCase(TestCase):

  init_data = False
  no_login = False

  def create_app(self):
    config = TestConfig()
    config.WHOOSH_BASE = os.path.join(BASEDIR, "whoosh", str(uuid.uuid4()))
    config.NO_LOGIN = self.no_login
    self.app = Application(config)

    return self.app

  def setUp(self):
    db.create_all()
    self.session = db.session
    if self.init_data:
      util.init_data(db)

  def tearDown(self):
    db.session.remove()
    db.drop_all()

  def assert_302(self, response):
    self.assert_status(response, 302)

  def assert_204(self, response):
    self.assert_status(response, 204)
