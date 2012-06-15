from flask import render_template, redirect, flash, url_for, request, g
from flaskext.babel import lazy_gettext as _

from yaka.core.subjects import User, Group
from yaka.core.frontend import BreadCrumbs
from yaka.extensions import db

from .social import social
from .forms import GroupForm
from .util import Env


def make_bread_crumbs(path="", label=None):
  bread_crumbs = BreadCrumbs([("/", "Home"), ("/users", "Users")])
  if label:
    return bread_crumbs + (path, label)
  else:
    return bread_crumbs


@social.route("/groups/")
def groups_home():
  tab = request.args.get("tab", "all_groups")
  e = Env()
  e.bread_crumbs = make_bread_crumbs()
  if tab == 'all_groups':
    e.groups = Group.query.all()
  else:
    e.groups = g.user.groups
    e.groups.sort(lambda x, y: cmp(x.name, y.name))
  return render_template("social/groups.html", **e)


@social.route("/groups/<int:group_id>")
def group_home(group_id):
  e = Env()
  e.bread_crumbs = make_bread_crumbs()
  e.group = Group.query.get(group_id)
  return render_template("social/group.html", **e)


@social.route("/groups/<int:group_id>", methods=['POST'])
def group_post(group_id):
  group = Group.query.get(group_id)
  action = request.form.get('action')
  if action == 'join':
    g.user.join(group)
  elif action == 'leave':
    g.user.leave(group)
  else:
    raise Exception("Should not happen")
  db.session.commit()

  return redirect(url_for(".group_home", group_id=group_id))


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
