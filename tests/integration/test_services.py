from nose.tools import eq_
from base import IntegrationTestCase

from yaka.apps.crm.entities import Account
from yaka.services.audit import AuditEntry, AuditService


class TestAudit(IntegrationTestCase):

  def setUp(self):
    AuditService.instance().start()
    IntegrationTestCase.setUp(self)

  def tearDown(self):
    IntegrationTestCase.tearDown(self)
    AuditService.instance().stop()

  def test_audit(self):
    eq_(0, len(AuditEntry.query.all()))

    account = Account(name="John SARL")
    self.session.add(account)
    self.session.commit()

    eq_(1, len(AuditEntry.query.all()))

    account.address_country = u"FR"
    self.session.commit()

    eq_(2, len(AuditEntry.query.all()))

    self.session.delete(account)
    self.session.commit()

    eq_(3, len(AuditEntry.query.all()))

  def test_audit_bis(self):
    eq_(0, len(AuditEntry.query.all()))

    account = Account(name="John SARL")
    self.session.add(account)
    self.session.commit()

    eq_(1, len(AuditEntry.query.all()))

    account.address_country = u"FR"
    self.session.commit()

    eq_(2, len(AuditEntry.query.all()))

    self.session.delete(account)
    self.session.commit()

    eq_(3, len(AuditEntry.query.all()))
