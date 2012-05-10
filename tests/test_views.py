from flaskext.testing import TestCase

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
    response = self.client.get("/search?q=john")
    self.assert_200(response)
