from datetime import datetime
from threading import Lock

from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, DateTime
from sqlalchemy import event

from ..extensions import db

__all__ = ['Column', 'Entity']


# TODO: get rid of flask-sqlalchemy, replace db.Model by Base
#Base = declarative_base()


class IdGenerator(object):
  """Dummy integer id generator."""

  # TODO: one counter and one lock per class ?

  def __init__(self):
    self.lock = Lock()
    self.current = 0

  def new(self):
    with self.lock:
      self.current += 1
    return self.current


class Entity(AbstractConcreteBase, db.Model):
  """Base class for Yaka entities."""

  base_url = None

  uid = Column(Integer, primary_key=True,
               info=dict(editable=False, auditable=False))

  created_at = Column(DateTime, default=datetime.utcnow,
                      info=dict(editable=False, auditable=False))
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                      info=dict(editable=False, auditable=False))
  deleted_at = Column(DateTime, default=None,
                      info=dict(editable=False, auditable=False))

  creator_id = Column(Integer, info=dict(editable=False, auditable=False))

  owner_id = Column(Integer)

  # Should not be necessary
  __editable__ = set()
  __searchable__ = set()
  __auditable__ = set()

  id_gen = IdGenerator()

  def __init__(self, **kw):
    self.uid = self.id_gen.new()
    self.update(kw)

  def __repr__(self):
    if hasattr(self, 'name'):
      name = self.name
    else:
      name = "with id=%s" % self.uid
    return "<%s %s>" % (self.__class__.__name__, name)

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


# TODO: make this unecessary
def register_metadata(cls):
  #print "register_metadata called for class", cls
  cls.__editable__ = set()
  cls.__searchable__ = set()
  cls.__auditable__ = set()

  if hasattr(cls, '__table__'):
    columns = cls.__table__.columns
  else:
    columns = [ v for k, v in vars(cls).items() if isinstance(v, Column) ]

  for column in columns:
    name = column.name
    info = column.info

    if info.get("editable", True):
      cls.__editable__.add(name)
    if info.get('searchable', False):
      cls.__searchable__.add(name)
    if info.get('auditable', True):
      cls.__auditable__.add(name)


event.listen(Entity, 'class_instrument', register_metadata)
