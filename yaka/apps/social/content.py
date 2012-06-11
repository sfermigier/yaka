"""
Social content items: messages aka status updates, private messages, etc.
"""

from datetime import datetime
import json

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, UnicodeText, DateTime, LargeBinary

from yaka.core.subjects import User
from yaka.core.entities import Entity, SEARCHABLE
from yaka.extensions import db

__all__ = ['Message', 'PrivateMessage']


# TODO: get rid of flask-sqlalchemy, replace db.Model by Base ?
#Base = declarative_base()

#class BaseModel(AbstractConcreteBase, db.Model):
#
#  def __init__(self, **kw):
#    self.update(kw)
#
#  def column_names(self):
#    return [ col.name for col in class_mapper(self.__class__).mapped_table.c ]
#
#  def update(self, d):
#    for k, v in d.items():
#      assert k in self.column_names(), "%s not allowed" % k
#      if type(v) == type(""):
#        v = unicode(v)
#      setattr(self, k, v)


class Message(Entity):
  """Message aka Status update aka Note.

  See: http://activitystrea.ms/head/activity-schema.html#note
  """
  __tablename__ = 'message'
  __editable__ = ['content']
  __exportable__ = __editable__ + ['uid', 'created_at', 'updated_at', 'creator_id', 'owner_id']

  content = Column(UnicodeText, info=SEARCHABLE)
  #group_id = Column(Integer, ForeignKey(Group.uid), nullable=False)

  @classmethod
  def query_by_creator(cls, user):
    return db.session.query(cls).filter(cls.creator_id==user.uid)


class PrivateMessage(Entity):
  """Private messages are like messages, except they are private."""

  __tablename__ = 'private_message'
  __editable__ = ['content']
  __exportable__ = __editable__ + ['uid', 'created_at', 'updated_at', 'creator_id', 'owner_id']

  content = Column(UnicodeText, info={'searchable': True})
  recipient_id = Column(Integer, ForeignKey(User.uid), nullable=False)


class Attachment(Entity):
  __tablename__ = 'attachment'

  content = Column(LargeBinary)


# TODO: doesn't belong here
class Activity(Entity):
  """Activity entry

  See: http://activitystrea.ms/specs/atom/1.0/#activity
  See: http://stackoverflow.com/questions/1443960/how-to-implement-the-activity-stream-in-a-social-network
  """
  __tablename__ = 'activity'
  __editable__ = []

  user_id = Column(Integer, ForeignKey(User.uid), nullable=False)
  time = Column(DateTime)
  activity_type = Column(Integer)
  source_id = Column(Integer)

  #parent_id = Column(Integer)
  #parent_type = Column(Integer)
