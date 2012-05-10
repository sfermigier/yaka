"""Audit Service.

Only subclasses of Entity are auditable, at this point.

TODO: In the future, we may decide to:

- Make Models that have the __auditable__ property (set to True) auditable.
- Make Entities that have the __auditable__ property set to False not auditable.

"""

from datetime import datetime
from flask.globals import g
from sqlalchemy import event

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, UnicodeText, DateTime, Text
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

  attribute = Column(Text)
  attribute_type = Column(Text)
  old_value = Column(UnicodeText)
  new_value = Column(UnicodeText)


class AuditService(object):

  def __init__(self, start=False):
    self.active = start
    event.listen(Session, "before_commit", self.before_commit)

  def start(self):
    self.active = True

  def stop(self):
    self.active = False

  def before_commit(self, session):
    if not self.active:
      return

    self.to_update = {}

    for model in session.new:
      self.log_new(session, model)

    for model in session.deleted:
      self.log_deleted(session, model)

    for model in session.dirty:
      self.log_updated(session, model)

  def log_new(self, session, model):
    if not isinstance(model, Entity):
      return
    entry = AuditEntry(type=CREATION)

    entry.entity_id = model.uid
    try:
      user_id = g.user.uid
    except:
      user_id = 0
    entry.user_id = user_id

    session.add(entry)

  def log_deleted(self, session, model):
    if not isinstance(model, Entity):
      return
    entry = AuditEntry(type=DELETION)

    entry.entity_id = model.uid
    try:
      user_id = g.user.uid
    except:
      user_id = 0
    entry.user_id = user_id

    session.add(entry)

  def log_updated(self, session, model):
    if not isinstance(model, Entity):
      return
    entry = AuditEntry(type=UPDATE)

    entry.entity_id = model.uid
    try:
      user_id = g.user.uid
    except:
      user_id = 0
    entry.user_id = user_id

    session.add(entry)
