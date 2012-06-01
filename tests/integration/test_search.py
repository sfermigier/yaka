from base import IntegrationTestCase
from nose.tools import eq_, ok_

from yaka_crm.entities import Contact
from yaka_crm.services.indexing import IndexService


class TestSearch(IntegrationTestCase):

  init_data = True
  no_login = True

  def setUp(self):
    IndexService.instance().start()
    IntegrationTestCase.setUp(self)

  def tearDown(self):
    IntegrationTestCase.tearDown(self)
    IndexService.instance().stop()

  def test_contacts_are_indexed(self):
    contact = Contact(first_name="John", last_name="Test User", email="test@example.com")
    self.session.add(contact)
    self.session.commit()
    contacts = list(Contact.search_query(u"john").all())
    eq_(1, len(contacts))

  def test_search(self):
    # Note: there a guy named "Paul Dupont" in the test data
    response = self.client.get("/search/?q=dupont")
    self.assert_200(response)
    ok_("Paul" in response.data)

    response = self.client.get("/search/live?q=dupont")
    self.assert_200(response)
    ok_("Paul" in response.data)
