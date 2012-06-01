from base import IntegrationTestCase
import re

import yaka_crm.views # Don't remove


class TestViews(IntegrationTestCase):

  init_data = True
  no_login = True

  def assert_302(self, response):
    self.assertStatus(response, 302)

  # Tests start here
  def test_home(self):
    response = self.client.get("/crm/")
    self.assert_200(response)

  def test_accounts(self):
    response = self.client.get("/crm/accounts/")
    self.assert_200(response)

    m = re.search("/crm/accounts/([0-9]+)", response.data)
    uid = int(m.group(1))

    response = self.client.get("/crm/accounts/%d" % uid)
    self.assert_200(response)

    response = self.client.get("/crm/accounts/%d/edit" % uid)
    self.assert_200(response)

    form_data = {'name': "some other name"}
    response = self.client.post("/crm/accounts/%d/edit" % uid, data=form_data)
    #self.assert_302(response)
    #self.assertEquals('http://localhost/crm/accounts/1', response.location)
    #response = self.client.get("/crm/accounts/1")
    self.assert_("some other name" in response.data)

  def test_contacts(self):
    response = self.client.get("/crm/contacts/")
    self.assert_200(response)

    m = re.search("/crm/contacts/([0-9]+)", response.data)
    uid = int(m.group(1))

    response = self.client.get("/crm/contacts/%d" % uid)
    self.assert_200(response)

    response = self.client.get("/crm/contacts/%d/edit" % uid)
    self.assert_200(response)

  def test_leads(self):
    response = self.client.get("/crm/leads/")
    self.assert_200(response)

  def test_opportunities(self):
    response = self.client.get("/crm/opportunities/")
    self.assert_200(response)
