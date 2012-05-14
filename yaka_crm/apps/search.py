from flask import render_template, request, Blueprint

from ..entities import *
from .dm import File

search = Blueprint("search", __name__, url_prefix="/search")

ALL_CLASSES = [Contact, Account, Lead, Opportunity, File]


@search.route("/")
def search_main():
  q = request.args.get("q")
  breadcrumbs = [
    dict(path="/", label="Home"),
    dict(path="", label="Search for '%s'" % q),
    ]

  res = []
  for klass in ALL_CLASSES:
    plural = klass.__name__ + 's'
    if plural == 'Opportunitys':
      plural = 'Opportunities'
    res.append((plural, list(klass.search_query(q).all())))

  return render_template('search/search.html', res=res,
                         breadcrumbs=breadcrumbs)


@search.route("/live")
def search_live():
  q = request.args.get("q")
  res = [ list(cls.search_query(q).all()) for cls in ALL_CLASSES ]

  if not sum(len(x) for x in res):
    return ""
  else:
    return render_template('search/live_search.html', res=res)
