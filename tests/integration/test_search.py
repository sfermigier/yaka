from base import IntegrationTestCase
from nose.tools import eq_, ok_
from tests.integration.util import DataLoader

from yaka.apps.crm.entities import Contact
from yaka.extensions import db
from yaka.services import indexing


class TestSearch(IntegrationTestCase):

  init_data = True
  no_login = True

  def setUp(self):
    self.index = indexing.get_service()
    self.index.start()
    IntegrationTestCase.setUp(self)

  def tearDown(self):
    IntegrationTestCase.tearDown(self)
    self.index.stop()

  def test_contacts_are_indexed(self):
    contact = Contact(first_name="John", last_name="Test User", email="test@example.com")
    self.session.add(contact)
    self.session.commit()

    # Check 3 different APIs
    search_result = list(Contact.search_query(u"john").all())
    eq_(1, len(search_result))
    eq_(contact, search_result[0])

    search_result = list(Contact.search_query.search(u"john"))
    eq_(1, len(search_result))
    eq_(contact, search_result[0][1])
    eq_(contact.uid, int(search_result[0][0]['uid']))

    search_result = list(self.index.search(u"john"))
    eq_(1, len(search_result))
    eq_(contact, search_result[0][1])
    eq_(contact.uid, int(search_result[0][0]['uid']))

  def test_basic_search(self):
    # Note: there a guy named "Paul Dupont" in the test data
    response = self.client.get("/search/?q=dupont")
    self.assert_200(response)
    ok_("Paul" in response.data)

  def test_live_search(self):
    response = self.client.get("/search/live?q=dupont")
    self.assert_200(response)
    ok_("Paul" in response.data)

  def test_document_search(self):
    loader = DataLoader(db)
    loader.load_users()
    loader.load_files()
    db.session.commit()

    response = self.client.get("/search/docs?q=rammstein")
    self.assert_200(response)
    print response.data
    ok_("Wikipedia" in response.data)
