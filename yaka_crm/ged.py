"""GED (i.e. document management module) for Yaka.

Don't worry, it's just a prototype. Will be refactored later.
"""
import os

from flask import Blueprint, render_template, redirect, request, make_response

from sqlalchemy.types import UnicodeText, LargeBinary, Integer

from yaka_crm.core.entities import Entity, Column
from yaka_crm.extensions import db


ged = Blueprint("ged", __name__, url_prefix="/ged")

#
# Entities and forms
#
class Folder(Entity):
  __tablename__ = 'folder'

  name = Column(UnicodeText)
  parent_id = Column(Integer)


class File(Entity):
  __tablename__ = 'file'

  base_url = "/ged"

  name = Column(UnicodeText, nullable=False, searchable=True)
  description = Column(UnicodeText, default=u"", searchable=True)
  folder_id = Column(Integer)

  data = Column(LargeBinary)
  mime_type = Column(UnicodeText, nullable=False)
  size = Column(Integer)

  text = Column(UnicodeText, default=u"", searchable=True)
  preview = Column(LargeBinary)

  @property
  def icon(self):
    # XXX Hack for now
    suffix = self.name.split(".")[-1]
    return '/static/fileicons/%s.png' % suffix


#
# Controllers
#

@ged.route("/")
def home():
  bc = [dict(path="/ged/", label="GED Home")]
  files = list(File.query.all())
  return render_template("ged/home.html", breadcrumbs=bc, files=files)


@ged.route("/", methods=['POST'])
def upload_new():
  fd = request.files['file']
  f = File()
  f.name = unicode(fd.filename, errors='ignore')
  f.data = fd.read()
  f.mime_type = fd.content_type
  f.size = fd.content_length

  db.session.add(f)
  db.session.commit()
  return redirect("/ged/%d" % f.uid)


@ged.route("/<int:file_id>")
def view(file_id):
  bc = [dict(path="/ged/", label="GED Home")]
  f = File.query.get(file_id)
  bc.append(dict(label=f.name))

  return render_template("ged/file.html", file=f, breadcrumbs=bc)


@ged.route("/<int:file_id>/delete")
def delete(file_id):
  f = File.query.get(file_id)
  db.session.delete(f)
  db.session.commit()
  return redirect("/ged/")


@ged.route("/<int:file_id>", methods=['POST'])
def upload_new_version(file_id):
  fd = request.files['file']
  f = File.query.get(file_id)
  f.name = unicode(fd.filename, errors='ignore')
  f.data = fd.read()
  f.mime_type = fd.content_type
  f.size = fd.content_length

  db.session.commit()
  return redirect("/ged/%d" % f.uid)


@ged.route("/<int:file_id>/download")
def download(file_id):
  """Returns a preview (image) for the file given by its id."""

  attach = request.args.get('attach')
  f = File.query.get(file_id)
  response = make_response(f.data)
  response.headers['content-type'] = f.mime_type
  if attach:
    response.headers['content-disposition'] = "attachment"
  return response


@ged.route("/<int:file_id>/preview")
def preview(file_id):
  """Returns a preview (image) for the file given by its id."""

  f = File.query.get(file_id)
  response = make_response(f.preview)
  response.headers['content-type'] = "image/jpeg"
  return response


# TODO: make asynchronous
def convert(f):
  import tempfile, subprocess

  tmp_in_fn = tempfile.mktemp()
  tmp_in_fd = open(tmp_in_fn, 'wc')
  tmp_in_fd.write(f.data)
  tmp_in_fd.close()

  tmp_out_fn = tempfile.mktemp()

  if f.mime_type == 'application/pdf':
    subprocess.check_output(['pdftotext', tmp_in_fn, tmp_out_fn])
    text = open(tmp_out_fn).read()
    print text
    f.text = unicode(text, 'utf8', errors='ignore')
    os.unlink(tmp_out_fn)

    subprocess.check_output(['pdftoppm', '-singlefile', '-jpeg', '-l', '1', tmp_in_fn, tmp_out_fn])
    preview = open(tmp_out_fn + '.jpg').read()
    f.preview = preview
    print tmp_out_fn + '.jpg'
    #os.unlink(tmp_out_fn)

  os.unlink(tmp_in_fn)
