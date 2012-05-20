from flask import Blueprint
from flask import render_template
from flask.globals import request
from flask.helpers import make_response
from sqlalchemy.sql.expression import not_

from ..entities import User
from ..core.frontend import BreadCrumbs
from ..services.image import crop_and_resize

from .dm import File


social = Blueprint("social", __name__, url_prefix="/social")


def make_bread_crumbs(path="", label=None):
  bread_crumbs = BreadCrumbs([("/", "Home"), ("/social/", "Social")])
  if label:
    return bread_crumbs + (path, label)
  else:
    return bread_crumbs


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


@social.route("/")
def home():
  e = Env()
  e.bread_crumbs = make_bread_crumbs()
  return render_template("social/home.html", **e._d)

