"""Document Management module for Yaka.

Don't worry, it's just a prototype. Will be refactored later and included into the ESN.
"""

from flask.helpers import json

import os

from flask import Blueprint, render_template, redirect, request,\
  make_response, flash, abort

from sqlalchemy.types import UnicodeText, LargeBinary, Integer

from .core.entities import Entity, Column
from .extensions import db
from .converter import convert
from yaka_crm.audit import AuditEntry


ROOT = "/dm/"
dm = Blueprint("dm", __name__, url_prefix="/dm")

searchable = dict(searchable=True)

#
# Entities and forms
#
class Folder(Entity):
  __tablename__ = 'folder'

  name = Column(UnicodeText, nullable=False, info=searchable)
  parent_id = Column(Integer)


class File(Entity):
  __tablename__ = 'file'

  base_url = "/dm"

  name = Column(UnicodeText, nullable=False, info=searchable)
  description = Column(UnicodeText, default=u"", info=searchable)
  folder_id = Column(Integer)

  data = Column(LargeBinary)
  mime_type = Column(UnicodeText, nullable=False)
  size = Column(Integer)

  tags = Column(UnicodeText, default=u"")

  #: for full-text search
  text = Column(UnicodeText, default=u"", info=searchable)

  #: for "view as PDF"
  pdf = Column(LargeBinary)

  #: preview image
  preview = Column(LargeBinary)

  @property
  def icon(self):
    # XXX Hack for now
    if not "." in self.name:
      return '/static/fileicons/bin.png'

    #noinspection PyUnresolvedReferences
    suffix = self.name.split(".")[-1]
    if os.path.exists("yaka_crm/static/fileicons/%s.png" % suffix):
      return '/static/fileicons/%s.png' % suffix
    else:
      return '/static/fileicons/bin.png'


#
# Controllers
#
@dm.route("/")
def home():
  bc = [dict(path="/dm/", label="DM Home")]
  files = list(File.query.all())
  return render_template("dm/home.html", breadcrumbs=bc, files=files)


@dm.route("/", methods=['POST'])
def upload_new():
  fds = request.files.getlist('file')
  if len(fds) > 1:
    for fd in fds:
      create_file(fd)
    f = None
  else:
    f = create_file(fds[0])
  db.session.commit()

  flash("%d files successfully uploaded" % len(fds), "success")

  if len(fds) == 1:
    return redirect(ROOT + "%d" % f.uid)
  else:
    return redirect(ROOT)


def create_file(fd):
  f = File()
  if isinstance(fd.filename, unicode):
    f.name = fd.filename
  else:
    f.name = unicode(fd.filename, errors='ignore')
  f.data = fd.read()
  f.mime_type = fd.content_type
  f.size = fd.content_length
  db.session.add(f)
  convert(f)
  return f


@dm.route("/<int:file_id>")
def view(file_id):
  f = get_file(file_id)

  bc = [dict(path=ROOT, label="DM Home")]
  bc.append(dict(label=f.name))

  audit_entries = AuditEntry.query.filter(AuditEntry.entity_id == f.uid).all()
  return render_template("dm/file.html", file=f, audit_entries=audit_entries, breadcrumbs=bc)


@dm.route("/<int:file_id>/delete", methods=['POST'])
def delete(file_id):
  f = get_file(file_id)

  db.session.delete(f)
  db.session.commit()

  flash("File successfully deleted.", "success")

  return redirect(ROOT)


@dm.route("/<int:file_id>", methods=['POST'])
def upload_new_version(file_id):
  f = get_file(file_id)

  fd = request.files['file']
  f.name = unicode(fd.filename, errors='ignore')
  f.data = fd.read()
  f.mime_type = fd.content_type
  f.size = fd.content_length

  db.session.commit()

  return redirect(ROOT + "%d" % f.uid)


@dm.route("/<int:file_id>/download")
def download(file_id):
  """Download the file's content."""

  f = get_file(file_id)

  attach = request.args.get('attach')
  response = make_response(f.data)
  response.headers['content-type'] = f.mime_type
  if attach:
    response.headers['content-disposition'] = "attachment"

  return response


@dm.route("/<int:file_id>/preview")
def preview(file_id):
  """Returns a preview (image) for the file given by its id."""

  f = get_file(file_id)
  response = make_response(f.preview)
  response.headers['content-type'] = "image/jpeg"

  return response


@dm.route("/upload")
def upload_form():
  bc = [dict(path=ROOT, label="DM Home")]
  return render_template("dm/upload.html", breadcrumbs=bc)


@dm.route("/upload", methods=['POST'])
def upload_post():
  fds = request.files.getlist('file')
  print fds
  result = []
  for fd in fds:
    result.append(dict(name=fd.filename))

  resp = make_response(json.dumps(result))
  resp.headers['Content-Type'] = "application/json"
  return resp


#
# Utils
#
def get_file(uid):
  f = File.query.get(uid)
  if not f:
    abort(404)
  return f
