from flask import render_template, redirect, flash, url_for
from flaskext.babel import lazy_gettext as _

from yaka.core.subjects import User, Group
from yaka.core.frontend import BreadCrumbs

from .social import social
from .forms import GroupForm
from .util import Env
from yaka.extensions import db


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
  e.groups = Group.query.all()
  return render_template("social/groups.html", **e)


@social.route("/groups/<int:group_id>")
def group_home(group_id):
  e = Env()
  e.bread_crumbs = make_bread_crumbs()
  e.group = Group.query.get(group_id)
  return render_template("social/group.html", **e)


@social.route("/groups/new")
def groups_new():
  e = Env()
  e.bread_crumbs = make_bread_crumbs()
  e.form = GroupForm()
  return render_template("social/groups-new.html", **e)


@social.route("/groups/new", methods=['POST'])
def groups_new_post():
  form = GroupForm()

  if form.validate():
    group = Group()
    form.populate_obj(group)
    db.session.add(group)
    db.session.commit()
    flash(_("Your new group has been created"), category='info')
    return redirect(url_for('.group_home', group_id=group.uid))

  else:
    e = Env()
    e.bread_crumbs = make_bread_crumbs()
    e.form = form
    return render_template("social/groups-new.html", **e)
