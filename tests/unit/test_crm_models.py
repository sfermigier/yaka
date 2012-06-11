from unittest import TestCase
from nose.tools import eq_, ok_

from yaka.core.entities import all_entity_classes
from yaka.apps.crm.entities import Lead, Contact, Account, Opportunity


class TestCRMEntities(TestCase):

  # Utility
  def check_editable(self, object):
    if hasattr(object, '__editable__'):
      for k in object.__editable__:
        ok_(hasattr(object, k), "Property '%s' of object %s is not editable" % (k, object))

  # Tests start here
  def test_lead(self):
    lead = Lead(first_name="John", last_name="Test User", email="test@example.com")
    self.check_editable(lead)

    d = lead.to_dict()
    j = lead.to_json()


  def test_account(self):
    account = Account(name="John SARL")
    self.check_editable(account)

    d = account.to_dict()
    j = account.to_json()

  def test_contact(self):
    account = Account(name="John SARL")

    contact = Contact(first_name="John", last_name="Test User", email="test@example.com")
    contact.account = account

    self.check_editable(contact)

    eq_([contact], account.contacts)

    d = contact.to_dict()
    j = contact.to_json()

  def test_opportunity(self):
    account = Account(name="John SARL")
    opty = Opportunity(name="1000 widgets")
    opty.account = account
    self.check_editable(opty)

    d = opty.to_dict()
    j = opty.to_json()

  def test_get_all_entity_classes(self):
    classes = all_entity_classes()
    ok_(Lead in classes)
    ok_(Account in classes)
    ok_(Contact in classes)
    ok_(Opportunity in classes)
