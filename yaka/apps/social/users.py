from flask import render_template, request, make_response
from flaskext.babel import lazy_gettext as _

from sqlalchemy.sql.expression import not_, or_

from yaka.core.subjects import User
from yaka.core.frontend import BreadCrumbs
from yaka.services.image import crop_and_resize
from yaka.services.activity import ActivityEntry
from yaka.services.audit import AuditEntry

from .social import social
from .util import Env
from ..dm import File


def make_bread_crumbs(path="", label=None):
  bread_crumbs = BreadCrumbs([("/", "Home"), ("/users", "Users")])
  if label:
    return bread_crumbs + (path, label)
  else:
    return bread_crumbs

def make_tabs(user):
  return [
    dict(id='activity', label='Activity', link=user._url, is_active=True),
    dict(id='profile', label='Profile', link=user._url + '?tab=profile'),
    dict(id='documents', label='Documents', link=user._url + '?tab=documents'),
    dict(id='images', label='Images', link=user._url + '?tab=images'),
    dict(id='audit', label='Audit', link=user._url + '?tab=audit'),
    ]


@social.route("/users/")
def users_home():
  query = request.args.get("query")
  e = Env()
  e.bread_crumbs = make_bread_crumbs()

  if query:
    query = query.replace("%", " ")
    q = or_(User.first_name.like("%"+query+"%"), User.last_name.like("%"+query+"%"))
    e.users = User.query.filter(q).all()
  else:
    e.users = User.query.all()
  return render_template("social/users.html", **e)


@social.route("/users/<int:user_id>")
def user_view(user_id):
  user = User.query.get(user_id)
  tab = request.args.get("tab", "activity")

  e = Env(label=user.name, user=user)
  e.bread_crumbs = make_bread_crumbs()
  e.active_tab_id = tab
  e.tabs = make_tabs(user)

  if tab == "activity":
    # XXX quick & dirty
    e.activity_entries =\
    ActivityEntry.query.filter(ActivityEntry.actor_id == user.uid).limit(30).all()

  elif tab == "audit":
    # XXX quick & dirty
    e.audit_entries =\
    AuditEntry.query.filter(AuditEntry.user_id == user.uid).limit(30).all()

  elif tab in ("documents", "images"):
    files = File.query.filter(File.owner_id == user_id)
    if tab == "documents":
      files = files.filter(not_(File.mime_type.like("image/%")))
      e.documents = files.all()
    elif tab == "images":
      files = files.filter(File.mime_type.like("image/%"))
      e.images = files.all()

  return render_template("social/user.html", **e)
