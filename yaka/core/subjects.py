"""Subject classes (i.e. people, groups, etc.).

See ICOM-ics-v1.0 "Subject Branch".
"""

from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer, UnicodeText, DateTime, LargeBinary

from yaka.core.entities import Entity
from yaka.extensions import db


following = Table(
  'following', db.Model.metadata,
  Column('follower_uid', Integer, ForeignKey('user.uid')),
  Column('followee_uid', Integer, ForeignKey('user.uid'))
)


class UserQuery(Query):

  def get_by_email(self, email):
    return self.filter_by(email=email).all()[0]


class User(Entity):
  __tablename__ = 'user'
  __searchable__ = ['first_name', 'last_name', 'job_title', 'department', 'company']
  __editable__ = ['first_name', 'last_name', 'job_title', 'department', 'company', 'email', 'password']
  __exportable__ = __editable__ + ['created_at', 'updated_at']

  query = db.session.query_property(UserQuery)

  uid = Column(Integer, primary_key=True)

  first_name = Column(UnicodeText)
  last_name = Column(UnicodeText)
  job_title = Column(UnicodeText)
  department = Column(UnicodeText)
  company = Column(UnicodeText)

  email = Column(UnicodeText, nullable=False)
  password = Column(UnicodeText, nullable=False)

  photo = Column(LargeBinary)

  # location
  # manager
  # phone numbers (office, mobile)
  # email(s)
  # IM addresses
  # social networking addresses
  # relationships
  # properties
  # profile / interests / job description

  # settings

  # created / member since
  created = Column(DateTime, default=datetime.utcnow)
  updated = Column(DateTime, default=datetime.utcnow)

  followees = []
  followers = relationship("User", secondary=following,
                           primaryjoin=uid==following.c.follower_uid,
                           secondaryjoin=uid==following.c.followee_uid,
                           backref='followees')

  def follow(self, followee):
    self.followees.append(followee)

  def unfollow(self, followee):
    i = self.followees.index(followee)
    del self.followees[i]

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
    return "/users/%d" % self.uid

