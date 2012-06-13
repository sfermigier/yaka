from flask import Blueprint, render_template, redirect, g
from flaskext.babel import lazy_gettext as _

from yaka.core import signals
from yaka.core.frontend import BreadCrumbs
from yaka.core.subjects import User
from yaka.core.util import get_params
from yaka.extensions import db

from .content import Message, PrivateMessage
from .util import Env

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

  e.latest_visitors = User.query.order_by(User.last_active).limit(15).all()

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
