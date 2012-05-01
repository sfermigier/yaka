from flaskext.testing import TestCase

from yaka_crm import app, db
from config import TestConfig

import yaka_crm.views # Don't remove

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

  def assert_302(self, response):
    self.assertStatus(response, 302)


  def test_home(self):
    response = self.client.get("/")
    self.assert_200(response)

  def test_admin(self):
    response = self.client.get("/admin/")
    self.assert_200(response)

  def test_accounts(self):
    response = self.client.get("/crm/accounts/")
    self.assert_200(response)

    response = self.client.get("/crm/accounts/1")
    self.assert_200(response)

    response = self.client.get("/crm/accounts/1/edit")
    self.assert_200(response)

    form_data = {'name': "some other name"}
    response = self.client.post("/crm/accounts/1/edit", data=form_data)
    #self.assert_302(response)
    #self.assertEquals('http://localhost/crm/accounts/1', response.location)
    #response = self.client.get("/crm/accounts/1")
    self.assert_("some other name" in response.data)

  def test_contacts(self):
    response = self.client.get("/crm/contacts/")
    self.assert_200(response)

    response = self.client.get("/crm/contacts/1")
    self.assert_200(response)

    response = self.client.get("/crm/contacts/1/edit")
    self.assert_200(response)

  def test_leads(self):
    response = self.client.get("/crm/leads/")
    self.assert_200(response)

  def test_opportunities(self):
    response = self.client.get("/crm/opportunities/")
    self.assert_200(response)

  def test_documents(self):
    response = self.client.get("/crm/documents/")
    self.assert_200(response)

  def test_search(self):
    response = self.client.get("/search?q=john")
    self.assert_200(response)
