from datetime import datetime

import json

from sqlalchemy.ext.declarative import AbstractConcreteBase, declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer, UnicodeText, DateTime, LargeBinary
from sqlalchemy import event

from . import db

# TODO: get rid of flask-sqlalchemy, replace db.Model by Base
#Base = declarative_base()


#
# Base classes (TODO: move to framework)
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

  def column_names(self):
    return [ col.name for col in class_mapper(self.__class__).mapped_table.c ]

  def update(self, d):
    for k, v in d.items():
      assert k in self.column_names(), "%s not allowed" % k
      if type(v) == type(""):
        v = unicode(v)
      setattr(self, k, v)

  def to_dict(self):
    if hasattr(self, "__exportable__"):
      exported = self.__exportable__
    else:
      exported = self.column_names()
    d = {}
    for k in exported:
      v = getattr(self, k)
      if type(v) == datetime:
        v = v.isoformat()
      d[k] = v
    return d

  def to_json(self):
    return json.dumps(self.to_dict())


class Panel(object):
  def __init__(self, label=None, *rows):
    self.label = label
    self.rows = rows

class Row(object):
  def __init__(self, *cols):
    self.cols = cols


def register_meta(cls):
  cls.__editable__ = set()
  cls.__searchable__ = set()

  for name, value in vars(cls).items():
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

  __tablename__ = 'account'

  name = Column(UnicodeText)
  website = Column(UnicodeText)

  type = Column(UnicodeText)
  industry = Column(UnicodeText)

  # Additional metadata
  meta(name, searchable=True)
  meta(website)
  meta(type)
  meta(industry)

  # More stuff
  __list_view__ = ['name', 'website']

  __view__ = [
    Panel('Overview',
      Row('name', 'website')),
    Panel('More information',
      Row('type', 'industry'))
  ]


class Contact(Entity):
  __tablename__ = 'contact'

  first_name = Column(UnicodeText)
  last_name = Column(UnicodeText)

  job_title = Column(UnicodeText)
  department = Column(UnicodeText)

  email = Column(UnicodeText)

  # Meta
  meta(first_name, searchable=True)
  meta(last_name, searchable=True)
  meta(job_title, searchable=True)
  meta(department, searchable=True)

  # Views
  __list_view__ = ['name', 'job_title', 'department', 'email']
  __view__ = [
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email'))
  ]

  @property
  def name(self):
    return self.first_name + " " + self.last_name


class Lead(Entity):
  __tablename__ = 'lead'

  first_name = Column(UnicodeText)
  last_name = Column(UnicodeText)

  job_title = Column(UnicodeText)
  department = Column(UnicodeText)

  email = Column(UnicodeText)

  #__editable__ = ['first_name', 'last_name', 'job_title', 'department', 'email']

  __list_view__ = ['name', 'job_title', 'department', 'email']
  __view__ = [
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email'))
  ]


class Opportunity(Entity):
  __tablename__ = 'opportunity'

  first_name = Column(UnicodeText)
  last_name = Column(UnicodeText)

  job_title = Column(UnicodeText)
  department = Column(UnicodeText)

  email = Column(UnicodeText)

  #__editable__ = ['first_name', 'last_name', 'job_title', 'department', 'email']

  __list_view__ = ['name', 'job_title', 'department', 'email']
  __view__ = [
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email'))
  ]


class User(Entity):
  __tablename__ = 'user'

  first_name = Column(UnicodeText)
  last_name = Column(UnicodeText)

  job_title = Column(UnicodeText)

  email = Column(UnicodeText)
  password = Column(UnicodeText)

  #__searchable__ = ['first_name', 'last_name', 'job_title']
  #__editable__ = ['first_name', 'last_name', 'job_title', 'email']

  @property
  def name(self):
    return self.first_name + " " + self.last_name

# TODO: Address
# TODO: Task
