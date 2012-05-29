import unittest
import datetime
from nose.tools import eq_

from yaka_crm.filters import filesize, date_age


class TestFilters(unittest.TestCase):

  def test_filesize(self):
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