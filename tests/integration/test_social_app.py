from base import IntegrationTestCase
import re


class TestViews(IntegrationTestCase):

  init_data = True
  no_login = True

  # Tests start here
  def test_home(self):
    response = self.client.get("/social/")
    self.assert_200(response)

  def test_users(self):
    response = self.client.get("/social/users/")
    self.assert_200(response)

  def test_groups(self):
    response = self.client.get("/social/groups/")
    self.assert_200(response)
