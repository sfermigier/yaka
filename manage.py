#!/usr/bin/env python

from flaskext.script import Manager
from flask.ext.sqlalchemy import get_debug_queries, SQLAlchemy
import sys

from yaka import create_app
from yaka.extensions import db
from config import DebugConfig


app = create_app(DebugConfig())
app.start_services()

manager = Manager(app)

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)

#
# Specific commands
#
@manager.command
def initdb():
  """Creates all database tables."""
  db.create_all()


@manager.command
def dropdb():
  """Drops all database tables."""
  db.drop_all()


@manager.command
def initdata():
  """Initializes DB with some dummy data."""
  from tests.integration.util import init_data

  init_data(db)


@manager.command
def loaddata():
  """Initializes DB with some dummy data."""
  from tests.integration.util import load_data

  load_data(db)


if __name__ == '__main__':
  if len(sys.argv) == 1:
    sys.argv.append('runserver')
  manager.run()
