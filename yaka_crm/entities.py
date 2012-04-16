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

  def single_view(self):
    return self.__single_viewer__.view(self)

  @classmethod
  def list_view(cls, entities):
    return cls.__list_viewer__.view(entities)


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
# View classes
#
class Table(object):
  def __init__(self, viewer, entities):
    self.viewer = viewer
    self.entities = entities

  @property
  def column_names(self):
    return self.viewer.column_names

  def __getitem__(self, item):
    return Line(self.viewer, self.entities[item])


class Line(object):
  def __init__(self, viewer, entity):
    self.viewer = viewer
    self.entity = entity

  @property
  def uid(self):
    return self.entity.uid

  @property
  def column_names(self):
    return self.viewer.column_names

  def __getitem__(self, item):
    if type(item) == int:
      if item >= len(self.column_names):
        raise IndexError
      name = self.column_names[item]
      return Cell(self.viewer, name, getattr(self.entity, name))
    else:
      cells = []
      for i in range(*item.indices(len(self.column_names))):
        name = self.column_names[i]
        cells += [Cell(self.viewer, name, getattr(self.entity, name))]
        print cells
      return cells


class Cell(object):
  def __init__(self, viewer, name, value):
    self.viewer = viewer
    self.name = name
    self.value = value

  def __str__(self):
    return str(self.value)


class ListViewer(object):

  _column_names = None

  def __init__(self, *columns):
    self.columns = columns

  @property
  def column_names(self):
    if not self._column_names:
      column_names = []
      for c in self.columns:
        if type(c) == str:
          column_names += [c]
        else:
          column_names += [c.name]
      self._column_names = column_names
    return self._column_names

  def view(self, entities):
    return Table(self, entities)


class SingleView(object):
  def __init__(self, viewer, entity):
    self.viewer = viewer
    self.entity = entity

  @property
  def panels(self):
    return self.viewer.panels

  def get(self, panel, row=None, col=None):
    panel_index = self.viewer.panels.index(panel)
    panel = self.viewer.panels[panel_index]

    if row is None:
      return panel

    row_index = panel.rows.index(row)
    row = panel.rows[row_index]

    if col is None:
      return row

    attr_name = row.cols[col]
    return getattr(self.entity, attr_name)


class SingleViewer(object):
  def __init__(self, *panels):
    self.panels = panels

  def view(self, entity):
    return SingleView(self, entity)


class Panel(object):
  def __init__(self, label=None, *rows):
    self.label = label
    self.rows = rows

  def __iter__(self):
    return iter(self.rows)

  def __getitem__(self, item):
    return self.rows[item]

  def __len__(self):
    return len(self.rows)


class Row(object):
  def __init__(self, *cols):
    self.cols = cols

  def __iter__(self):
    return iter(self.cols)

  def __getitem__(self, item):
    return self.cols[item]

  def __len__(self):
    return len(self.cols)


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
  __list_viewer__ = ListViewer(name, website, type, industry)

  __single_viewer__ = SingleViewer(
    Panel('Overview',
          Row('name', 'website')),
    Panel('More information',
          Row('type', 'industry')),
  )

class Person(object):
  """Mixin class for persons."""

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

  @property
  def full_name(self):
    return self.first_name + " " + self.last_name


class Contact(Entity, Person):
  __tablename__ = 'contact'

  # Views
  __list_viewer__ = ListViewer('full_name', 'job_title', 'department', 'email')

  __single_viewer__ = SingleViewer(
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email')),
  )


class Lead(Entity, Person):
  __tablename__ = 'lead'

  # Views
  __list_viewer__ = ListViewer('full_name', 'job_title', 'department', 'email')
  __single_viewer__ = SingleViewer(
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email')),
  )


class Opportunity(Entity):
  __tablename__ = 'opportunity'

  name = Column(UnicodeText)

  account_id = Column(Integer, ForeignKey(Account.uid), nullable=False)

  __list_viewer__ = ListViewer('name')

  __single_viewer__ = SingleViewer(
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email')),
  )


class User(Entity, Person):
  __tablename__ = 'user'

  password = Column(UnicodeText)


# TODO: Address
# TODO: Task
