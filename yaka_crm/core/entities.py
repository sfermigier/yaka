from datetime import datetime
from threading import Lock

import sqlalchemy
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.types import Integer, DateTime
from sqlalchemy import event

from ..extensions import db

__all__ = ['Column', 'Entity', 'all_entity_classes']


# TODO: get rid of flask-sqlalchemy, replace db.Model by Base
#Base = declarative_base()


class IdGenerator(object):
  """Dummy integer id generator."""

  def __init__(self):
    self.lock = Lock()
    self.current = 0

  def new(self):
    with self.lock:
      self.current += 1
    return self.current


id_gen = IdGenerator()


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
    m.auditable = kwargs.pop('auditable', True)

    sqlalchemy.schema.Column.__init__(self, *args, **kwargs)


# Poor man's registry of entity classes.
all_entity_classes = set()


class Entity(AbstractConcreteBase, db.Model):
  """Base class for Yaka entities."""

  base_url = None

  uid = Column(Integer, primary_key=True, auditable=False)

  created_at = Column(DateTime, default=datetime.utcnow,
                      editable=False, auditable=False)
  updated_at = Column(DateTime, default=datetime.utcnow,
                      onupdate=datetime.utcnow, editable=False, auditable=False)
  deleted_at = Column(DateTime, default=None, editable=False, auditable=False)

  creator_id = Column(Integer, auditable=False)
  owner_id = Column(Integer)

  def __init__(self, **kw):
    all_entity_classes.add(self.__class__)
    self.uid = id_gen.new()
    self.update(kw)

  @classmethod
  def collect_metadata(cls):
    print "Registering metadata for class", cls
    cls.__editable__ = set()
    cls.__searchable__ = set()
    cls.__auditable__ = set()

    for name, attr in vars(cls).items():
      metadata = getattr(attr, '__yaka_metadata__', None)
      if not metadata:
        continue
      if metadata.editable:
        cls.__editable__.add(name)
      if metadata.searchable:
        cls.__searchable__.add(name)
      if metadata.auditable:
        cls.__auditable__.add(name)

    print cls.__editable__
    print cls.__searchable__
    print cls.__auditable__
    print

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


# TODO: not sure it really wortks (only called once for Entity class, not for subclasses).
def register_metadata(cls):
  print "Registering metadata for class", cls
  cls.__editable__ = set()
  cls.__searchable__ = set()
  cls.__auditable__ = set()

  for name in dir(cls):
    column = getattr(cls, name)
    metadata = getattr(column, '__yaka_metadata__', None)
    if not metadata:
      continue
    if metadata.editable:
      cls.__editable__.add(name)
    if metadata.searchable:
      cls.__searchable__.add(name)
    if metadata.auditable:
      cls.__auditable__.add(name)


event.listen(Entity, 'class_instrument', register_metadata)
