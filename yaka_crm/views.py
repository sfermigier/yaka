from flask import render_template, session, request
from flask.globals import g

from . import app
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import redirect
from .entities import *
from .frontend import CRM
from yaka_crm.ged import File


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

  res = []
  for klass in [Contact, Account, Lead, Opportunity, File]:
    plural = klass.__name__ + 's'
    if plural == 'Opportunitys':
      plural = 'Opportunities'
    res.append((plural, list(klass.search_query(q).all())))

  num_results = sum([len(x) for x in res])

  if live:
    if not num_results:
      return ""
    return render_template('search/live_search.html', res=res)
  else:
    return render_template('search/search.html', res=res,
                           breadcrumbs=breadcrumbs)


@app.errorhandler(404)
def page_not_found(error):
  return render_template('error404.html'), 404
