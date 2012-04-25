from .core.entities import *

from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, UnicodeText, LargeBinary, Date

#
# Domain classes
#
class Account(Entity):
  __tablename__ = 'account'

  name = Column(UnicodeText, searchable=True)
  website = Column(UnicodeText)
  office_phone = Column(UnicodeText)

  type = Column(UnicodeText)
  industry = Column(UnicodeText)

  contacts = relationship("Contact", backref='account')


class Person(object):
  """Mixin class for persons."""

  salutation = Column(UnicodeText)
  first_name = Column(UnicodeText, searchable=True)
  last_name = Column(UnicodeText, searchable=True)

  job_title = Column(UnicodeText, searchable=True)
  department = Column(UnicodeText, searchable=True)

  email = Column(UnicodeText)
  description = Column(UnicodeText, searchable=True)

  @property
  def name(self):
    return self.first_name + " " + self.last_name


class Contact(Person, Entity):
  __tablename__ = 'contact'

  account_id = Column(Integer, ForeignKey(Account.uid), nullable=True)


class Lead(Person, Entity):
  __tablename__ = 'lead'

  lead_status = Column(UnicodeText)


class Opportunity(Entity):
  __tablename__ = 'opportunity'

  name = Column(UnicodeText, searchable=True)
  type = Column(UnicodeText)
  stage = Column(UnicodeText)

  close_date = Column(Date)

  account_id = Column(Integer, ForeignKey(Account.uid), nullable=False)


class Document(Entity):
  __tablename__ = 'document'

  blob = Column(LargeBinary)


class User(Person, Entity):
  __tablename__ = 'user'

  password = Column(UnicodeText)


# TODO: Address
# TODO: Task
