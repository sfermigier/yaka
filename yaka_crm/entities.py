from datetime import datetime

import json

from sqlalchemy.ext.declarative import AbstractConcreteBase, declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer, UnicodeText, DateTime, LargeBinary

from . import db

# TODO: get rid of flask-sqlalchemy, replace db.Model by Base
#Base = declarative_base()


#
# Base classes
#
class Entity(AbstractConcreteBase, db.Model):
  uid = Column(Integer, primary_key=True)

  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(DateTime, default=datetime.utcnow)
  deleted_at = Column(DateTime, default=datetime.utcnow)


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

#
# Domain classes
#

class Account(Entity):

  # ORM stuff
  __tablename__ = 'account'

  name = Column(UnicodeText)
  website = Column(UnicodeText)

  type = Column(UnicodeText)
  industry = Column(UnicodeText)

  # More stuff
  __searchable__ = ['website']
  __editable__ = ['name', 'website']

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

  #__searchable__ = ['first_name', 'last_name', 'job_title', 'department']
  __editable__ = ['first_name', 'last_name', 'job_title', 'department', 'email']

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

  __editable__ = ['first_name', 'last_name', 'job_title', 'department', 'email']

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

  __editable__ = ['first_name', 'last_name', 'job_title', 'department', 'email']

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
  __editable__ = ['first_name', 'last_name', 'job_title', 'email']

  @property
  def name(self):
    return self.first_name + " " + self.last_name

# TODO: Address
# TODO: Task
