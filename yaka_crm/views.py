from flask import render_template, session, request
from flask.globals import g
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from . import app
from .entities import *
from .frontend import CRM

from yaka_crm.core.frontend import TableView, BreadCrumbs
from yaka_crm.frontend import Contacts, Opportunities, Leads, Accounts

import filters #don't remove

__all__ = []


@app.before_request
def before_request():
  # TODO remove when tests pass
  if app.config.get("UNSAFE", False):
    g.user = User.query.all()[0]

  else:
    user_id = session.get("user_id")
    if user_id:
      try:
        user = User.query.get(user_id)
        g.user = user
      except:
        return redirect("/login", code=401)
        #abort(401, "Must authenticate")
    elif request.path == '/login' or request.path.startswith("/static/"):
      g.user = None
    else:
      return redirect("/login", code=401)
      #abort(401, "Must authenticate")

  g.modules = CRM.modules
  g.recent_items = session.get('recent_items', [])


#
# Authentication
#
@app.route("/login")
def login_form():
  """Login form."""
  return render_template("login.html")


@app.route("/login", methods=['POST'])
def login():
  if 'user_id' in session:
    del session['user_id']

  email = request.form.get('email')
  password = request.form.get('password')

  if not email or not password:
    err_msg = "You must provide your email and password."
    return render_template("login.html", err_msg=err_msg), 401

  try:
    user = User.query.filter(User.email == email).one()
  except NoResultFound:
    err_msg = "Sorry, we couldn't find an account for email '%s'." % email
    return render_template("login.html", err_msg=err_msg), 401

  # TODO: encrypt passwd
  if user and password != user.password:
    err_msg = "Sorry, wrong password."
    return render_template("login.html", err_msg=err_msg), 401

  # Login successful
  session['user_id'] = user.uid
  return redirect("/")


@app.route("/logout")
def logout():
  del session['user_id']
  return redirect("/login")


#
# Basic navigation
#
@app.route("/test")
def test():
  return "BAD", 401


@app.route("/")
def home():
  """Home page."""
  return redirect("/social/")


# Hackish home page for the CRM apps. TODO: redefine & refactor.
@app.route("/crm/")
def crm_home():
  bc = BreadCrumbs([('/', "Home"), ('/crm/', 'CRM')])

  tables = []
  for cls in [Accounts, Leads, Opportunities, Contacts]:
    managed_class = cls.managed_class
    entities = managed_class.query.limit(10).all()

    table_view = TableView(cls.list_view_columns)
    rendered_table = table_view.render(entities)
    tables.append(dict(name=cls.__name__, rendered=rendered_table))

  return render_template('crm/home.html', tables=tables, breadcrumbs=bc)


@app.route("/help/")
def help():
  # TODO: help
  return render_template('help.html')


@app.errorhandler(404)
def page_not_found(error):
  return render_template('error404.html'), 404
