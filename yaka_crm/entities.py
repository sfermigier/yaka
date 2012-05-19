"""Entity objects for the CRM applications.

"""

from .core.entities import *

from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, UnicodeText, LargeBinary, Date, Text


searchable = dict(searchable=True)

#
# Mixins
#
class Person(object):
  """Mixin class for persons."""

  salutation = Column(UnicodeText, default=u"")
  first_name = Column(UnicodeText, default=u"", info=searchable)
  last_name = Column(UnicodeText, default=u"", info=searchable)

  job_title = Column(UnicodeText, default=u"", info=searchable)
  department = Column(UnicodeText, default=u"", info=searchable)

  email = Column(UnicodeText, default=u"")
  phone = Column(UnicodeText, default=u"")

  description = Column(UnicodeText, default=u"", info=searchable)

  photo = Column(LargeBinary)

  @property
  def name(self):
    return "%s %s" % (self.first_name, self.last_name)


class Addressable(object):
  """Mixin class for entities with an address."""

  address_street = Column(UnicodeText, default=u"")
  address_city = Column(UnicodeText, default=u"")
  address_state = Column(UnicodeText, default=u"")
  address_country = Column(UnicodeText, default=u"")

  @property
  def address(self):
    if self.address_city or self.address_country or self.address_state or self.address_street:
      return "%s, %s, %s, %s" % (
        self.address_street, self.address_city, self.address_state, self.address_country)
    else:
      return ""


#
# Domain classes
#

class Account(Addressable, Entity):
  __tablename__ = 'account'

  name = Column(UnicodeText, default=u"", info=searchable)
  website = Column(Text, default=u"")
  office_phone = Column(UnicodeText, default=u"")

  type = Column(UnicodeText, default=u"")
  industry = Column(UnicodeText, default=u"")

  logo = Column(LargeBinary)

  contacts = relationship("Contact", backref='account')
  opportunities = relationship("Opportunity", backref='account')


  def __unicode__(self):
    return self.name


class Contact(Addressable, Person, Entity):
  __tablename__ = 'contact'

  account_id = Column(Integer, ForeignKey(Account.uid), nullable=True)


class Opportunity(Entity):
  __tablename__ = 'opportunity'

  name = Column(UnicodeText, nullable=False, info=searchable)
  description = Column(UnicodeText, default=u"", info=searchable)

  type = Column(UnicodeText, default=u"")
  stage = Column(UnicodeText, default=u"")
  amount = Column(Integer)
  probability = Column(Integer)
  close_date = Column(Date)

  account_id = Column(Integer, ForeignKey(Account.uid), nullable=False)


class Lead(Addressable, Person, Entity):
  __tablename__ = 'lead'

  account_name = Column(UnicodeText, default=u"")
  lead_status = Column(UnicodeText, default=u"")


class Document(Entity):
  __tablename__ = 'document'

  blob = Column(LargeBinary)


class User(Person, Entity):
  __tablename__ = 'user'

  password = Column(UnicodeText, nullable=False)

  def __unicode__(self):
    return self.name

  # Should entities know about their own URL? I guess yes.
  @property
  def _url(self):
    return "/users/%d" % self.uid


# TODO: Task
# TODO: Activity
