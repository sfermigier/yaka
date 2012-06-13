from flask import Blueprint, render_template, redirect, g
from flask.globals import request
from flask.helpers import make_response
from flaskext.babel import lazy_gettext as _

from yaka.core import signals
from yaka.core.frontend import BreadCrumbs
from yaka.core.subjects import User, Group
from yaka.core.util import get_params
from yaka.extensions import db

from .content import Message, PrivateMessage
from .util import Env
from yaka.services.image import crop_and_resize

__all__ = ['social']

ROOT = '/social'
social = Blueprint("social", __name__, url_prefix=ROOT)


def make_bread_crumbs(path="", label=None):
  bread_crumbs = BreadCrumbs([("/", "Home"), ("/social/", "Social")])
  if label:
    return bread_crumbs + (path, label)
  else:
    return bread_crumbs


@social.route("/")
def home():
  e = Env()
  e.bread_crumbs = make_bread_crumbs()

  #group_ids = [None] + [ group.uid for group in g.user.groups ]

  messages = Message.query.filter(Message.group_id==None).all()
  for group in g.user.groups:
    messages += Message.query.filter(Message.group_id==group.uid).all()
  messages.sort(lambda x, y: -cmp(x.uid, y.uid))
  e.messages = messages

  # Alternate technique
  #  group_ids = [ group.uid for group in g.user.groups ]
  #  messages = Message.query.filter(Message.group_id.in_(group_ids)) \
  #      .order_by(Message.created_at) \
  #      .limit(20).all()

  e.latest_visitors = User.query.order_by(User.last_active.desc()).limit(15).all()

  return render_template("social/home.html", **e)


@social.route("/stream/<stream_name>")
def stream(stream_name):
  pass


@social.route("/", methods=['POST'])
def share():
  d = get_params(Message.__editable__)
  message = Message(**d)
  db.session.add(message)
  db.session.commit()
  signals.entity_created.send(message)

  return redirect(ROOT)


@social.route("/private/")
def private():
  bread_crumbs = make_bread_crumbs()
  return render_template("social/home.html", bread_crumbs=bread_crumbs)


@social.route("/private/", methods=['POST'])
def private_post():
  """Post a private message."""
  bread_crumbs = make_bread_crumbs()
  return render_template("social/home.html", bread_crumbs=bread_crumbs)


@social.route("/<users_or_groups>/<int:uid>/mugshot")
def mugshot(users_or_groups, uid):
  size = int(request.args.get('s', 0))
  if size > 500:
    raise Exception("Error, size = %d" % size)

  if users_or_groups == "users":
    subject = User.query.get(uid)
  else:
    subject = Group.query.get(uid)

  data = subject.photo
  if size:
    data = crop_and_resize(data, size)

  response = make_response(data)
  response.headers['content-type'] = 'image/jpeg'
  return response
