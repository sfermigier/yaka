from datetime import datetime
from threading import Lock
from flask.globals import g

from sqlalchemy.ext.declarative import AbstractConcreteBase, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, DateTime, UnicodeText
from sqlalchemy import event

from ..extensions import db

__all__ = ['Column', 'Entity']


# TODO: get rid of flask-sqlalchemy, replace db.Model by Base
#Base = declarative_base()


# FIXME: this is completely broken (breaks after a server restart).
class IdGenerator(object):
  """Dummy integer id generator."""

  # TODO: one counter and one lock per class ?

  def __init__(self):
    self.lock = Lock()
    try:
      self.current = int(open("maxid.data").read())
    except:
      self.current = 0

  def new(self):
    with self.lock:
      self.current += 1
      with open("maxid.data", "wc") as fd:
        fd.write(str(self.current))
      print self.current
    return self.current


# Singleton. Yuck :( !
id_gen = IdGenerator()
system = dict(editable=False, auditable=False)


class Entity(AbstractConcreteBase, db.Model):
  """Base class for Yaka entities."""

  base_url = None

  uid = Column(Integer, primary_key=True, info=system)

  created_at = Column(DateTime, default=datetime.utcnow, info=system)
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                      info=system)
  deleted_at = Column(DateTime, default=None, info=system)


  @declared_attr
  def creator_id(self):
    return Column(Integer, info=system)
    #return Column(Integer, ForeignKey("UserBase.id"), info=system)

  @declared_attr
  def owner_id(self):
    return Column(Integer)
    #return Column(Integer, ForeignKey("UserBase.id"))

  # TODO: doesn't work.
  #@declared_attr
  #def creator(self):
  #  return relationship("User")
  #@declared_attr
  #def owner(self):
  #  return relationship("User")

  # FIXME: extremely suboptimal
  @property
  def creator(self):
    from ..entities import User
    return User.query.get(self.creator_id)

  @property
  def owner(self):
    from ..entities import User
    return User.query.get(self.owner_id)

  # Should not be necessary
  __editable__ = set()
  __searchable__ = set()
  __auditable__ = set()

  def __init__(self, **kw):
    self.uid = id_gen.new()
    if hasattr(g, 'user'):
      self.creator_id = self.owner_id = g.user.uid
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

  # TODO: only one of these two
  @property
  def url(self):
    return "%s/%s" % (self.base_url, self.uid)

  @property
  def _url(self):
    return self.base_url + "/%d" % self.uid

  def _icon(self, size=12):
    return "/static/icons/%s-%d.png" % (self.__class__.__name__.lower(), size)


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
