from base import IntegrationTestCase
from nose.tools import eq_, ok_
import re


class TestViews(IntegrationTestCase):

  init_data = True
  no_login = True

  # Tests start here
  def test_home(self):
    response = self.client.get("/")
    ok_(response.status_code in [200, 302])

  def test_admin(self):
    response = self.client.get("/admin/")
    self.assert_200(response)

  def test_accounts(self):
    response = self.client.get("/crm/accounts/")
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
