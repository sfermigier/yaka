from base import IntegrationTestCase
from nose.tools import eq_, ok_
from yaka_crm.application import init_index_service

from yaka_crm.entities import Contact


class TestSearch(IntegrationTestCase):

  init_data = True
  no_login = True

  def create_app(self):
    app = IntegrationTestCase.create_app(self)
    init_index_service(app)
    return app

  def test_contacts_are_indexed(self):
    contact = Contact(first_name="John", last_name="Test User", email="test@example.com")
    self.session.add(contact)
    self.session.commit()
    contacts = list(Contact.search_query(u"john").all())
    eq_(1, len(contacts))

  def test_search(self):
    response = self.client.get("/search/?q=john")
    self.assert_200(response)

    response = self.client.get("/search/live?q=john")
    self.assert_200(response)

    # Note: there a guy named "Paul Dupont" in the test data
    response = self.client.get("/search/?q=dupont")
    self.assert_200(response)
    ok_("Paul" in response.data)

    response = self.client.get("/search/live?q=dupont")
    self.assert_200(response)
    ok_("Paul" in response.data)
