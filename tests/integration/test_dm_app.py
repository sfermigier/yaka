from base import IntegrationTestCase
import unittest

import os
import re
from io import StringIO

from nose.tools import eq_, ok_
from util import DataLoader

from yaka_crm import app, db
from config import TestConfig
from yaka_crm.apps.dm import match

import yaka_crm.views # Don't remove

from util import init_data

ROOT = "/dm/"


class TestViews(IntegrationTestCase):

  def create_app(self):
    app.config.from_object(TestConfig())
    app.config['UNSAFE'] = True
    return app

  def setUp(self):
    IntegrationTestCase.setUp(self)
    init_data(db)

  @staticmethod
  def uid_from_url(url):
    return int(url[len("http://localhost" + ROOT):])

  # Actual tests start here
  def test_home(self):
    response = self.client.get(ROOT)
    self.assert_200(response)

  def test_preview(self):
    loader = DataLoader(db)
    loader.load_users()
    loader.load_files()
    db.session.commit()

    response = self.client.get(ROOT)
    self.assert_200(response)

    data = response.data
    for m in re.findall(ROOT + "([0-9]+)", data):
      uid = int(m)

      response = self.client.get(ROOT + "%d/preview?size=500" % uid)
      self.assert_200(response)

  def test_upload_text(self):
    CONTENT = u'my file contents'
    NAME = u'hello world.txt'
    data = {
      'file': (StringIO(CONTENT), NAME, 'text/plain'),
      'action': 'upload',
    }
    response = self.client.post(ROOT, data=data)
    self.assert_302(response)

    uid = self.uid_from_url(response.location)

    response = self.client.get(ROOT + "%d" % uid)
    self.assert_200(response)

    response = self.client.get(ROOT)
    self.assert_200(response)
    ok_(NAME in response.data)
    ok_((ROOT + "%d" % uid) in response.data)

    response = self.client.get(ROOT + "%d/download" % uid)
    self.assert_200(response)
    eq_(response.headers['Content-Type'], 'text/plain')
    eq_(response.data, CONTENT)

    response = self.client.post(ROOT + "%d/delete" % uid)
    self.assert_302(response)

    response = self.client.get(ROOT + "%d" % uid)
    self.assert_404(response)

  def test_upload_pdf(self):
    NAME = u"onepage.pdf"
    data = {
      'file': (self.open_file(NAME), NAME, 'application/pdf'),
      'action': 'upload',
    }
    response = self.client.post(ROOT, data=data)
    self.assert_302(response)

    uid = self.uid_from_url(response.location)
    response = self.client.get(ROOT + "%d" % uid)
    self.assert_200(response)

    response = self.client.get(ROOT)
    self.assert_200(response)
    ok_(NAME in response.data)
    ok_((ROOT + "%d" % uid) in response.data)

    response = self.client.get(ROOT + "%d/download" % uid)
    self.assert_200(response)
    eq_(response.headers['Content-Type'], 'application/pdf')
    ok_(response.data)

    response = self.client.get(ROOT + "%d/preview?size=500" % uid)
    self.assert_200(response)
    eq_(response.headers['Content-Type'], 'image/jpeg')

    response = self.client.post(ROOT + "%d/delete" % uid)
    self.assert_302(response)

    response = self.client.get(ROOT + "%d" % uid)
    self.assert_404(response)

  @staticmethod
  def open_file(filename):
    path = os.path.join(os.path.dirname(__file__), "..", "dummy_files", filename)
    return open(path)


class TestUtils(unittest.TestCase):

  def test_match(self):
    ok_(match("text/plain", ["text/*"]))
    ok_(not match("text/plain", ["text/html"]))

    ok_(match("text/plain", ["application/pdf", "text/plain"]))
    ok_(not match("text/plain", ["application/pdf", "application/msword"]))
