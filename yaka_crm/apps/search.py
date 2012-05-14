from flask import render_template, request, Blueprint

from ..entities import *
from .dm import File

search = Blueprint("search", __name__, url_prefix="/search")


@search.route("/")
def search_main():
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
