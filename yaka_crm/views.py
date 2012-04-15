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


@app.route("/admin")
def admin():
  # TODO: admin
  return "ADMIN"


@app.route("/help")
def help():
  # TODO: help
  return "HELP"


@app.route("/<tab_id>/")
def list_view(tab_id):
  g.tab = get_tab_for(tab_id)
  class_ = g.tab['class']
  entities = getattr(class_, 'query').all()
  columns = class_.__list_view__
  return render_template('list_view.html', entities=entities, columns=columns, getattr=getattr)

@app.route("/<tab_id>/<int:entity_id>")
def entity_view(tab_id, entity_id):
  g.tab = get_tab_for(tab_id)
  class_ = g.tab['class']
  entities = getattr(class_, 'query').get(entity_id)
  columns = class_.__list_view__
  return render_template('entity_view.html', entities=entities, columns=columns, getattr=getattr)
