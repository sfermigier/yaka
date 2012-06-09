from unittest import TestCase
from nose.tools import ok_
from yaka.core.entities import SEARCHABLE, NOT_SEARCHABLE, AUDITABLE


class InfoTestCase(TestCase):

  def test(self):
    info = SEARCHABLE
    ok_(info['searchable'])

    info = NOT_SEARCHABLE
    ok_(not info['searchable'])

    info = SEARCHABLE + AUDITABLE
    ok_(info['searchable'])
    ok_(info['auditable'])
