from datetime import datetime

from flask import g

import sqlalchemy
from sqlalchemy.ext.declarative import AbstractConcreteBase, declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, UnicodeText, DateTime, LargeBinary
from sqlalchemy import event

from .extensions import db


# TODO: get rid of flask-sqlalchemy, replace db.Model by Base
#Base = declarative_base()


#
# Base Entity classes (TODO: move to framework)
#
class Column(sqlalchemy.schema.Column):

  def __init__(self, *args, **kwargs):
    class YakaMetadata(object):
      pass

    m = self.__yaka_metadata__ = YakaMetadata()
    m.editable = kwargs.pop('editable', True)
    m.searchable = kwargs.pop('searchable', False)

    sqlalchemy.schema.Column.__init__(self, *args, **kwargs)


class Entity(AbstractConcreteBase, db.Model):
  """Base class for Yaka entities."""

  base_url = None

  uid = Column(Integer, primary_key=True)

  created_at = Column(DateTime, default=datetime.utcnow, editable=False)
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, editable=False)
  deleted_at = Column(DateTime, default=None, editable=False)


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

  @property
  def url(self):
    return "%s/%s" % (self.base_url, self.uid)


def register_metadata(cls):
  cls.__editable__ = set()
  cls.__searchable__ = set()

  for name in dir(cls):
    value = getattr(cls, name)
    metadata = getattr(value, '__yaka_metadata__', None)
    if not metadata:
      continue
    if metadata.editable:
      cls.__editable__.add(name)
    if metadata.searchable:
      cls.__searchable__.add(name)


event.listen(Entity, 'class_instrument', register_metadata)


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

  account_id = Column(Integer, ForeignKey(Account.uid), nullable=False)


class Lead(Person, Entity):
  __tablename__ = 'lead'


class Opportunity(Entity):
  __tablename__ = 'opportunity'

  name = Column(UnicodeText)

  account_id = Column(Integer, ForeignKey(Account.uid), nullable=False)


class User(Person, Entity):
  __tablename__ = 'user'

  password = Column(UnicodeText)


# TODO: Address
# TODO: Task
