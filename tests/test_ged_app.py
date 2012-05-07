from io import StringIO
from flaskext.testing import TestCase

from yaka_crm import app, db
from config import TestConfig

import yaka_crm.views # Don't remove

from util import init_data


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


  def test_home(self):
    response = self.client.get("/ged/")
    self.assert_200(response)

  def test_upload_text(self):
    data = {
      'file': (StringIO(u'my file contents'), u'hello world.txt', 'text/plain'),
    }
    response = self.client.post("/ged/", data=data)
    #stream = StringIO(u'my file contents')
    #response = self.client.post("/ged/", input_stream=stream)
    self.assert_302(response)
