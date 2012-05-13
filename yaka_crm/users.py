from StringIO import StringIO
from PIL import Image
from flask import Blueprint
from flask import render_template
from flask.globals import request
from flask.helpers import make_response

from .entities import User
from .core.frontend import BreadCrumbs
from .services.audit import AuditEntry
from .services.image import resize


users = Blueprint("users", __name__, url_prefix="/users")


def make_bread_crumbs(path=None, label=None):
  bread_crumbs = BreadCrumbs([("/", "Home"), ("/users", "Users")])
  if label:
    return bread_crumbs + (path, label)
  else:
    return bread_crumbs


# Not a great idea (can't be used a a ** argument).
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
  e = Env(label=user.name, user=user)
  e.audit_entries = AuditEntry.query.filter(AuditEntry.user_id==user_id).all()
  # TODO
  e.activity_entries = []
  return render_template("users/user.html", **e._d)


@users.route("/<int:user_id>/mugshot")
def mugshot(user_id):
  size = int(request.args.get('s', 0))
  user = User.query.get(user_id)

  if size == 0:
    data = user.photo
  else:
    data = resize(user.photo, size)

  response = make_response(data)
  response.headers['content-type'] = 'image/jpeg'
  return response
