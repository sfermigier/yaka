import re

from flaskext.testing import TestCase
from nose.tools import eq_
from tests.util import init_data

from yaka_crm import app, db

from config import TestConfig

from yaka_crm import views # Don't remove


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


  def test_home(self):
    response = self.client.get("/")
    self.assert_200(response)

  def test_admin(self):
    response = self.client.get("/admin/")
    self.assert_200(response)

  def test_accounts(self):
    response = self.client.get("/crm/accounts/")
    self.assert_200(response)

  def test_search(self):
    response = self.client.get("/search/?q=john")
    self.assert_200(response)


  # Test additional blueprints (TODO: move to a distinct test case).
  def test_users(self):
    response = self.client.get("/users/")
    self.assert_200(response)

    m = re.search("/users/([0-9]+)", response.data)
    uid = int(m.group(1))

    response = self.client.get("/users/%d" % uid)
    self.assert_200(response)

    response = self.client.get("/users/%d/mugshot" % uid)
    self.assert_200(response)
    eq_("image/jpeg", response.headers["content-type"])

    response = self.client.get("/users/%d/mugshot?s=55" % uid)
    self.assert_200(response)
    eq_("image/jpeg", response.headers["content-type"])

    response = self.client.get("/users/%d/mugshot?s=48" % uid)
    self.assert_200(response)
    eq_("image/jpeg", response.headers["content-type"])


  def test_reports(self):
    response = self.client.get("/reports/")
    self.assert_200(response)

  # Util
  @staticmethod
  def uid_from_url(url):
    return int(url[len("http://localhost/users/"):])



