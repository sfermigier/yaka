from functools import wraps

from flask import render_template, redirect, session, request
from flask.globals import g
from flask.helpers import url_for, flash
from flaskext.wtf import Form, TextField
from werkzeug.exceptions import abort
from wtforms.validators import Email, Length

from . import app
from .entities import *


__all__ = []

#
# Config. Hardcoded for now.
#
TABS = [
  {'id': 'accounts', 'label': 'Accounts', 'class': Account},
  {'id': 'contacts', 'label': 'Contacts', 'class': Contact},
  {'id': 'opportunities', 'label': 'Opportunities', 'class': Opportunity},
  {'id': 'leads', 'label': 'Leads', 'class': Lead},
]

#
# Utils
#
def get_params(names):
  """Returns dictionary with params from request"""
  params = {}
  for name in names:
    value = request.form.get(name) or request.files.get(name)
    if value is not None:
      params[name] = value
  return params

def get_tab_for(id):
  for d in TABS:
    if d['id'] == id:
      return d

@app.before_request
def before_request():
  g.user = User.query.get(1)
  g.tabs = TABS
  g.breadcrumbs = [dict(path='/', label='Home')]

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


@app.route("/tab/<tab_id>/")
def list_view(tab_id):
  g.tab_id = tab_id
  g.tab = get_tab_for(tab_id)
  g.breadcrumbs.append(dict(path="", label=g.tab['label']))

  cls = g.tab['class']
  entities = getattr(cls, 'query').all()

  table = cls.list_view(entities)
  return render_template('list_view.html', table=table)


@app.route("/tab/<tab_id>/<int:entity_id>")
def entity_view(tab_id, entity_id):
  g.tab_id = tab_id
  g.tab = get_tab_for(tab_id)
  g.breadcrumbs.append(dict(path="/tab/%s" % tab_id, label=g.tab['label']))

  cls = g.tab['class']
  entity = getattr(cls, 'query').get(entity_id)
  g.breadcrumbs.append(dict(path="", label=entity.display_name))

  view = entity.single_view()
  return render_template('single_view.html', view=view)


@app.route("/search")
def search():
  q = request.args.get("q")
  live = request.args.get("live")
  g.tab = get_tab_for('accounts')
  g.breadcrumbs.append(dict(path="", label="Search for '%s'" % q))

  contacts = list(Contact.search_query(q).all())
  accounts = list(Account.search_query(q).all())

  if live:
    if not contacts:
      return ""
    return render_template('live_search.html', contacts=contacts, accounts=accounts)
  else:
    return render_template('search.html', contacts=contacts, accounts=accounts)
