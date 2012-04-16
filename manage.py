#!/usr/bin/env python

from flaskext.script import Manager

from yaka_crm import app, db, entities, views, finish_setup
from config import DebugConfig

# Config
app.config.from_object(DebugConfig())
finish_setup()

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

  from yaka_crm.entities import Contact, Account, User

  account1 = Account(name="Fermi Corp", website="http://fermigier.com/")
  db.session.add(account1)
  db.session.commit()

  contact1 = Contact(first_name="Stefane", last_name="Fermigier", email="sf@example.com")
  contact1.account = account1
  contact2 = Contact(first_name="Paul", last_name="Dupont", email="paul@example.com")
  contact2.account = account1

  user1 = User(first_name="Stefane", last_name="Fermigier", email="sf@example.com")

  db.session.add(contact1)
  db.session.add(contact2)
  db.session.add(user1)
  db.session.commit()


if __name__ == '__main__':
    manager.run()
