"""
Conversion service.

Hardcoded to manage only conversion to PDF, to text and to image series.

Assumes poppler-utils is installed and CloudOOo is running (needs LibreOffice too).
"""

# Yay, no dependencies on Yaka!

import glob
import hashlib
import random
from abc import ABCMeta, abstractmethod
from magic import Magic
import os
import subprocess
import time
from base64 import encodestring, decodestring
from xmlrpclib import ServerProxy
import mimetypes
import re


mime_sniffer = Magic(mime=True)
encoding_sniffer = Magic(mime_encoding=True)


class ConversionError(Exception):
  pass


class Converter(object):
  def __init__(self):
    self.handlers = []
    self.cache = {}
    if not os.path.exists("data"):
      os.mkdir("data")

  def register_handler(self, handler):
    self.handlers.append(handler)

  def put(self, file, mime_type=""):
    """
    Assume file is a string for now.
    """
    if not os.path.exists("data"):
      os.mkdir("data")
    if not mime_type:
      mime_type = mime_sniffer.from_buffer(file)
    key = hashlib.md5(file + "::" + mime_type).hexdigest()
    fd = open("data/%s.blob" % key, "wcb")
    fd.write(file)
    fd.flush()

    fd = open("data/%s.mime" % key, "wcb")
    fd.write(mime_type)
    fd.flush()

    return key

  def get(self, key):
    """Gets the result of a conversion given a token."""

    # Special case
    if key == "empty":
      return u""

    fn = "data/%s.blob" % key
    mime_type = mime_sniffer.from_file(fn)
    encoding = encoding_sniffer.from_file(fn)

    data = open(fn).read()
    if mime_type != "text/plain":
      return data
    else:
      return unicode(data, encoding)
      #return unicode(data, encoding, errors='ignore')

  def to_pdf(self, key):
    """Converts a file to a PDF document."""
    if key+":pdf" in self.cache and os.path.exists(key+":pdf"):
      return self.cache[key+":pdf"]

    mime_type = open("data/%s.mime" % key).read()
    for handler in self.handlers:
      if handler.accept(mime_type, "application/pdf"):
        new_key = handler.convert(key)
        self.cache[key+":pdf"] = new_key
        return new_key
    raise ConversionError("No handler found to convert from %s to PDF" % mime_type)

  def to_text(self, key):
    """Converts a file to plain text.

    Useful for full text indexing. Returns an unicode string.
    """
    if key+":txt" in self.cache and os.path.exists(key+":txt"):
      return self.cache[key+":txt"]

    mime_type = open("data/%s.mime" % key).read()

    # Special case, for now (XXX).
    if mime_type.startswith("image/"):
      return "empty"

    # Direct conversion possible
    for handler in self.handlers:
      if handler.accept(mime_type, "text/plain"):
        new_key = handler.convert(key)
        self.cache[key+":txt"] = new_key
        return new_key

    # Use PDF as a pivot format
    key = self.to_pdf(key)
    for handler in self.handlers:
      if handler.accept("application/pdf", "text/plain"):
        new_key = handler.convert(key)
        self.cache[key+":txt"] = new_key
        return new_key

    raise ConversionError()

  def to_images(self, key, size=500):
    """Converts a file to a list of images.
    Returns a list of tokens.
    """
    if key+":img" in self.cache and os.path.exists(key+":img"):
      return self.cache[key+":img"]

    mime_type = open("data/%s.mime" % key).read()

    # Is there a handler for direct conversion?
    for handler in self.handlers:
      if handler.accept(mime_type, "image/jpeg"):
        new_keys = handler.convert(key, size=size)
        self.cache[key+":img"] = new_keys
        return new_keys

    ## Indirect conversion via PDF
    key = self.to_pdf(key)
    for handler in self.handlers:
      if handler.accept("application/pdf", "image/jpeg"):
        new_keys = handler.convert(key, size=size)
        self.cache[key+":img"] = new_keys
        return new_keys

    # Fail
    raise ConversionError()

  def get_metadata(self, file, mime_type):
    """Gets a dictionary representing the metadata embedded in the given file."""
    pass


