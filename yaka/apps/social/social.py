from flask import Blueprint, render_template

from yaka.core.frontend import BreadCrumbs

__all__ = ['social']

social = Blueprint("social", __name__, url_prefix="/social")


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
