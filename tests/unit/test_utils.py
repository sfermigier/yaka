from unittest import TestCase
from nose.tools import ok_

from yaka.apps.dm import match
from yaka.core.util import Pagination


class TestDMUtils(TestCase):

  def test_match(self):
    ok_(match("text/plain", ["text/*"]))
    ok_(not match("text/plain", ["text/html"]))

    ok_(match("text/plain", ["application/pdf", "text/plain"]))
    ok_(not match("text/plain", ["application/pdf", "application/msword"]))


class TestPagination(TestCase):

  def test1(self):
    p = Pagination(1, 10, 10)
    l = list(p.iter_pages())
    self.assertEquals([1], l)

  def test2(self):
    p = Pagination(1, 10, 20)
    l = list(p.iter_pages())
    self.assertEquals([1, 2], l)

  def test3(self):
    p = Pagination(1, 10, 100)
    l = list(p.iter_pages())
    self.assertEquals([1, 2, 3, 4, 5, None, 9, 10], l)

  def test4(self):
    p = Pagination(10, 10, 100)
    l = list(p.iter_pages())
    self.assertEquals([1, 2, None, 8, 9, 10], l)
