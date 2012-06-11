"""File / Document Management module for Yaka.

Don't worry, it's just a prototype to test the architecture.
Will be refactored later and included in the ESN.
"""

import StringIO
import traceback
from urllib import quote
from zipfile import ZipFile
from guess_language.guess_language import guessLanguageName
import os
import hashlib
import re

from flask import Blueprint, render_template, redirect, request,\
  make_response, flash, abort, json, g, current_app

from flaskext.mail import Message

from sqlalchemy.types import UnicodeText, LargeBinary, Integer, Text

import whoosh.fields

from yaka.extensions import db, mail

from yaka.core.entities import Entity, Column
from yaka.core.frontend import add_to_recent_items
from yaka.core.signals import activity

from yaka.services.conversion import converter, ConversionError
from yaka.services.audit import AuditEntry
from yaka.services.image import resize


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
  mime_type = Column(Text, nullable=False)
  language = Column(Text)
  size = Column(Integer)
  page_num = Column(Integer, default=1)

  #: Comma-separated list for now...
  tags = Column(UnicodeText, default=u"")

  #: for full-text search
  text = Column(UnicodeText, default=u"", info=searchable)

  #: for "view as PDF"
  pdf = Column(LargeBinary, info=dict(auditable=False))

  #: preview image
  preview = Column(LargeBinary, info=dict(auditable=False))

  extra_metadata_json = Column(UnicodeText, info=dict(auditable=False))

  # FIXME: hardwired dependency
  whoosh_schema = whoosh.fields.Schema(
    uid=whoosh.fields.ID(stored=True, unique=True),

    created_at=whoosh.fields.DATETIME(stored=True),
    updated_at=whoosh.fields.DATETIME(stored=True),
    creator_id=whoosh.fields.ID(stored=True),
    creator=whoosh.fields.ID(stored=True),
    owner_id=whoosh.fields.ID(stored=True),
    owner=whoosh.fields.ID(stored=True),

    name=whoosh.fields.TEXT(stored=True),
    description=whoosh.fields.TEXT(stored=True),
    text=whoosh.fields.TEXT(stored=True),

    mime_type=whoosh.fields.ID(stored=True),
    language=whoosh.fields.ID(stored=True),
    size=whoosh.fields.NUMERIC(stored=True),
    tags=whoosh.fields.KEYWORD(stored=True, commas=True),
  )

  def __init__(self, name, data, mime_type):
    Entity.__init__(self)

    self.name = name
    self._update(data, mime_type)

  def _update(self, data, mime_type=None):
    new_digest = hashlib.md5(data).hexdigest()
    if new_digest == self.digest:
      return

    self.digest = new_digest
    self.data = data
    self.size = len(data)
    if mime_type:
      self.mime_type = mime_type
    # TODO Else: use a sniffer

    # TODO: This should be asynchronous
    if self.mime_type != "application/pdf":
      try:
        self.pdf = converter.to_pdf(self.digest, self.data, self.mime_type)
      except ConversionError:
        traceback.print_exc()
    else:
      self.pdf = self.data

    try:
      self.text = converter.to_text(self.digest, self.data, self.mime_type)
    except ConversionError:
      self.text = u""
      traceback.print_exc()

    try:
      self.extra_metadata = converter.get_metadata(self.digest, self.data, self.mime_type)
    except ConversionError:
      self.extra_metadata = {}
      traceback.print_exc()

    if self.text:
      self.language = guessLanguageName(self.text)

    self.page_num = self.extra_metadata.get("PDF:Pages", 1)

  def get_extra_metadata(self):
    if not hasattr(self, '_extra_metadata'):
      self._extra_metadata = json.loads(self.extra_metadata_json)
    return self._extra_metadata

  def set_extra_metadata(self, extra_metadata):
    self._extra_metadata = extra_metadata
    self.extra_metadata_json = json.dumps(extra_metadata)

  extra_metadata = property(get_extra_metadata, set_extra_metadata)

  @property
  def icon(self):
    # XXX Hack for now
    # TODO: use the mimetypes Python library to map mime type to icon
    if not "." in self.name:
      return '/static/fileicons/bin.png'

    #noinspection PyUnresolvedReferences
    suffix = self.name.split(".")[-1]
    if os.path.exists("yaka/static/fileicons/%s.png" % suffix):
      return '/static/fileicons/%s.png' % suffix
    else:
      return '/static/fileicons/bin.png'


#
# Controllers
#
@dm.route("/")
def home():
  bc = [dict(path="/", label="Home"), dict(path="/dm/", label="DM")]
  files = list(File.query.all())
  title = "All your files"
  return render_template("dm/home.html", title=title, breadcrumbs=bc, files=files)


@dm.route("/tag")
def tag():
  tag = request.args.get("tag")
  if not tag:
    return redirect("/dm/")

  bc = [dict(path="/", label="Home"), dict(path="/dm/", label="DM")]
  bc += [dict(path=request.path, label="Filter by tag")]
  files = File.query.filter(File.tags.like("%" + tag + "%"))
  files = list(files.all())
  files = [f for f in files if tag in f.tags.split(",")]
  title = "Files filtered by tag: %s" % tag
  return render_template("dm/home.html", title=title, breadcrumbs=bc, files=files)


