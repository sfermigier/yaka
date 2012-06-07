from unittest import TestCase
from nose.tools import eq_, ok_

from yaka.entities import *


class TestModels(TestCase):

  # Utility
  def check_editable(self, object):
    if hasattr(object, '__editable__'):
      for k in object.__editable__:
        ok_(hasattr(object, k), "Property '%s' of object %s is not editable" % (k, object))

  # Tests start here
  def test_account(self):
    account = Account(name="John SARL")
    self.check_editable(account)

  def test_contact(self):
    contact = Contact(first_name="John", last_name="Test User", email="test@example.com")
    self.check_editable(contact)

    account = Account(name="John SARL")
    contact.account = account
    eq_([contact], account.contacts)

  def test_get_all_entity_classes(self):
    classes = all_entity_classes()
    print classes
    ok_(len(classes) > 4)