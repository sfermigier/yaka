from flask import render_template, request, Blueprint
from jinja2._markupsafe import Markup

from ..entities import *
from .dm import File


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


@search.route("/live")
def search_live():
  q = request.args.get("q")
  res = reduce(lambda x, y: x + y,
               [list(cls.search_query(q).all()) for cls in ALL_CLASSES])

  if not res:
    return ""
  else:
    return render_template('search/live_search.html', res=res)
