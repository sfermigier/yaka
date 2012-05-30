from nose.tools import eq_
from base import IntegrationTestCase
from util import init_data

from yaka_crm import db


class TestViews(IntegrationTestCase):

  def setUp(self):
    IntegrationTestCase.setUp(self)
    init_data(db)

  # Tests start here
  def test_login_happy_path(self):
    data = dict(email='sf@example.com', password='admin')
    response = self.client.post("/login", data=data)
    eq_(response.status_code, 302)

  def test_login_wrong_password(self):
    data = dict(email='sf@example.com', password='wrong')
    response = self.client.post("/login", data=data)
    eq_(response.status_code, 401)

  def test_login_wrong_email(self):
    data = dict(email='wrong@example.com', password='wrong')
    response = self.client.post("/login", data=data)
    eq_(response.status_code, 401)
