from flask import Blueprint, render_template, request, make_response
from sqlalchemy.sql.expression import not_

from ..entities import User
from ..core.frontend import BreadCrumbs
from ..services.image import crop_and_resize
from ..services.activity import ActivityEntry
from ..services.audit import AuditEntry

from .dm import File


users = Blueprint("users", __name__, url_prefix="/users")


def make_bread_crumbs(path="", label=None):
  bread_crumbs = BreadCrumbs([("/", "Home"), ("/users", "Users")])
  if label:
    return bread_crumbs + (path, label)
  else:
    return bread_crumbs

def make_tabs(user):
  return [
    dict(id='activity', label='Activity', link=user._url, is_active=True),
    dict(id='profile', label='Profile', link=user._url + '?tab=profile'),
    dict(id='documents', label='Documents', link=user._url + '?tab=documents'),
    dict(id='images', label='Images', link=user._url + '?tab=images'),
    dict(id='audit', label='Audit', link=user._url + '?tab=audit'),
  ]

# Not a great idea (can't be used as a ** argument).
class Env(object):
  _d = {}

  def __init__(self, label=None, **kw):
    self.__dict__['_d'] = {}

    self.bread_crumbs = self.breadcrumbs = make_bread_crumbs(label=label)
    for key, value in kw.items():
      self._d[key] = value

  def __setattr__(self, key, value):
    self._d[key] = value

  def __iter__(self):
    return self._d.iterkeys()

  def __getitem__(self, key):
    return self._d[key]


@users.route("/")
def home():
  e = Env()
  e.bread_crumbs = make_bread_crumbs()
  e.users = User.query.all()
  return render_template("users/home.html", **e._d)


@users.route("/<int:user_id>")
def user_view(user_id):
  user = User.query.get(user_id)
  tab = request.args.get("tab", "activity")

  e = Env(label=user.name, user=user)
  e.active_tab_id = tab
  e.tabs = make_tabs(user)

  if tab == "activity":
    # XXX quick & dirty
    e.activity_entries =\
        ActivityEntry.query.filter(ActivityEntry.actor_id == user.uid).limit(30).all()

  elif tab == "audit":
    # XXX quick & dirty
    e.audit_entries =\
        AuditEntry.query.filter(AuditEntry.user_id == user.uid).limit(30).all()

  elif tab in ("documents", "images"):
    files = File.query.filter(File.owner_id == user_id)
    if tab == "documents":
      files = files.filter(not_(File.mime_type.like("image/%")))
      e.documents = files.all()
    elif tab == "images":
      files = files.filter(File.mime_type.like("image/%"))
      e.images = files.all()

  return render_template("users/user.html", **e._d)


@users.route("/<int:user_id>/mugshot")
def mugshot(user_id):
  size = int(request.args.get('s', 0))
  if size > 500:
    raise Exception("Error, size = %d" % size)
  user = User.query.get(user_id)

  data = user.photo
  if size:
    data = crop_and_resize(data, size)

  response = make_response(data)
  response.headers['content-type'] = 'image/jpeg'
  return response


@users.route("/groups/")
def groups_home():
  e = Env()
  e.bread_crumbs = make_bread_crumbs()
  e.users = User.query.all()
  return render_template("users/groups.html", **e._d)

