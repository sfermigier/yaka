"""Audit Service.

Only subclasses of Entity are auditable, at this point.

TODO: In the future, we may decide to:

- Make Models that have the __auditable__ property (set to True) auditable.
- Make Entities that have the __auditable__ property set to False not auditable.

"""

from datetime import datetime
from flask.globals import g
from sqlalchemy import event
from sqlalchemy.orm.events import InstrumentationEvents

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, UnicodeText, DateTime, Text, LargeBinary
from sqlalchemy.orm.session import Session

from .extensions import db
from yaka_crm.core.entities import Entity

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

  attribute_name = Column(Text)
  attribute_type = Column(Text)
  old_value = Column(UnicodeText)
  new_value = Column(UnicodeText)

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


class AuditService(object):

  def __init__(self, start=False):
    self.all_model_classes = set()
    self.active = start

    event.listen(Session, "before_commit", self.before_commit)
    #event.listen(InstrumentationEvents, "class_instrument", self.class_instrument)

  def start(self):
    self.active = True

  def stop(self):
    self.active = False

  def class_instrument(self, model_class):
    if not model_class in self.all_model_classes:
      self.all_model_classes.add(model_class)
      if issubclass(model_class, Entity):
        self.register_class(model_class)

  def register_class(self, entity_class):
    print "Audit registering class", entity_class, "with attrs", entity_class.__auditable__
    for attr_name in entity_class.__auditable__:
      event.listen(getattr(entity_class, attr_name), "set", self.set_attribute)

  def set_attribute(self, model, value, oldvalue, initiator):
    entry = AuditEntry.from_model(model, UPDATE)
    entry.attribute_name = initiator.key
    entry.old_value = str(oldvalue)
    entry.new_value = str(value)

    if not hasattr(model, "__audit__"):
      model.__audit__ = []
    model.__audit__.append(entry)

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
    session.add(entry)

  def log_deleted(self, session, model):
    if not isinstance(model, Entity):
      return

    entry = AuditEntry.from_model(model, type=DELETION)
    session.add(entry)

  def log_updated(self, session, model):
    if not isinstance(model, Entity):
      return
    if not hasattr(model, '__audit__'):
      return
    for entry in model.__audit__:
      session.add(entry)
    del model.__audit__
