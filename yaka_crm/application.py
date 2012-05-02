from flask import Flask
from whooshalchemy import IndexService

from .extensions import oid, mail, db, cache

__all__ = ['oid', 'mail', 'db', 'cache', 'app']

# Create app
app = Flask(__name__)

# Initialise helpers and services
db.init_app(app)

# TODO: autodiscovery of searchable classes
from .entities import Contact, Account, Opportunity, Lead, Document
index_service = IndexService(app.config)
index_service.register_class(Contact)
index_service.register_class(Account)
index_service.register_class(Opportunity)
index_service.register_class(Lead)
index_service.register_class(Document)

from .frontend import CRM

crm = CRM(app)

# Register additional blueprints
from admin import admin
app.register_blueprint(admin)
