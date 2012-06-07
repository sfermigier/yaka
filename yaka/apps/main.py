"""Main views.
"""

from flask import render_template, session, request, Blueprint
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import redirect

from ..entities import *

from ..core.frontend import TableView, BreadCrumbs
from ..frontend import Contacts, Opportunities, Leads, Accounts


__all__ = []

main = Blueprint("main", __name__, url_prefix="")

#
# Authentication
#
@main.route("/login")
def login_form():
  """Login form."""
  return render_template("login.html")


@main.route("/login", methods=['POST'])
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


@main.route("/logout")
def logout():
  del session['user_id']
  return redirect("/login")


#
# Basic navigation
#
@main.route("/")
def home():
  """Home page."""
  return redirect("/social/")


# Hackish home page for the CRM apps. TODO: redefine & refactor.
@main.route("/crm/")
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


@main.route("/help/")
def help():
  # TODO: help
  return render_template('help.html')


@main.errorhandler(404)
def page_not_found(error):
  return render_template('error404.html'), 404
