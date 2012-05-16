"""
Conversion service.

Hardcoded to manage only conversion to PDF, to text and to image series.

Includes result caching (on filesystem).

Assumes poppler-utils and LibreOffice are installed.
"""

# Yay, no dependencies on Yaka!

import glob
import hashlib
import shutil
from tempfile import mktemp
from abc import ABCMeta, abstractmethod
from magic import Magic
import os
import subprocess
from base64 import encodestring, decodestring
from xmlrpclib import ServerProxy
import mimetypes
import re


TMP_DIR = "tmp"
CACHE_DIR = "cache"

mime_sniffer = Magic(mime=True)
encoding_sniffer = Magic(mime_encoding=True)


class ConversionError(Exception):
  pass


class Cache(object):

  def get(self, key):
    if os.path.exists("cache/%s.blob" % key):
      value = open("cache/%s.blob" % key).read()
      if key.startswith("txt:"):
        value = unicode(value, encoding="utf8")
      return value
    else:
      return None

  def set(self, key, value):
    if not os.path.exists(CACHE_DIR):
      os.mkdir(CACHE_DIR)
    fd = open("cache/%s.blob" % key, "wbc")
    if key.startswith("txt:"):
      fd.write(value.encode("utf8"))
    else:
      fd.write(value)
    fd.close()

  __setitem__ = set

  def clear(self):
    pass


class Converter(object):
  def __init__(self):
    self.handlers = []
    self.cache = Cache()
    if not os.path.exists(TMP_DIR):
      os.mkdir(TMP_DIR)
    if not os.path.exists(CACHE_DIR):
      os.mkdir(CACHE_DIR)

  def clear(self):
    self.cache.clear()
    shutil.rmtree(TMP_DIR)
    shutil.rmtree(CACHE_DIR)

  def register_handler(self, handler):
    self.handlers.append(handler)

  def to_pdf(self, digest, blob, mime_type):
    cache_key = "pdf:" + digest

    pdf = self.cache.get(cache_key)
    if pdf:
      return pdf

    for handler in self.handlers:
      if handler.accept(mime_type, "application/pdf"):
        pdf = handler.convert(blob)
        self.cache[cache_key] = pdf
        return pdf
    raise ConversionError("No handler found to convert from %s to PDF" % mime_type)

  def to_text(self, digest, blob, mime_type):
    """Converts a file to plain text.

    Useful for full-text indexing. Returns an unicode string.
    """
    # Special case, for now (XXX).
    if mime_type.startswith("image/"):
      return u""

    cache_key = "txt:" + digest

    text = self.cache.get(cache_key)
    if text:
      return text

    # Direct conversion possible
    for handler in self.handlers:
      if handler.accept(mime_type, "text/plain"):
        text = handler.convert(blob)
        self.cache[cache_key] = text
        return text

    # Use PDF as a pivot format
    pdf = self.to_pdf(digest, blob, mime_type)
    for handler in self.handlers:
      if handler.accept("application/pdf", "text/plain"):
        text = handler.convert(pdf)
        self.cache[cache_key] = text
        return text

    raise ConversionError()

  def to_image(self, digest, blob, mime_type, index, size=500):
    """Converts a file to a list of images. Returns image at the given index.
    """
    # Special case, for now (XXX).
    if mime_type.startswith("image/"):
      return ""

    cache_key = "img:%s:%s:%s" % (index, size, digest)
    converted = self.cache.get(cache_key)
    if converted:
      return converted

    # Direct conversion possible
    for handler in self.handlers:
      if handler.accept(mime_type, "image/jpeg"):
        converted = handler.convert(blob, index=index, size=size)
        self.cache[cache_key] = converted
        return converted

    # Use PDF as a pivot format
    pdf = self.to_pdf(digest, blob, mime_type)
    for handler in self.handlers:
      if handler.accept("application/pdf", "image/jpeg"):
        converted = handler.convert(pdf)
        self.cache[cache_key] = converted
        return converted

    raise ConversionError()

  @staticmethod
  def digest(blob):
    assert type(blob) in (str, unicode)
    if type(blob) == str:
      digest = hashlib.md5(blob).hexdigest()
    else:
      digest = hashlib.md5(blob.encode("utf8")).hexdigest()
    return digest

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

  @staticmethod
  def make_temp_file(blob):
    if not os.path.exists(TMP_DIR):
      os.mkdir(TMP_DIR)
    in_fn = mktemp(dir=TMP_DIR)
    fd = open(in_fn, "wcb")
    fd.write(blob)
    fd.close()
    return in_fn


class PdfToTextHandler(Handler):
  accepts_mime_types = ['application/pdf']
  produces_mime_types = ['text/plain']

  def convert(self, blob):
    in_fn = self.make_temp_file(blob)
    out_fn = mktemp(dir=TMP_DIR)

    subprocess.check_call(['pdftotext', in_fn, out_fn])

    encoding = encoding_sniffer.from_file(out_fn)
    converted = open(out_fn).read()
    converted_unicode = unicode(converted, encoding, errors="ignore")

    return converted_unicode


class ImageMagickHandler(Handler):
  accepts_mime_types = ['image/.*']
  produces_mime_types = ['application/pdf']

  def convert(self, blob):
    in_fn = self.make_temp_file(blob)
    out_fn = mktemp(dir=TMP_DIR)

    subprocess.check_call(['convert', in_fn, "pdf:" + out_fn])

    converted = open(out_fn).read()
    return converted


class PdfToPpmHandler(Handler):
  accepts_mime_types = ['application/pdf']
  produces_mime_types = ['image/jpeg']

  def convert(self, blob, index=0, size=500):
    in_fn = self.make_temp_file(blob)
    out_fn = mktemp(dir=TMP_DIR)

    subprocess.check_call(['pdftoppm', '-jpeg', in_fn, out_fn])

    # TODO: resize images
    # TODO: cache
    l = glob.glob("%s-*.jpg" % out_fn)
    print l
    return open(l[index]).read()


class UnoconvPdfHandler(Handler):
  """Handles conversion from office documents (MS-Office, OOo) to PDF.

  Uses unoconv.
  """

  accepts_mime_types = [r'application/.*']
  produces_mime_types = ['application/pdf']

  def convert(self, blob):
    in_fn = self.make_temp_file(blob)
    out_fn = mktemp(suffix=".pdf", dir=TMP_DIR)

    # Hack for my Mac, FIXME later
    if os.path.exists("/Applications/LibreOffice.app/Contents/program/python"):
      cmd = ['/Applications/LibreOffice.app/Contents/program/python',
             '/usr/local/bin/unoconv', '-f', 'pdf', '-o', out_fn, in_fn]
    else:
      cmd = ['unoconv', '-f', 'pdf', '-o', out_fn, in_fn]
    subprocess.check_call(cmd)

    converted = open(out_fn).read()
    return converted


class CloudoooPdfHandler(Handler):
  """Handles conversion from OOo to PDF.

  Highly inefficient since file are serialized in base64 over HTTP.

  Deactivated because it's so hard to set up.
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
converter.register_handler(ImageMagickHandler())
converter.register_handler(UnoconvPdfHandler())
#converter.register_handler(CloudoooPdfHandler())
