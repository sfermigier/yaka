from nose.tools import eq_
from base import IntegrationTestCase

from yaka_crm.entities import Account
from yaka_crm.services.audit import AuditEntry


class TestAudit(IntegrationTestCase):

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
