from flask import render_template, request, Blueprint
from jinja2._markupsafe import Markup

from ..entities import *
from .dm import File


search = Blueprint("search", __name__, url_prefix="/search")

# File must be first
ALL_CLASSES = [File, Contact, Account, Lead, Opportunity]


@search.route("/")
def search_main():
  q = request.args.get("q")
  breadcrumbs = [
    dict(path="/", label="Home"),
    dict(path="", label="Search for '%s'" % q),
    ]

  hits = list(File.search_query.search(q))
  documents = [(obj, hit, Markup(hit.highlights("text", text=obj.text)))
               for hit, obj in hits if obj]

  res = []
  for cls in ALL_CLASSES[1:]:
    plural = cls.__name__ + 's'
    if plural == 'Opportunitys':
      plural = 'Opportunities'
    res.append((plural, list(cls.search_query(q).all())))

  return render_template('search/search.html', res=res, documents=documents,
                         breadcrumbs=breadcrumbs)


@search.route("/live")
def search_live():
  q = request.args.get("q")
  res = reduce(lambda x, y: x + y, [list(cls.search_query(q).all()) for cls in ALL_CLASSES])

  if not res:
    return ""
  else:
    return render_template('search/live_search.html', res=res)
