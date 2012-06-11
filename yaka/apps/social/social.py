from flask import Blueprint, render_template, redirect

from yaka.core import signals
from yaka.core.frontend import BreadCrumbs
from yaka.core.util import get_params
from yaka.extensions import db

from .content import Message, PrivateMessage

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
  bread_crumbs = make_bread_crumbs()
  return render_template("social/home.html", bread_crumbs=bread_crumbs)


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


@social.route("/users/")
def users():
  pass

