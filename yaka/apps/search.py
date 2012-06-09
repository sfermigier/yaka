from flask import render_template, request, Blueprint
from jinja2._markupsafe import Markup
from whoosh.query.terms import Term

from yaka.services import indexing
from yaka.core.util import Pagination

from .crm.entities import *
from .dm import File


# TODO: make it a config param
PAGE_SIZE = 10


search = Blueprint("search", __name__, url_prefix="/search")

# Some hardcoded settings (for now)

# File must be first
ALL_CLASSES = [File, Contact, Account, Lead, Opportunity]

COLUMNS = [
  dict(name="name", width="40%"),
  dict(name="creator", width="20%"),
  dict(name="owner", width="20%"),
  dict(name="updated_at", width="20%"),
  ]


class Wrapper(object):

  def __init__(self, obj):
    self.obj = obj

  def __getitem__(self, name):
    value = getattr(self.obj, name)

    if name == "name":
      return Markup('<a href="%s"><img src="%s"> %s</a>'
                    % (self.obj._url, self.obj._icon(), value))
    if isinstance(value, Entity):
      return Markup('<a href="%s">%s</a>' % (value._url, value.name))
    if hasattr(value, 'strftime'):
      return value.strftime("%Y-%m-%d %H:%M")
    return value


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
    class_name = cls.__name__
    plural =  class_name + 's'
    if plural == 'Opportunitys':
      plural = 'Opportunities'

    result = list(cls.search_query(q).all())
    result = [Wrapper(obj) for obj in result]
    if result:
      res.append((plural, result, COLUMNS))

  return render_template('search/search.html', query_string=q,
                         res=res, documents=documents,
                         breadcrumbs=breadcrumbs)


@search.route("/docs")
def search_docs():
  """Alternative route for document search."""

  q = request.args.get("q")
  page = int(request.args.get("page", 1))

  breadcrumbs = [
    dict(path="/", label="Home"),
    dict(path="", label="Search for '%s'" % q),
  ]

  index_service = indexing.get_service()
  results = index_service.search(q, File, page*PAGE_SIZE)
  hit_count = results.estimated_length()

  pagination = Pagination(page, PAGE_SIZE, hit_count)

  facets = []
  facets.append(make_facet(results, "Language", "language"))
  facets.append(make_facet(results, "File format", "mime_type"))
  facets.append(make_facet(results, "Creator", "creator"))
  facets.append(make_facet(results, "Owner", "owner"))
  #  ('Created since', []),
  #  ('Modified since', []),

  hits = results[(page-1)*PAGE_SIZE:page*PAGE_SIZE]

  return render_template('search/search-docs.html',
                         query=q,
                         hits=hits,
                         hit_count=hit_count,
                         pagination=pagination,
                         facets=facets,
                         breadcrumbs=breadcrumbs)


def make_facet(hits, name, group, limit=10):
  l = [ (k, len(v)) for k, v in hits.groups(group).items()]
  l.sort(key=lambda x: x[1], reverse=True)
  if limit and limit < len(l):
    l = l[0:limit]
  return [name, l]


@search.route("/ajax")
def ajax():
  q = request.args.get("q")
  page = int(request.args.get("page", 1))
  filters = request.args.getlist("filters[]")

  index_service = indexing.get_service()

  if not filters:
    results = index_service.search(q, File, limit=page*PAGE_SIZE)
    hit_count = results.estimated_length()
  else:
    fieldname, text = filters[0].split(":", 1)
    filter = Term(fieldname, text)
    print filter
    results = index_service.search(q, File, limit=page*PAGE_SIZE, filter=filter)
    hit_count = results.estimated_length()


  pagination = Pagination(page, PAGE_SIZE, hit_count)


  hits = results[(page-1)*PAGE_SIZE:page*PAGE_SIZE]

  return render_template('search/search-ajax.html',
                         query=q,
                         hits=hits,
                         hit_count=hit_count,
                         pagination=pagination)


@search.route("/live")
def search_live():
  q = request.args.get("q")
  res = reduce(lambda x, y: x + y,
               [list(cls.search_query(q).all()) for cls in ALL_CLASSES])

  if not res:
    return ""
  else:
    return render_template('search/live_search.html', res=res)
