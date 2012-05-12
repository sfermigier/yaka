"""Static configuration for the application.
"""

from flask import Flask

#noinspection PyUnresolvedReferences
from .extensions import oid, mail, db, cache

__all__ = ['oid', 'mail', 'db', 'cache', 'app']

# Create app
app = Flask(__name__)

# Initialise helpers and services
db.init_app(app)

# TODO: autodiscovery of searchable classes
from .entities import Contact, Account, Opportunity, Lead, Document
from .ged import File, Folder

all_entity_classes = [Contact, Account, Opportunity, Lead, Document, File, Folder]

from .frontend import CRM
crm = CRM(app)

# Register additional blueprints
from admin import admin
app.register_blueprint(admin)

from ged import ged
app.register_blueprint(ged)

# Must (currently) come after all entity classes are declared.
from whooshalchemy import IndexService
index_service = IndexService(app.config)

from audit import AuditService
audit_service = AuditService(start=True)
app.extensions['audit'] = audit_service

# TODO: remove
for cls in all_entity_classes:
  index_service.register_class(cls)
  #audit_service.register_class(cls)
