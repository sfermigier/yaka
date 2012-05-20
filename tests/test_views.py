# Don't remove
import datetime
import fix_path


import unittest
from flaskext.testing import TestCase
from nose.tools import eq_, ok_

from util import init_data
from config import TestConfig

from yaka_crm import app, db

import re

from yaka_crm import views # Don't remove
from yaka_crm.views import filesize, date_age


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


  def test_home(self):
    response = self.client.get("/")
    ok_(response.status_code in [200, 302])

  def test_admin(self):
    response = self.client.get("/admin/")
    self.assert_200(response)

  def test_accounts(self):
    response = self.client.get("/crm/accounts/")
    self.assert_200(response)

  def test_search(self):
    response = self.client.get("/search/?q=john")
    self.assert_200(response)

    response = self.client.get("/search/live?q=john")
    self.assert_200(response)

  # Test additional blueprints (TODO: move to a distinct test case).
  def test_users(self):
    response = self.client.get("/users/")
    self.assert_200(response)

    m = re.search("/users/([0-9]+)", response.data)
    uid = int(m.group(1))

    response = self.client.get("/users/%d" % uid)
    self.assert_200(response)

    response = self.client.get("/users/%d/mugshot" % uid)
    self.assert_200(response)
    eq_("image/jpeg", response.headers["content-type"])

    response = self.client.get("/users/%d/mugshot?s=55" % uid)
    self.assert_200(response)
    eq_("image/jpeg", response.headers["content-type"])

    response = self.client.get("/users/%d/mugshot?s=48" % uid)
    self.assert_200(response)
    eq_("image/jpeg", response.headers["content-type"])


  def test_reports(self):
    response = self.client.get("/reports/")
    self.assert_200(response)

  # Util
  @staticmethod
  def uid_from_url(url):
    return int(url[len("http://localhost/users/"):])


class TestFilters(unittest.TestCase):

  def test_bytes(self):
    eq_("100 B", filesize(100))
    eq_("1.0 kB", filesize(1000))
    eq_("1.1 kB", filesize(1100))
    eq_("10 kB", filesize(10000))

  def test_date_age(self):
    now = datetime.datetime(2012, 6, 10, 10, 10, 10)

    dt = datetime.datetime(2012, 6, 10, 10, 10, 0)
    eq_("2012-06-10 10:10 (a minute ago)", date_age(dt, now))

    dt = datetime.datetime(2012, 6, 10, 10, 8, 10)
    eq_("2012-06-10 10:08 (2 minutes ago)", date_age(dt, now))

    dt = datetime.datetime(2012, 6, 10, 8, 10, 10)
    eq_("2012-06-10 08:10 (2 hours ago)", date_age(dt, now))