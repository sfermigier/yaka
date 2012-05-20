from flask import render_template, session, request
from flask.globals import g
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import redirect

from . import app
from .entities import *
from .frontend import CRM

from datetime import datetime
from yaka_crm.core.frontend import TableView, BreadCrumbs
from yaka_crm.frontend import Contacts, Opportunities, Leads, Accounts


__all__ = []


@app.before_request
def before_request():
  # FIXME: temp hack
  g.user = User.query.all()[0]
  g.modules = CRM.modules
  g.recent_items = session.get('recent_items', [])


@app.template_filter('labelize')
def labelize(s):
  return " ".join([ w.capitalize() for w in s.split("_") ])


@app.template_filter('filesize')
def filesize(d):
  if d < 1000:
    return "%d B" % d

  if d < 1e4:
    return "%.1f kB" % (d / 1e3)
  if d < 1e6:
    return "%.0f kB" % (d / 1e3)

  if d < 1e7:
    return "%.1f MB" % (d / 1e6)
  if d < 1e9:
    return "%.0f MB" % (d / 1e6)

  if d < 1e10:
    return "%.1f GB" % (d / 1e9)

  return "%.0f GB" % (d / 1e9)


@app.template_filter('age')
def age(dt, now=None):
  # Fail silently for now XXX
  if not dt:
    return ""

  if not now:
    now = datetime.utcnow()

  age = now - dt
  if age.days == 0:
    if age.seconds < 120:
      age_str = "a minute ago"
    elif age.seconds < 3600:
      age_str = "%d minutes ago" % (age.seconds / 60)
    elif age.seconds < 7200:
      age_str = "an hour ago"
    else:
      age_str = "%d hours ago" % (age.seconds / 3600)
  else:
    if age.days == 1:
      age_str = "yesterday"
    elif age.days <= 31:
      age_str = "%d days ago" % age.days
    elif age.days <= 72:
      age_str = "a month ago"
    elif age.days <= 365:
      age_str = "%d months ago" % (age.days / 30)
    else:
      age_str = "%d years ago" % (age.days / 365)

  return age_str


@app.template_filter('date_age')
def date_age(dt, now=None):
  # Fail silently for now XXX
  if not dt:
    return ""
  age_str = age(dt, now)
  return "%s (%s)" % (dt.strftime("%Y-%m-%d %H:%M"), age_str)


@app.template_filter('abbrev')
def abbrev(s, max_size):
  if len(s) <= max_size:
    return s
  else:
    h = max_size / 2 - 1
    return s[0:h] + "..." + s[-h:]


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
@app.route("/login")
def login_form():
  """Login form."""
  return render_template("login.html")


@app.route("/login", methods=['POST'])
def login():
  email = request.form.get('email')
  password = request.form.get('password')
  err_msg = ""

  try:
    user = User.query.filter(User.email == email).one()
  except NoResultFound:
    user = None
    err_msg = "Sorry, we couldn't find an account for email %s." % email

  # TODO: encrypt passwd
  if user and password != user.password:
    user = None
    err_msg = "Sorry, wrong password."

  if not user:
    if 'user_id' in session:
      del session['user_id']
    return render_template("login.html", err_msg=err_msg), 401
  else:
    session['user_id'] = user.uid
    return redirect("/")


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