@dm.route("/", methods=['POST'])
def home_post():
  action = request.form.get("action")

  if action == 'upload':
    return upload_new()

  if action == 'download':
    return download_multiple()
  elif action == 'delete':
    return delete_multiple()
  else:
    return home()


def upload_new():
  fds = request.files.getlist('file')
  if len(fds) > 1:
    for fd in fds:
      create_file(fd)
    f = None
    flash("%d new files successfully uploaded" % len(fds), "success")
  else:
    f = create_file(fds[0])
    flash("One new file successfully uploaded", "success")

  db.session.commit()

  if len(fds) == 1:
    return redirect(ROOT + "%d" % f.uid)
  else:
    return redirect(ROOT)


def download_multiple():
  selected_ids = map(int, request.form.getlist("file-selected"))
  files = map(get_file, selected_ids)

  zip_fd = StringIO.StringIO()
  with ZipFile(zip_fd, "w") as zipfile:
    for f in files:
      zipfile.writestr(f.name, f.data)

  response = make_response(zip_fd.getvalue())
  response.headers['content-type'] = "application/zip"
  return response


def delete_multiple():
  selected_ids = map(int, request.form.getlist("file-selected"))
  files = map(get_file, selected_ids)

  for f in files:
    db.session.delete(f)
    self = current_app._get_current_object()
    activity.send(self, actor=g.user, verb="delete", object=f)

  db.session.commit()
  flash("%d file(s) successfully deleted." % len(files), "success")

  return redirect(ROOT)


def create_file(fs):
  if isinstance(fs.filename, unicode):
    name = fs.filename
  else:
    name = unicode(fs.filename, errors='ignore')
  f = File(name, fs.read(), fs.content_type)

  db.session.add(f)
  self = current_app._get_current_object()
  activity.send(self, actor=g.user, verb="post", object=f)

  return f


@dm.route("/<int:file_id>")
def view(file_id):
  f = get_file(file_id)

  if f.mime_type.startswith("image/"):
    add_to_recent_items(f, "image")
  else:
    add_to_recent_items(f, "document")

  bc = [dict(path="/", label="Home"), dict(path="/dm/", label="DM")]
  bc.append(dict(label=f.name))

  # FIXME: too intimate
  audit_entries = AuditEntry.query.filter(AuditEntry.entity_id == f.uid).all()
  return render_template("dm/file.html", file=f, audit_entries=audit_entries, breadcrumbs=bc)


@dm.route("/<int:file_id>/delete", methods=['POST'])
def delete_file(file_id):
  f = get_file(file_id)

  db.session.delete(f)
  db.session.commit()

  flash("File successfully deleted.", "success")

  return redirect(ROOT)


@dm.route("/<int:file_id>/upload", methods=['POST'])
def upload_new_version(file_id):
  f = get_file(file_id)
  fd = request.files['file']

  f._update(fd.read(), fd.content_type)
  self = current_app._get_current_object()
  activity.send(self, actor=g.user, verb="update", object=f)
  db.session.commit()

  flash("New version successfully uploaded", "success")
  return redirect(ROOT + "%d" % f.uid)


@dm.route("/<int:file_id>/tag", methods=['POST'])
def tag_post(file_id):
  f = get_file(file_id)
  tags = request.form.get("tags")

  f.tags = tags
  self = current_app._get_current_object()
  activity.send(self, actor=g.user, verb="tag", object=f)

  db.session.commit()

  flash("Tags successfully successfully updated", "success")

  return redirect(ROOT + "%d" % f.uid)


@dm.route("/<int:file_id>/download")
def download(file_id):
  """Download the file's content."""

  attach = request.args.get('attach')
  f = get_file(file_id)

  if attach:
    response = make_response(f.data)
    response.headers['content-type'] = f.mime_type
    enc_fn = quote(f.name)
    response.headers['content-disposition'] = 'attachment;filename="%s"' % enc_fn

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
  size = int(request.args.get("size", 0))

  # Just in case
  if size > 1000:
    size = 1000

  if f.mime_type.startswith("image/"):
    image = f.data
    if size:
      image = resize(image, size)
  else:
    page = int(request.args.get("page", 0))
    image = converter.to_image(f.digest, f.data, f.mime_type, page, size)

  response = make_response(image)
  response.headers['content-type'] = "image/jpeg"

  return response


@dm.route("/upload")
def upload_form():
  bc = [dict(path=ROOT, label="DM Home")]
  return render_template("dm/upload.html", breadcrumbs=bc)


@dm.route("/<int:file_id>/send", methods=['POST'])
def send(file_id):
  recipient = request.form.get("recipient")
  f = get_file(file_id)

  msg = Message("File sent from Yaka")
  msg.sender = g.user.email
  msg.recipients = [recipient]
  msg.body = """The following file (%s) might be interesting to you.

  """ % f.name

  msg.attach(f.name, f.mime_type, f.data)

  mail.send(msg)
  flash("Email successfully sent", "success")

  return redirect(ROOT + "%d" % f.uid)


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
