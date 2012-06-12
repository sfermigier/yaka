from flask import render_template
from yaka.apps.social.util import Env

from yaka.core.subjects import User
from yaka.core.frontend import BreadCrumbs

from .social import social


def make_bread_crumbs(path="", label=None):
  bread_crumbs = BreadCrumbs([("/", "Home"), ("/users", "Users")])
  if label:
    return bread_crumbs + (path, label)
  else:
    return bread_crumbs


@social.route("/groups/")
def groups_home():
  e = Env()
  e.bread_crumbs = make_bread_crumbs()
  e.users = User.query.all()
  return render_template("social/groups.html", **e)

