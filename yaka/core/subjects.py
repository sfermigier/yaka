"""Subject classes (i.e. people, groups, etc.).

See ICOM-ics-v1.0 "Subject Branch".
"""

from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer, UnicodeText, LargeBinary, Boolean

from yaka.core.entities import Entity, SEARCHABLE
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


class UserQuery(Query):

  def get_by_email(self, email):
    return self.filter_by(email=email).all()[0]


class User(Entity):
  __tablename__ = 'user'
  __editable__ = ['first_name', 'last_name', 'job_title', 'department', 'company', 'email', 'password']
  __exportable__ = __editable__ + ['created_at', 'updated_at', 'uid']

  query = db.session.query_property(UserQuery)

  first_name = Column(UnicodeText, info=SEARCHABLE)
  last_name = Column(UnicodeText, info=SEARCHABLE)
  job_title = Column(UnicodeText, info=SEARCHABLE)
  department = Column(UnicodeText, info=SEARCHABLE)
  company = Column(UnicodeText, info=SEARCHABLE)

  email = Column(UnicodeText, nullable=False)
  # TODO: encrypt
  password = Column(UnicodeText, nullable=False)

  photo = Column(LargeBinary)

  # TODO: move to a roles or permission table
  is_admin = Column(Boolean, nullable=False, default=False)

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
                           primaryjoin=(uid==following.c.follower_uid),
                           secondaryjoin=(uid==following.c.followee_uid),
                           backref='followees')
  followees = []

  groups = relationship("Group", secondary=membership,
                        backref='members')

  def follow(self, followee):
    self.followees.append(followee)

  def unfollow(self, followee):
    i = self.followees.index(followee)
    del self.followees[i]

  def join(self, group):
    if not group in self.groups:
      self.groups.append(group)

  def leave(self, group):
    if group in self.groups:
      del self.groups[self.groups.index(group)]

  @property
  def username(self):
    return (self.first_name or "") + (self.last_name or "")

  @property
  def name(self):
    return (self.first_name or "Unknown") + " " + (self.last_name or "Unknown")

  def __unicode__(self):
    return self.name

  # Should entities know about their own URL? I guess yes.
  @property
  def _url(self):
    return "/social/users/%d" % self.uid


class Group(Entity):
  __tablename__ = 'group'

  name = Column(UnicodeText, nullable=False, info=SEARCHABLE)

  members = []


