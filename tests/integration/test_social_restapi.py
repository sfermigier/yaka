from StringIO import StringIO
from datetime import datetime, timedelta
import iso8601
from pytz import UTC

from werkzeug.datastructures import FileStorage

from tests.integration.base import IntegrationTestCase
from yaka.core.subjects import User


class BaseApiTest(IntegrationTestCase):

  init_data = True
  no_login = True

  def setUp(self):
    IntegrationTestCase.setUp(self)
    self.master_user = User.query.all()[0]


class MessagesApiTest(BaseApiTest):

  def create_message(self):
    data = {'content': "First post!"}
    response = self.client.post("/api/messages", data=data)
    self.assert_status(response, 201)
    m = response.json

    now = datetime.utcnow().replace(tzinfo=UTC)
    created = iso8601.parse_date(m['created_at'])
    self.assert_(now > created)
    self.assert_(now - created < timedelta(1))

    content = m['content']
    self.assertEquals(content, "First post!")

    return m

  def test_create_message(self):
    response = self.client.get("/api/messages")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 0)

    m = self.create_message()

    # Test message exists
    response = self.client.get("/api/messages/%d" % m['uid'])
    self.assert_200(response)
    m1 = response.json
    for k in m1:
      self.assertEquals(m[k], m1[k])

    # Test list
    response = self.client.get("/api/messages")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 1)
    message = messages[0]
    self.assertEquals(message['creator_id'], self.master_user.uid)

    # Test stream
    response = self.client.get("/api/users/%d/messages" % self.master_user.uid)
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 1)

    return # TODO

    # Test search
    response = self.client.get("/api/search/messages?q=first")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 1)

    response = self.client.get("/api/search/messages?q=last")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 0)

    response = self.client.get("/api/search/messages?q=post")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 1)

  def test_update_message(self):
    m = self.create_message()

    # Test update
    response = self.client.put("/api/messages/%d" % m['uid'], data={'content': 'Changed'})
    self.assert_200(response)
    m2 = response.json
    content = m2['content']
    self.assertEquals(content, "Changed")

    response = self.client.get("/api/messages/%d" % m['uid'])
    self.assert_200(response)
    m3 = response.json
    for k in m3:
      self.assertEquals(m2[k], m3[k])

    return # TODO
    # Test search
    response = self.client.get("/api/search/messages?q=first")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 0)

    response = self.client.get("/api/search/messages?q=changed")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 1)

  def test_delete_message(self):
    m = self.create_message()

    # Test delete
    response = self.client.delete("/api/messages/%d" % m['uid'])
    self.assert_204(response)

    response = self.client.get("/api/messages")
    messages = response.json
    self.assertEquals(len(messages), 0)

    return # TODO
    # Test search
    response = self.client.get("/api/search/messages?q=first")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 0)


