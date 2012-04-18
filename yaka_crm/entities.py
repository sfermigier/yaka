from datetime import datetime

import json

from sqlalchemy.ext.declarative import AbstractConcreteBase, declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer, UnicodeText, DateTime, LargeBinary
from sqlalchemy import event

from .extensions import db

# TODO: get rid of flask-sqlalchemy, replace db.Model by Base
#Base = declarative_base()


#
# Base Entity classes (TODO: move to framework)
#
def meta(column, searchable=False, editable=True):
  """Utility function to add additional metadata to SQLAlchemy columns."""

  class Meta(object):
    pass

  m = column.__yaka_meta__ = Meta()
  m.searchable = searchable
  m.editable = editable


class Entity(AbstractConcreteBase, db.Model):
  """Base class for Yaka entities."""

  uid = Column(Integer, primary_key=True)

  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(DateTime, default=datetime.utcnow)
  deleted_at = Column(DateTime, default=datetime.utcnow)

  meta(created_at, editable=False),
  meta(updated_at, editable=False),
  meta(deleted_at, editable=False),


  def __init__(self, **kw):
    self.update(kw)

  @property
  def column_names(self):
    return [ col.name for col in class_mapper(self.__class__).mapped_table.c ]

  def update(self, d):
    for k, v in d.items():
      assert k in self.column_names, "%s not allowed" % k
      if type(v) == type(""):
        v = unicode(v)
      setattr(self, k, v)

  def to_dict(self):
    if hasattr(self, "__exportable__"):
      exported = self.__exportable__
    else:
      exported = self.column_names
    d = {}
    for k in exported:
      v = getattr(self, k)
      if type(v) == datetime:
        v = v.isoformat()
      d[k] = v
    return d

  def to_json(self):
    return json.dumps(self.to_dict())


def register_meta(cls):
  cls.__editable__ = set()
  cls.__searchable__ = set()

  for name in dir(cls):
    value = getattr(cls, name)
    if not hasattr(value, '__yaka_meta__'):
      continue
    meta = value.__yaka_meta__
    if meta.editable:
      cls.__editable__.add(name)
    if meta.searchable:
      cls.__searchable__.add(name)


event.listen(Entity, 'class_instrument', register_meta)

#
# Domain classes
#
class Account(Entity):

  # ORM
  __tablename__ = 'account'

  name = Column(UnicodeText)
  website = Column(UnicodeText)
  office_phone = Column(UnicodeText)

  type = Column(UnicodeText)
  industry = Column(UnicodeText)

  contacts = relationship("Contact", backref='account')

  # Additional metadata
  meta(name, searchable=True)
  meta(website)
  meta(office_phone)
  meta(type)
  meta(industry)


  @property
  def display_name(self):
    return self.name


class Person(object):
  """Mixin class for persons."""

  first_name = Column(UnicodeText)
  last_name = Column(UnicodeText)

  job_title = Column(UnicodeText)
  department = Column(UnicodeText)

  email = Column(UnicodeText)
  description = Column(UnicodeText)

  # Meta
  meta(first_name, searchable=True)
  meta(last_name, searchable=True)
  meta(job_title, searchable=True)
  meta(department, searchable=True)

  @property
  def full_name(self):
    return self.first_name + " " + self.last_name

  @property
  def display_name(self):
    return self.full_name


class Contact(Person, Entity):
  __tablename__ = 'contact'

  account_id = Column(Integer, ForeignKey(Account.uid), nullable=False)


class Lead(Person, Entity):
  __tablename__ = 'lead'


class Opportunity(Entity):
  # ORM
  __tablename__ = 'opportunity'

  name = Column(UnicodeText)

  account_id = Column(Integer, ForeignKey(Account.uid), nullable=False)


class User(Person, Entity):
  __tablename__ = 'user'

  password = Column(UnicodeText)


# TODO: Address
# TODO: Task
