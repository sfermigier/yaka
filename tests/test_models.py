from nose.tools import eq_, ok_, raises
from flaskext.testing import TestCase

from yaka_crm import app, db, finish_setup
from yaka_crm.config import TestConfig
from yaka_crm.entities import *

from datetime import datetime, timedelta


class TestModels(TestCase):

  def create_app(self):
    app.config.from_object(TestConfig())
    finish_setup()
    return app

  def setUp(self):
    db.create_all()
    self.session = db.session

  def tearDown(self):
    db.session.remove()
    db.drop_all()


  def check_editable(self, object):
    if hasattr(object, '__editable__'):
      for k in object.__editable__:
        ok_(hasattr(object, k), "Property '%s' of object %s is not editable" % (k, object))


  def test_contact(self):
    contact = Contact(first_name="John", last_name="Test User", email="test@example.com")

    self.check_editable(contact)

    self.session.add(contact)
    self.session.commit()

    ok_(datetime.utcnow() - contact.created_at < timedelta(1))

    table = Contact.list_view([contact])
    name_cell = table[0][0]
    eq_("John Test User", str(name_cell))

    contacts = list(Contact.search_query(u"john").all())
    eq_(1, len(contacts))

  def test_account(self):
    account = Account(name="John SARL")
    self.check_editable(account)

    self.session.add(account)
    self.session.commit()

    ok_(datetime.utcnow() - account.created_at < timedelta(1))

    table = Account.list_view([account])
    eq_("John SARL", str(table[0][0]))
