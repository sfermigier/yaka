"""Audit Service.

Only subclasses of Entity are auditable, at this point.

TODO: In the future, we may decide to:

- Make Models that have the __auditable__ property (set to True) auditable.
- Make Entities that have the __auditable__ property set to False not auditable.

"""

from datetime import datetime
import json
from flask import g

from sqlalchemy import event
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import NO_VALUE
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, DateTime, Text

from ..core.subjects import User
from ..core.entities import Entity, all_entity_classes

from ..extensions import db


CREATION = 0
UPDATE   = 1
DELETION = 2


class AuditEntry(db.Model):
  """Logs modifications to auditable classes."""

  __tablename__ = 'audit_entry'

  uid = Column(Integer, primary_key=True)
  happened_at = Column(DateTime, default=datetime.utcnow)
  type = Column(Integer) # CREATION / UPDATE / DELETION

  entity_id = Column(Integer)
  entity_class = Column(Text)

  user_id = Column(Integer, ForeignKey(User.uid))
  user = relationship(User)

  changes_json = Column(Text, default="{}", nullable=False)


  @staticmethod
  def from_model(model, type):
    try:
      user_id = g.user.uid
    except:
      user_id = 0

    entry = AuditEntry()
    entry.type = type
    entry.entity_id = model.uid
    entry.entity_class = model.__class__.__name__
    entry.user_id = user_id

    return entry

  def __repr__(self):
    return "<AuditEntry uid=%s type=%s user=%s>" % (
      self.uid,
      {CREATION: "CREATION", DELETION: "DELETION", UPDATE: "UPDATE"}[self.type],
      self.user)

  #noinspection PyTypeChecker
  def get_changes(self):
    return json.loads(self.changes_json)

  def set_changes(self, changes):
    self.changes_json = json.dumps(changes)

  changes = property(get_changes, set_changes)

  # FIXME: extremely innefficient
  @property
  def entity(self):
    #noinspection PyTypeChecker
    cls = locals()[self.entity_class]
    return cls.query.get(self.entity_id)


class AuditService(object):

  __instance = None
  running = False

  @classmethod
  def instance(cls, app=None):
    if not cls.__instance:
      cls.__instance = AuditService(app)
    return cls.__instance

  def __init__(self, app=None):
    self.all_model_classes = set()
    if app:
      self.init_app(app)

  def init_app(self, app):
    self.app = app
    event.listen(Session, "before_commit", self.before_commit)

  def start(self):
    assert not self.running
    self.running = True
    self.register_classes()

  def stop(self):
    assert self.running
    self.running = False
    # One can't currently remove these events.
    #event.remove(Session, "before_commit", self.before_commit)

  def register_classes(self):
    for cls in all_entity_classes():
      self.register_class(cls)

  def register_class(self, entity_class):
    if not hasattr(entity_class, "__table__"):
      return
    if entity_class in self.all_model_classes:
      return
    self.all_model_classes.add(entity_class)
    for column in entity_class.__table__.columns:
      name = column.name
      attr = getattr(entity_class, name)

      info = column.info
      if info.get('auditable', True):
        #print "I will now audit attribute %s for class %s" % (name, entity_class)
        event.listen(attr, "set", self.set_attribute)

  def set_attribute(self, entity, new_value, old_value, initiator):
    attr_name = initiator.key
    if old_value == new_value:
      return
    #print "set_atttribute called for", entity, "key", attr_name
    changes = getattr(entity, "__changes__", None)
    if not changes:
      changes = entity.__changes__ = {}
    if changes.has_key(attr_name):
      old_value = changes[attr_name][0]
    if old_value == NO_VALUE:
      old_value = None
    # FIXME: a bit hackish
    try:
      if len(old_value) > 100:
        old_value = "<<large value>>"
      if len(new_value) > 100:
        new_value = "<<large value>>"
    except:
      pass
    changes[attr_name] = (old_value, new_value)

  def before_commit(self, session):
    for model in session.new:
      self.log_new(session, model)

    for model in session.deleted:
      self.log_deleted(session, model)

    for model in session.dirty:
      self.log_updated(session, model)

  def log_new(self, session, model):
    if not isinstance(model, Entity):
      return

    entry = AuditEntry.from_model(model, type=CREATION)
    session.add(entry)

  def log_deleted(self, session, model):
    if not isinstance(model, Entity):
      return

    entry = AuditEntry.from_model(model, type=DELETION)
    #print "logging", entry
    session.add(entry)

  def log_updated(self, session, model):
    if not isinstance(model, Entity):
      return
    if not hasattr(model, '__changes__'):
      return
    entry = AuditEntry.from_model(model, type=UPDATE)
    entry.changes = model.__changes__
    session.add(entry)

    del model.__changes__

  def entries_for(self, entity):
    return AuditEntry.query.filter(AuditEntry.entity_id == entity.uid).all()


def get_service(app=None):
  return AuditService.instance(app)
