
# Don't remove
import subprocess

from nose.tools import eq_
from flaskext.testing import TestCase

from yaka_crm import app, db
from yaka_crm import views # Don't remove

from config import TestConfig
from util import init_data


class TestViews(TestCase):

  def create_app(self):
    app.config.from_object(TestConfig())
    return app

  def setUp(self):
    TestCase.setUp(self)
    db.create_all()
    self.session = db.session
    init_data(db)

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    TestCase.tearDown(self)

  def test_login_happy_path(self):
    data = dict(email='sf@example.com', password='admin')
    response = self.client.post("/login", data=data)
    eq_(response.status_code, 302)

  def test_login_wrong_password(self):
    data = dict(email='sf@example.com', password='wrong')
    response = self.client.post("/login", data=data)
    eq_(response.status_code, 401)

  def test_login_wrong_email(self):
    data = dict(email='wrong@example.com', password='wrong')
    response = self.client.post("/login", data=data)
    eq_(response.status_code, 401)
