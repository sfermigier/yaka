from flask import Blueprint
from flask import render_template
from flask.globals import request
from flask.helpers import make_response
from sqlalchemy.sql.expression import not_

from .entities import User
from .core.frontend import BreadCrumbs
from .services.image import resize
from .dm import File


users = Blueprint("users", __name__, url_prefix="/users")


def make_bread_crumbs(path=None, label=None):
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
  ]

# Not a great idea (can't be used as a ** argument).
class Env(object):
  _d = {}

  def __init__(self, label=None, **kw):
    self.__dict__['_d'] = {}

    self.bread_crumbs = self.breadcrumbs = make_bread_crumbs()
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
    # TODO
    e.activity_entries = []

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

  if size == 0:
    data = user.photo
  else:
    data = resize(user.photo, size)

  response = make_response(data)
  response.headers['content-type'] = 'image/jpeg'
  return response
