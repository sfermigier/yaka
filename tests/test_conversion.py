# Don't remove
import fix_path

import shutil
from os.path import join, dirname

from unittest import TestCase
from nose.tools import eq_
from magic import Magic

from yaka_crm.services.conversion import converter


BASEDIR = join(dirname(__file__), "dummy_files")
BASEDIR2 = join(dirname(__file__), "dummy_files2")

mime_sniffer = Magic(mime=True)
encoding_sniffer = Magic(mime_encoding=True)


class Test(TestCase):

  @classmethod
  def tearDownClass(cls):
    shutil.rmtree("data")
    converter.clear_cache()

  def read_file(self, fn):
    try:
      return open(join(BASEDIR, fn)).read()
    except IOError, e:
      return open(join(BASEDIR2, fn)).read()


  # To text
  def test_pdf_to_text(self):
    blob = self.read_file("onepage.pdf")
    key = converter.put(blob, "application/pdf")
    new_key = converter.to_text(key)
    new_blob = converter.get(new_key)
    # FIXME later (!= behavious between my Mac and Travis)
    #eq_("text/plain", mime_sniffer.from_buffer(new_blob.encode("latin1")))
    #eq_("iso-8859-1", encoding_sniffer.from_buffer(new_blob.encode("latin1")))

  def test_word_to_text(self):
    blob = self.read_file("test.doc")
    key = converter.put(blob, "application/msword")
    new_key = converter.to_text(key)
    new_blob = converter.get(new_key)
    eq_("text/plain", mime_sniffer.from_buffer(new_blob.encode("latin1")))
    eq_("iso-8859-1", encoding_sniffer.from_buffer(new_blob.encode("latin1")))

  def test_wordx_to_text(self):
    blob = self.read_file("test.docx")
    key = converter.put(blob, "application/msword")
    new_key = converter.to_text(key)
    new_blob = converter.get(new_key)
    eq_("text/plain", mime_sniffer.from_buffer(new_blob.encode("latin1")))
    eq_("iso-8859-1", encoding_sniffer.from_buffer(new_blob.encode("latin1")))

  def test_excel_to_text(self):
    blob = self.read_file("test.xls")
    key = converter.put(blob, "application/excel")
    new_key = converter.to_text(key)
    new_blob = converter.get(new_key)
    eq_("text/plain", mime_sniffer.from_buffer(new_blob.encode("latin1")))
    eq_("us-ascii", encoding_sniffer.from_buffer(new_blob.encode("latin1")))

  # To PDF
  def test_odt_to_pdf(self):
    blob = self.read_file("test.odt")
    key = converter.put(blob, "application/vnd.oasis.opendocument.text")
    new_key = converter.to_pdf(key)
    new_blob = converter.get(new_key)
    eq_("application/pdf", mime_sniffer.from_buffer(new_blob))

  def test_word_to_pdf(self):
    blob = self.read_file("test.doc")
    key = converter.put(blob, "application/msword")
    new_key = converter.to_pdf(key)
    new_blob = converter.get(new_key)
    eq_("application/pdf", mime_sniffer.from_buffer(new_blob))

  def test_image_to_pdf(self):
    blob = self.read_file("picture.jpg")
    key = converter.put(blob, "image/jpeg")
    new_key = converter.to_pdf(key)
    new_blob = converter.get(new_key)
    eq_("application/pdf", mime_sniffer.from_buffer(new_blob))

  # To images
  def test_pdf_to_images(self):
    blob = self.read_file("onepage.pdf")
    key = converter.put(blob, "application/pdf")
    new_keys = converter.to_images(key, 500)
    new_blob = converter.get(new_keys[0])
    eq_("image/jpeg", mime_sniffer.from_buffer(new_blob))

  def test_word_to_images(self):
    blob = self.read_file("test.doc")
    key = converter.put(blob, "application/msword")
    new_key = converter.to_images(key, 1000)
    new_blob = converter.get(new_key[0])
    eq_("image/jpeg", mime_sniffer.from_buffer(new_blob))

