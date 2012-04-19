#!/usr/bin/env python

from flaskext.script import Manager

from yaka_crm import app, db, entities, views
from config import DebugConfig

# Config
app.config.from_object(DebugConfig())

# Manager
manager = Manager(app)

# Debug Toolbar
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

  from tests.util import init_data
  init_data(db)


if __name__ == '__main__':
    manager.run()
