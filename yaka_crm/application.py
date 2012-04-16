from flask import Flask
from whooshalchemy import IndexService

from .extensions import *

__all__ = ['oid', 'mail', 'db', 'cache', 'app', 'finish_setup']

# Create app
app = Flask(__name__)

# Initialise helpers and services
db.init_app(app)

# TODO: autodiscovery of searchable classes
from yaka_crm import entities
index_service = IndexService(app.config)
print entities.Contact.__searchable__
index_service.register_class(entities.Contact)
index_service.register_class(entities.Account)

def finish_setup():
  pass

# Register blueprints
#app.register_blueprint(restapi)