class Handler(object):
  __metaclass__ = ABCMeta

  accepts_mime_types = []
  produces_mime_types = []

  def accept(self, source_mime_type, target_mime_type):
    """Generic matcher based on patterns."""

    match_source = False
    match_target = False

    for pat in self.accepts_mime_types:
      if re.match("^%s$" % pat, source_mime_type):
        match_source = True
        break

    for pat in self.produces_mime_types:
      if re.match("^%s$" % pat, target_mime_type):
        match_target = True
        break

    return match_source and match_target

  @abstractmethod
  def convert(self, key, **kw):
    pass


class PdfToTextHandler(Handler):
  accepts_mime_types = ['application/pdf']
  produces_mime_types = ['text/plain']

  # TODO: add Unicode encoding sniffing
  def convert(self, key):
    in_fn = "data/%s.blob" % key
    tmp_out_fn = "data/%s-%s.blob" % (time.time(), random.randint(0, 1000000))

    assert os.path.exists(in_fn)
    subprocess.check_call(['pdftotext', in_fn, tmp_out_fn])

    new_key = hashlib.md5(open(tmp_out_fn).read()).hexdigest()
    os.rename(tmp_out_fn, "data/%s.blob" % new_key)
    return new_key


class ImageMagickHandler(Handler):
  accepts_mime_types = ['image/.*']
  produces_mime_types = ['application/pdf']

  def convert(self, key):
    in_fn = "data/%s.blob" % key
    tmp_out_fn = "data/%s-%s.blob" % (time.time(), random.randint(0, 1000000))

    assert os.path.exists(in_fn)
    subprocess.check_call(['convert', in_fn, "pdf:" + tmp_out_fn])
    new_key = hashlib.md5(open(tmp_out_fn).read()).hexdigest()
    os.rename(tmp_out_fn, "data/%s.blob" % new_key)
    return new_key


class PdfToPpmHandler(Handler):
  accepts_mime_types = ['application/pdf']
  produces_mime_types = ['image/jpeg']

  def convert(self, key, size=500):
    in_fn = "data/%s.blob" % key
    tmp_out_fn = "data/%s-%s.tmp" % (time.time(), random.randint(0, 1000000))

    subprocess.check_call(['pdftoppm', '-scale-to', str(size), '-jpeg', in_fn, tmp_out_fn])

    new_keys = []
    for fn in glob.glob("%s-*.jpg" % tmp_out_fn):
      new_key = hashlib.md5(open(fn).read()).hexdigest()
      os.rename(fn, "data/%s.blob" % new_key)
      new_keys.append(new_key)

    return new_keys


class CloudoooPdfHandler(Handler):
  """Handles conversion from OOo to PDF.

  Highly inefficient since file are serialized in base64 over HTTP.
  """

  accepts_mime_types = [r'application/.*']
  produces_mime_types = ['application/pdf']

  # Hardcoded for now
  SERVER_URL = "http://localhost:8011"

  pivot_format_map = {
    "doc": "odt",
    "docx": "odt",
    "xls": "ods",
    "xlsx": "ods",
    "ppt": "odp",
    "pptx": "odp",
    }

  def convert(self, key):
    in_fn = "data/%s.blob" % key
    in_mime_type = open("data/%s.mime" % key).read()
    file_extension = mimetypes.guess_extension(in_mime_type).strip(".")

    data = encodestring(open(in_fn).read())
    proxy = ServerProxy(self.SERVER_URL, allow_none=True)

    if in_mime_type.startswith("application/vnd.oasis.opendocument"):
      data = proxy.convertFile(data, file_extension, 'pdf')
    else:
      pivot_format = self.pivot_format_map[file_extension]
      data = proxy.convertFile(data, file_extension, pivot_format)
      data = proxy.convertFile(data, pivot_format, 'pdf')

    converted = decodestring(data)
    new_key = hashlib.md5(converted).hexdigest()
    fd = open("data/%s.blob" % new_key, "wcb")
    fd.write(converted)
    fd.close()
    return new_key


# Singleton, yuck!
converter = Converter()
converter.register_handler(PdfToTextHandler())
converter.register_handler(PdfToPpmHandler())
converter.register_handler(CloudoooPdfHandler())
converter.register_handler(ImageMagickHandler())

