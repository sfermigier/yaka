import unittest
from nose.tools import ok_
from yaka_crm.apps.dm import match


class TestDMUtils(unittest.TestCase):

  def test_match(self):
    ok_(match("text/plain", ["text/*"]))
    ok_(not match("text/plain", ["text/html"]))

    ok_(match("text/plain", ["application/pdf", "text/plain"]))
    ok_(not match("text/plain", ["application/pdf", "application/msword"]))
