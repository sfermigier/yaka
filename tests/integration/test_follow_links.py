"""
Test the application by clicking on all the links.

Some links are blacklisted due to side effects.

TODO: fix this.
"""

from HTMLParser import HTMLParser
from nose.tools import eq_
from tests.integration.base import IntegrationTestCase


class HrefExtractor(HTMLParser):

  def __init__(self):
    HTMLParser.__init__(self)
    self.links = set()

  def handle_starttag(self, tag, attrs):
    for attr_name, attr_value in attrs:
      if (tag, attr_name) in [('a', 'href'), ('link', 'href'), ('script', 'src'), ('img', 'src')]:
        link = attr_value.split("#")[0]
        if link.startswith("http://"):
          continue
        self.links.add(link)


class Crawler(object):

  def __init__(self, client, root):
    self.client = client
    self.to_visit = set([root])
    self.visited = set()

  def blacklisted(self, url):
    if url in ["/logout", "/users", "/"]:
      return True
    if url.startswith("/crm/") or url.startswith("/users/"):
      return True
    return False

  def crawl(self):
    while self.to_visit:
      link = self.to_visit.pop()
      if not link or link in self.visited:
        continue
      response = self.client.get(link)
      eq_(200, response.status_code)

      if not response.content_type.startswith('text/html'):
        continue

      self.visited.add(link)
      parser = HrefExtractor()
      parser.feed(response.data)
      for new_link in parser.links:
        if self.blacklisted(new_link):
          continue
        if not new_link.startswith("/"):
          new_link = link.split("?")[0] + new_link
        if new_link not in self.visited:
          self.to_visit.add(new_link)


class TestViews(IntegrationTestCase):

  init_data = True
  no_login = True

  # Tests start here
  def test_home(self):
    crawler = Crawler(self.client, "/social/")
    crawler.crawl()
