
# Don't remove
import subprocess

from io import StringIO
from nose.tools import eq_, ok_
import os
from flaskext.testing import TestCase
import re
from tests.util import DataLoader

from yaka_crm import app, db
from config import TestConfig

import yaka_crm.views # Don't remove

from util import init_data

ROOT = "/dm/"


class TestViews(TestCase):

  def create_app(self):
    app.config.from_object(TestConfig())
    return app

  def setUp(self):
    TestCase.setUp(self)
    db.create_all()
    self.session = db.session
    init_data(db)

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    TestCase.tearDown(self)

  def assert_302(self, response):
    self.assertStatus(response, 302)

  @staticmethod
  def uid_from_url(url):
    return int(url[len("http://localhost" + ROOT):])


  def test_home(self):
    response = self.client.get(ROOT)
    self.assert_200(response)

  def test_preview(self):
    loader = DataLoader(db)
    loader.load_files()
    db.session.commit()

    response = self.client.get(ROOT)
    self.assert_200(response)

    data = response.data
    for m in re.findall(ROOT + "([0-9]+)", data):
      uid = int(m)

      response = self.client.get(ROOT + "%d/preview" % uid)
      self.assert_200(response)


  def test_upload_text(self):
    CONTENT = u'my file contents'
    NAME = u'hello world.txt'
    data = {
      'file': (StringIO(CONTENT), NAME, 'text/plain'),
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

    response = self.client.get(ROOT + "%d/preview" % uid)
    self.assert_200(response)
    eq_(response.headers['Content-Type'], 'image/jpeg')

    response = self.client.post(ROOT + "%d/delete" % uid)
    self.assert_302(response)

    response = self.client.get(ROOT + "%d" % uid)
    self.assert_404(response)

  @staticmethod
  def open_file(filename):
    path = os.path.join(os.path.dirname(__file__), "dummy_files", filename)
    return open(path)