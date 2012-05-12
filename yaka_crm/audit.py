"""Audit Service.

Only subclasses of Entity are auditable, at this point.

TODO: In the future, we may decide to:

- Make Models that have the __auditable__ property (set to True) auditable.
- Make Entities that have the __auditable__ property set to False not auditable.

"""

from datetime import datetime
import json
from flask.globals import g
from sqlalchemy import event
from sqlalchemy.orm.attributes import NO_VALUE
from sqlalchemy.orm.events import InstrumentationEvents

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, UnicodeText, DateTime, Text, LargeBinary
from sqlalchemy.orm.session import Session

from .extensions import db
from yaka_crm.core.entities import Entity
from yaka_crm.entities import User

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
  user_id = Column(Integer)
  changes_json = Column(UnicodeText, default="{}", nullable=False)

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
      self.uid, {CREATION: "CREATION", DELETION: "DELETION", UPDATE: "UPDATE"}[self.type],
      User.query.get(self.user_id),
    )

  #noinspection PyTypeChecker
  def get_changes(self):
    return json.loads(self.changes_json)

  def set_changes(self, changes):
    self.changes_json = json.dumps(changes)

  changes = property(get_changes, set_changes)


class AuditService(object):

  def __init__(self, start=False):
    self.all_model_classes = set()
    self.active = start

    # Testing
    event.listen(InstrumentationEvents, "attribute_instrument", self.attribute_instrument)
    event.listen(InstrumentationEvents, "class_instrument", self.class_instrument)

    # We register the events late in the boot process, beacause it doesn't work otherwise
    #event.listen(Session, "after_attach", self.after_attach)
    #event.listen(Session, "after_attach", self.after_attach)

    event.listen(Session, "before_commit", self.before_commit)

  def start(self):
    self.active = True

  def stop(self):
    self.active = False

  def class_instrument(self, cls):
    pass
    #print "class_instrument", cls

  def attribute_instrument(self, cls, key, inst):
    #print "attribute_instrument", cls, key, inst
    if issubclass(cls, Entity):
      self.register_class(cls)

  def after_attach(self, session, model):
    self.register_model(model)

  def register_model(self, model):
    model_class = model.__class__
    if not model_class in self.all_model_classes:
      self.all_model_classes.add(model_class)
      if issubclass(model_class, Entity):
        self.register_class(model_class)

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
    changes[attr_name] = (old_value, new_value)

  def before_commit(self, session):
    if not self.active:
      return

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
    #print "logging", entry
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
    #print "logging", model
    if not hasattr(model, '__changes__'):
      print "model has no __changes__, this might be wrong"
      return
    print "changes:", model.__changes__
    entry = AuditEntry.from_model(model, type=UPDATE)
    entry.changes = model.__changes__
    session.add(entry)

    del model.__changes__
