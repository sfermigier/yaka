from flask import Flask
from whooshalchemy import IndexService

from .extensions import oid, mail, db, cache

__all__ = ['oid', 'mail', 'db', 'cache', 'app']

# Create app
app = Flask(__name__)

# Initialise helpers and services
db.init_app(app)

# TODO: autodiscovery of searchable classes
from yaka_crm import entities
index_service = IndexService(app.config)
index_service.register_class(entities.Contact)
index_service.register_class(entities.Account)

# Register blueprints
#app.register_blueprint(restapi)
