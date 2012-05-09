from .core.entities import *

from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, UnicodeText, LargeBinary, Date

#
# Mixins
#
class Person(object):
  """Mixin class for persons."""

  salutation = Column(UnicodeText)
  first_name = Column(UnicodeText, searchable=True)
  last_name = Column(UnicodeText, searchable=True)

  job_title = Column(UnicodeText, searchable=True)
  department = Column(UnicodeText, searchable=True)

  email = Column(UnicodeText)
  description = Column(UnicodeText, searchable=True)

  photo = Column(LargeBinary)

  @property
  def name(self):
    return self.first_name + " " + self.last_name


class Addressable(object):
  """Mixin class for entities with an address."""

  address_street = Column(UnicodeText)
  address_city = Column(UnicodeText)
  address_state = Column(UnicodeText)
  address_country = Column(UnicodeText)

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

  name = Column(UnicodeText, searchable=True)
  website = Column(UnicodeText)
  office_phone = Column(UnicodeText)

  type = Column(UnicodeText)
  industry = Column(UnicodeText)

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

  name = Column(UnicodeText, searchable=True)
  description = Column(UnicodeText, searchable=True)
  type = Column(UnicodeText)
  stage = Column(UnicodeText)
  amount = Column(Integer)
  probability = Column(Integer)
  close_date = Column(Date)

  account_id = Column(Integer, ForeignKey(Account.uid), nullable=False)


class Lead(Addressable, Person, Entity):
  __tablename__ = 'lead'

  account_name = Column(UnicodeText)
  lead_status = Column(UnicodeText)


class Document(Entity):
  __tablename__ = 'document'

  blob = Column(LargeBinary)


class User(Person, Entity):
  __tablename__ = 'user'

  password = Column(UnicodeText, nullable=False)


# TODO: Task