class UserApiTest(BaseApiTest):

  def setUp(self):
    BaseApiTest.setUp(self)
    response = self.client.get("/api/users")
    self.assert_200(response)
    users = response.json
    self.initial_user_count = len(users)

  def create_user(self):
    """Creates an user called "John"."""

    data = dict(first_name="John", last_name="Test User", email="test@example.com", password="toto")
    response = self.client.post("/api/users", data=data)
    self.assert_status(response, 201)
    u = response.json

    now = datetime.utcnow().replace(tzinfo=UTC)
    created = iso8601.parse_date(u['created_at'])
    self.assert_(now > created)
    self.assert_(now - created < timedelta(1))

    self.assertEquals(u['first_name'], "John")
    self.assertEquals(u['last_name'], "Test User")

    return u

  def test_create_user(self):
    u = self.create_user()

    # Test user exists
    response = self.client.get("/api/users/%d" % u['uid'])
    self.assert_200(response)
    u1 = response.json
    for k in u1:
      self.assertEquals(u[k], u1[k])

    # Test list
    response = self.client.get("/api/users")
    self.assert_200(response)
    users = response.json
    self.assertEquals(len(users), self.initial_user_count + 1)

    return # TODO
    # Test search
    response = self.client.get("/api/search/users?q=john")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 1)

  def test_update_user(self):
    u = self.create_user()

    # Test update
    response = self.client.put("/api/users/%d" % u['uid'], data={'first_name': 'Paul'})
    self.assert_200(response)
    u2 = response.json
    content = u2['first_name']
    self.assertEquals(content, "Paul")

    response = self.client.get("/api/users/%d" % u['uid'])
    self.assert_200(response)
    u3 = response.json
    for k in u3:
      self.assertEquals(u2[k], u3[k])

    return # TODO
    # Test search after update
    response = self.client.get("/api/search/users?q=first")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 0)

    response = self.client.get("/api/search/users?q=paul")
    self.assert_200(response)
    messages = response.json
    self.assertEquals(len(messages), 1)

  def test_delete_user(self):
    u = self.create_user()

    # Test delete
    response = self.client.delete("/api/users/%d" % u['uid'])
    self.assert_204(response)

    response = self.client.get("/api/users")
    self.assert_200(response)
    users = response.json
    self.assertEquals(len(users), self.initial_user_count)

    return

    # Test search
    response = self.client.get("/api/search/users?q=first")
    self.assert_200(response)
    users = response.json
    self.assertEquals(len(users), 0)

  def test_following(self):
    # Create a new user
    u = self.create_user()

    # Nobody follows / is followed by new user
    response = self.client.get("/api/users/%d/followers" % u['uid'])
    self.assert_200(response)
    self.assertEquals(len(response.json), 0)

    response = self.client.get("/api/users/%d/followees" % u['uid'])
    self.assert_200(response)
    self.assertEquals(len(response.json), 0)

    # Follow new user
    response = self.client.post("/api/users/%d/followers" % u['uid'])
    self.assert_204(response)

    response = self.client.get("/api/users/%d/followers" % u['uid'])
    self.assert_200(response)
    self.assertEquals(len(response.json), 1)

    response = self.client.get("/api/users/%d/followees" % u['uid'])
    self.assert_200(response)
    self.assertEquals(len(response.json), 0)

    response = self.client.get("/api/users/%d/followees" % self.master_user.uid)
    self.assert_200(response)
    self.assertEquals(len(response.json), 1)

    # Unfollow
    response = self.client.delete("/api/users/%d/followers/%d" % (u['uid'], self.master_user.uid))
    self.assert_204(response)

    #users = response.json
    #self.assertEquals(len(users), 0)


class AttachmentApiTest(BaseApiTest):

  def test_create_attachment(self):
    fs = FileStorage(StringIO("Some random content"), "test.txt")
    data = {'attachment': fs}
    response = self.client.post("/api/attachments", data=data)
    self.assert_status(response, 201)


class SearchApiTest(BaseApiTest):

  def XXXtest_users(self):
    response = self.client.get("/api/search/users")
    self.assert_200(response)
    self.assertEquals(len(response.json), 0)

    response = self.client.get("/api/search/users?q=toto")
    self.assert_200(response)
    self.assertEquals(len(response.json), 0)

  def XXXtest_messages(self):
    response = self.client.get("/api/search/messages")
    self.assert_200(response)
    self.assertEquals(len(response.json), 0)

    response = self.client.get("/api/search/messages?q=toto")
    self.assert_200(response)
    self.assertEquals(len(response.json), 0)


class GroupApiTest(BaseApiTest):

  def setUp(self):
    BaseApiTest.setUp(self)
    response = self.client.get("/api/groups")
    self.assert_200(response)
    groups = response.json
    self.initial_group_count = len(groups)

  def create_group(self):
    """Creates an user called "John"."""

    data = dict(name="Group1")
    response = self.client.post("/api/groups", data=data)
    self.assert_status(response, 201)
    group = response.json

    now = datetime.utcnow().replace(tzinfo=UTC)
    created = iso8601.parse_date(group['created_at'])
    self.assert_(now > created)
    self.assert_(now - created < timedelta(1))

    self.assertEquals(group['name'], "Group1")

    return group

  def test_create_group(self):
    group = self.create_group()

    # Test user exists
    response = self.client.get("/api/groups/%d" % group['uid'])
    self.assert_200(response)
    group1 = response.json
    for k in group1:
      self.assertEquals(group[k], group1[k])

    # Test list
    response = self.client.get("/api/groups")
    self.assert_200(response)
    groups = response.json
    self.assertEquals(len(groups), self.initial_group_count + 1)

    # Test search
#    response = self.client.get("/api/search/users?q=john")
#    self.assert_200(response)
#    messages = response.json
#    self.assertEquals(len(messages), 1)