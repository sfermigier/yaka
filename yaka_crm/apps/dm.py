"""Document Management module for Yaka.

Don't worry, it's just a prototype to test the architecture.
Will be refactored later and included in the ESN.
"""
import traceback

import os
import hashlib

from flask import Blueprint, render_template, redirect, request,\
  make_response, flash, abort, json
import re

from sqlalchemy.types import UnicodeText, LargeBinary, Integer, Text

from ..extensions import db
from ..core.entities import Entity, Column
from ..core.frontend import add_to_recent_items

from ..services.conversion import converter, ConversionError
from ..services.audit import AuditEntry
from ..services.image import resize


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


# TODO: rename to "Document" ? Only one class or several?
class File(Entity):
  __tablename__ = 'file'

  base_url = "/dm"

  name = Column(UnicodeText, nullable=False, info=searchable)
  description = Column(UnicodeText, default=u"", info=searchable)
  folder_id = Column(Integer)

  data = Column(LargeBinary)
  digest = Column(Text)
  # TODO: normalize mime type?
  mime_type = Column(UnicodeText, nullable=False)
  size = Column(Integer)

  tags = Column(UnicodeText, default=u"")

  #: for full-text search
  text = Column(UnicodeText, default=u"", info=searchable)

  #: for "view as PDF"
  pdf = Column(LargeBinary)

  #: preview image
  preview = Column(LargeBinary)

  def __init__(self, name, data, mime_type):
    Entity.__init__(self)

    self.data = data
    self.digest = hashlib.md5(data).hexdigest()
    self.size = len(data)
    self.name = name
    self.mime_type = mime_type

    # TODO: This should be asynchronous
    try:
      self.pdf = converter.to_pdf(self.digest, self.data, self.mime_type)
    except ConversionError:
      self.text = u""
      traceback.print_exc()

    try:
      self.text = converter.to_text(self.digest, self.data, self.mime_type)
    except ConversionError:
      self.text = u""
      traceback.print_exc()

  @property
  def icon(self):
    # XXX Hack for now
    # TODO: use the mimetypes Python library to map mime type to icon
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
  if isinstance(fd.filename, unicode):
    name = fd.filename
  else:
    name = unicode(fd.filename, errors='ignore')
  f = File(name, fd.read(), fd.content_type)

  db.session.add(f)
  return f


@dm.route("/<int:file_id>")
def view(file_id):
  f = get_file(file_id)

  if f.mime_type.startswith("image/"):
    add_to_recent_items(f, "image")
  else:
    add_to_recent_items(f, "document")

  bc = [dict(path=ROOT, label="DM Home")]
  bc.append(dict(label=f.name))

  # FIXME: too intimate
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

  attach = request.args.get('attach')
  f = get_file(file_id)

  if attach:
    response = make_response(f.data)
    response.headers['content-type'] = f.mime_type
    response.headers['content-disposition'] = "attachment"

  else:
    # Note: we omit text/html for security reasons.
    if match(f.mime_type, ("text/plain", "application/pdf", "image/*")):
      response = make_response(f.data)
      response.headers['content-type'] = f.mime_type
    else:
      response = make_response(f.data)
      response.headers['content-type'] = f.mime_type

  return response


@dm.route("/<int:file_id>/preview")
def preview(file_id):
  """Returns a preview (image) for the file given by its id."""

  f = get_file(file_id)
  size = int(request.args.get("s", 0))
  page = int(request.args.get("page", 0))
  data = converter.to_image(f.digest, f.data, f.mime_type, page, size)
  #if size:
  #  data = resize(data, size)

  response = make_response(data)
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

def match(mime_type, patterns):
  for pat in patterns:
    pat = pat.replace("*", r"\w*")
    if re.match(pat, mime_type):
      return True
  return False
