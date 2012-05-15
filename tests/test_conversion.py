# Don't remove
import fix_path

import shutil
from os.path import join, dirname

from unittest import TestCase
from nose.tools import eq_
from magic import Magic

from yaka_crm.services.conversion import converter


BASEDIR = join(dirname(__file__), "dummy_files")

mime_sniffer = Magic(mime=True)
encoding_sniffer = Magic(mime_encoding=True)


class Test(TestCase):

  @classmethod
  def tearDownClass(cls):
    shutil.rmtree("data")

  # To text
  def test_pdf_to_text(self):
    blob = open(join(BASEDIR, "onepage.pdf")).read()
    key = converter.put(blob, "application/pdf")
    new_key = converter.to_text(key)
    new_blob = converter.get(new_key)
    eq_("text/plain", mime_sniffer.from_buffer(new_blob.encode("latin1")))
    eq_("iso-8859-1", encoding_sniffer.from_buffer(new_blob.encode("latin1")))

  def test_word_to_text(self):
    blob = open(join(BASEDIR, "test.doc")).read()
    key = converter.put(blob, "application/msword")
    new_key = converter.to_text(key)
    new_blob = converter.get(new_key)
    eq_("text/plain", mime_sniffer.from_buffer(new_blob.encode("latin1")))
    eq_("iso-8859-1", encoding_sniffer.from_buffer(new_blob.encode("latin1")))

  def test_wordx_to_text(self):
    blob = open(join(BASEDIR, "test.docx")).read()
    key = converter.put(blob, "application/msword")
    new_key = converter.to_text(key)
    new_blob = converter.get(new_key)
    eq_("text/plain", mime_sniffer.from_buffer(new_blob.encode("latin1")))
    eq_("iso-8859-1", encoding_sniffer.from_buffer(new_blob.encode("latin1")))

  def test_excel_to_text(self):
    blob = open(join(BASEDIR, "test.xls")).read()
    key = converter.put(blob, "application/excel")
    new_key = converter.to_text(key)
    new_blob = converter.get(new_key)
    eq_("text/plain", mime_sniffer.from_buffer(new_blob.encode("latin1")))
    eq_("us-ascii", encoding_sniffer.from_buffer(new_blob.encode("latin1")))

  # To PDF
  def test_odt_to_pdf(self):
    blob = open(join(BASEDIR, "test.odt")).read()
    key = converter.put(blob, "application/vnd.oasis.opendocument.text")
    new_key = converter.to_pdf(key)
    new_blob = converter.get(new_key)
    eq_("application/pdf", mime_sniffer.from_buffer(new_blob))

  def test_word_to_pdf(self):
    blob = open(join(BASEDIR, "test.doc")).read()
    key = converter.put(blob, "application/msword")
    new_key = converter.to_pdf(key)
    new_blob = converter.get(new_key)
    eq_("application/pdf", mime_sniffer.from_buffer(new_blob))

  def test_image_to_pdf(self):
    blob = open(join(BASEDIR, "picture.jpg")).read()
    key = converter.put(blob, "image/jpeg")
    new_key = converter.to_pdf(key)
    new_blob = converter.get(new_key)
    eq_("application/pdf", mime_sniffer.from_buffer(new_blob))

  # To images
  def test_pdf_to_images(self):
    blob = open(join(BASEDIR, "onepage.pdf")).read()
    key = converter.put(blob, "application/pdf")
    new_keys = converter.to_images(key, 500)
    new_blob = converter.get(new_keys[0])
    eq_("image/jpeg", mime_sniffer.from_buffer(new_blob))

  def test_word_to_images(self):
    blob = open(join(BASEDIR, "test.doc")).read()
    key = converter.put(blob, "application/msword")
    new_key = converter.to_images(key, 1000)
    new_blob = converter.get(new_key[0])
    eq_("image/jpeg", mime_sniffer.from_buffer(new_blob))

