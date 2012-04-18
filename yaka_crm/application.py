from flask import Flask
from whooshalchemy import IndexService

from .extensions import oid, mail, db, cache

__all__ = ['oid', 'mail', 'db', 'cache', 'app']

# Create app
app = Flask(__name__)

# Initialise helpers and services
db.init_app(app)

# TODO: autodiscovery of searchable classes
from .entities import Contact, Account
index_service = IndexService(app.config)
index_service.register_class(Contact)
index_service.register_class(Account)

from .frontend import CRM

crm = CRM(app)


# Register blueprints
#app.register_blueprint(restapi)
