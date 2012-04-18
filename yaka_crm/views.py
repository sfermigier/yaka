from functools import wraps

from flask import render_template, redirect, session, request
from flask.globals import g

from . import app
from .entities import *


__all__ = []


@app.before_request
def before_request():
  g.user = User.query.get(1)


@app.template_filter('labelize')
def labelize(s):
  return " ".join([ w.capitalize() for w in s.split("_") ])


#  user_id = session.get("user_id")
#  if user_id:
#    try:
#      user = User.query.get(user_id)
#      g.user = user
#    except:
#      abort(401, "Must authenticate")
#  else:
#    g.user = None

#
# Navigation
#
@app.route("/")
def home():
  # TODO: dashboard
  return "OK"


@app.route("/admin/")
def admin():
  # TODO: admin
  return "ADMIN"


@app.route("/help/")
def help():
  # TODO: help
  return "HELP"


#@app.route("/tab/<tab_id>/")
#def list_view(tab_id):
#  g.tab_id = tab_id
#  g.tab = get_tab_for(tab_id)
#  g.breadcrumbs.append(dict(path="", label=g.tab['label']))
#
#  cls = g.tab['class']
#  entities = getattr(cls, 'query').all()
#
#  table = cls.list_view(entities)
#  return render_template('list_view.html', table=table)
#
#
#@app.route("/tab/<tab_id>/<int:entity_id>")
#def entity_view(tab_id, entity_id):
#  g.tab_id = tab_id
#  g.tab = get_tab_for(tab_id)
#  g.breadcrumbs.append(dict(path="/tab/%s" % tab_id, label=g.tab['label']))
#
#  cls = g.tab['class']
#  entity = getattr(cls, 'query').get(entity_id)
#  g.breadcrumbs.append(dict(path="", label=entity.display_name))
#
#  view = entity.single_view()
#  return render_template('single_view.html', view=view)
#
#
#@app.route("/tab/<tab_id>/<int:entity_id>/edit")
#def entity_edit(tab_id, entity_id):
#  g.tab_id = tab_id
#  g.tab = get_tab_for(tab_id)
#  g.breadcrumbs.append(dict(path="/tab/%s" % tab_id, label=g.tab['label']))
#
#  cls = g.tab['class']
#  entity = getattr(cls, 'query').get(entity_id)
#  g.breadcrumbs.append(dict(path="", label=entity.display_name))
#
#  view = entity.single_view()
#  return render_template('edit_view.html', view=view)
#
#
#@app.route("/tab/<tab_id>/<int:entity_id>/delete")
#def entity_delete(tab_id, entity_id):
#  return "deleted"


@app.route("/search")
def search():
  q = request.args.get("q")
  live = request.args.get("live")
  breadcrumbs = [
    dict(path="/", label="Home"),
    dict(path="", label="Search for '%s'" % q),
  ]

  contacts = list(Contact.search_query(q).all())
  accounts = list(Account.search_query(q).all())

  if live:
    if not contacts:
      return ""
    return render_template('live_search.html', contacts=contacts, accounts=accounts)
  else:
    return render_template('search.html', contacts=contacts, accounts=accounts, breadcrumbs=breadcrumbs)
