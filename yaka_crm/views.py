from functools import wraps

from flask import render_template, redirect, session, request
from flask.globals import g

from . import app
from .entities import *
from .frontend import CRM


__all__ = []


@app.before_request
def before_request():
  g.user = User.query.get(1)
  g.modules = CRM.modules
  g.recent_items = session.get('recent_items', [])


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


@app.route("/help/")
def help():
  # TODO: help
  return "HELP"


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
