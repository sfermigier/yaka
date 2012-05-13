"""Activity Service.

See http://activitystrea.ms/specs/json/1.0/
"""

from datetime import datetime
import json
from blinker import signal
from flask.globals import g
from sqlalchemy import event
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import NO_VALUE
from sqlalchemy.orm.events import InstrumentationEvents

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, UnicodeText, DateTime, Text, LargeBinary
from sqlalchemy.orm.session import Session

from ..extensions import db
from ..core.entities import Entity
from ..entities import User


class ActivityEntry(db.Model):
  """Main table for all activities."""

  __tablename__ = 'activity_entry'

  uid = Column(Integer, primary_key=True)
  happened_at = Column(DateTime, default=datetime.utcnow)

  verb = Column(Text)

  actor_id = Column(Integer, ForeignKey(User.id))

  object_class = Column(Text)
  object_id = Column(Integer)

  subject = Column(Text)
  subject_id = Column(Integer)

  type = Column(Integer) # CREATION / UPDATE / DELETION

  entity_id = Column(Integer)
  entity_class = Column(Text)

  actor = relationship(User)


  def __repr__(self):
    return "<ActivityEntry uid=%s actor=%s verb=%s object=%s subject=%s>" % (
      self.uid, self.actor, self.verb, "TODO", "TODO")


class ActivityService(object):

  def __init__(self):
    signal("log-activity").connect(self.log_activity)
    
  def log_activity(self, actor, verb, object, subject):
    entry = ActivityEntry()
    entry.actor = actor
    entry.verb = verb
    entry.object_id = object.uid
    entry.object_class = object.__class__.__name__
    if subject:
      entry.subject_id = subject.uid
      entry.subject_class = subject.__class__.__name__

  @staticmethod
  def entries_for(entity):
    return ActivityEntry.query.filter(ActivityEntry.entity_id == entity.uid).all()
