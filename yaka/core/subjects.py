"""Subject classes (i.e. people, groups, etc.).

See ICOM-ics-v1.0 "Subject Branch".
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer, UnicodeText, LargeBinary, Boolean, DateTime, Text

from yaka.core.entities import Entity, SEARCHABLE, SYSTEM
from yaka.extensions import db


# Tables for many-to-many relationships
following = Table(
  'following', db.Model.metadata,
  Column('follower_uid', Integer, ForeignKey('user.uid')),
  Column('followee_uid', Integer, ForeignKey('user.uid'))
)
membership = Table(
  'membership', db.Model.metadata,
  Column('user_uid', Integer, ForeignKey('user.uid')),
  Column('group_uid', Integer, ForeignKey('group.uid'))
)
administratorship = Table(
  'administratorship', db.Model.metadata,
  Column('user_uid', Integer, ForeignKey('user.uid')),
  Column('group_uid', Integer, ForeignKey('group.uid'))
)


class UserQuery(Query):
  def get_by_email(self, email):
    return self.filter_by(email=email).all()[0]


class User(Entity):
  __tablename__ = 'user'
  __editable__ = ['first_name', 'last_name', 'job_title', 'department', 'company', 'email', 'password']
  __exportable__ = __editable__ + ['created_at', 'updated_at', 'uid']

  query = db.session.query_property(UserQuery)

  # Basic information
  first_name = Column(UnicodeText, info=SEARCHABLE)
  last_name = Column(UnicodeText, info=SEARCHABLE)
  # Should we add gender, salutation ?

  # System information
  locale = Column(Text)

  # Additional information (should be customisable)
  job_title = Column(UnicodeText, info=SEARCHABLE)
  department = Column(UnicodeText, info=SEARCHABLE)
  company = Column(UnicodeText, info=SEARCHABLE)
  location = Column(UnicodeText)
  expertise = Column(UnicodeText)
  interests = Column(UnicodeText)
  # More: education, work experience, etc.

  email = Column(UnicodeText, nullable=False)
  # TODO: encrypt
  password = Column(UnicodeText, nullable=False)

  photo = Column(LargeBinary)

  # TODO: move to a roles or permission table
  is_admin = Column(Boolean, nullable=False, default=False)

  last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, info=SYSTEM)

  # TODO: add if needed:
  # location
  # manager
  # phone numbers (office, mobile)
  # email(s)
  # IM addresses
  # social networking addresses
  # properties
  # profile / interests / job description
  # settings

  uid = Entity.uid
  followers = relationship("User", secondary=following,
                           primaryjoin=(uid == following.c.follower_uid),
                           secondaryjoin=(uid == following.c.followee_uid),
                           backref='followees')
  followees = []

  groups = []

  def follow(self, followee):
    if followee == self:
      raise Exception("User can't follow self")
    self.followees.append(followee)

  def unfollow(self, followee):
    if followee == self:
      raise Exception("User can't follow self")
    i = self.followees.index(followee)
    del self.followees[i]

  def join(self, group):
    if not group in self.groups:
      self.groups.append(group)

  def leave(self, group):
    if group in self.groups:
      del self.groups[self.groups.index(group)]

  #
  # Boolean properties
  #
  def is_following(self, other):
    return other in self.followees

  def is_member_of(self, group):
    return self in group.members

  def is_admin_of(self, group):
    return self in group.admins

  @property
  def is_active(self):
    return datetime.utcnow() - self.last_active <= timedelta(0, 60)

  #
  # Other properties
  #
  @property
  def username(self):
    return (self.first_name or "") + (self.last_name or "")

  @property
  def name(self):
    return (self.first_name or "Unknown") + " " + (self.last_name or "Unknown")

  def __unicode__(self):
    return self.name

  # XXX: Should entities know about their own URL? I guess yes.
  @property
  def url(self):
    return "/social/users/%d" % self.uid

  # FIXME: choose canonical name
  _url = url


class Group(Entity):
  __tablename__ = 'group'
  __editable__ = ['name', 'description']
  __exportable__ = __editable__ + ['created_at', 'updated_at', 'uid']


  name = Column(UnicodeText, nullable=False, info=SEARCHABLE)
  description = Column(UnicodeText, info=SEARCHABLE)

  members = relationship("User", secondary=membership,
                         backref='groups')
  admins = relationship("User", secondary=administratorship)

  photo = Column(LargeBinary)

  # Should entities know about their own URL? I guess yes.
  @property
  def url(self):
    return "/social/groups/%d" % self.uid

  # FIXME: choose canonical name
  _url = url


