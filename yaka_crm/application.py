"""Static configuration for the application.
"""

from flask import Flask

from .extensions import mail, db
from .filters import init_filters
from .auth import init_auth
from .services.audit import AuditService
from .services.activity import ActivityService
from .services.indexing import IndexService

# Import entity classes. Don't remove
from .entities import *
from .apps.dm import *


__all__ = ['mail', 'db', 'create_app']


def create_app(config):

  # Create app
  app = Flask(__name__)

  # TODO: deal with envvar and pyfile
  app.config.from_object(config)

  # Initialise helpers and services
  db.init_app(app)
  mail.init_app(app)

  # Initialise filters
  init_filters(app)
  init_auth(app)

  from .frontend import CRM
  crm = CRM(app)

  # Register additional blueprints
  from .views import main
  from .apps.admin import admin
  from .apps.dm import dm
  from .apps.reports import reports
  from .apps.users import users
  from .apps.search import search
  from .apps.social import social

  app.register_blueprint(main)
  app.register_blueprint(admin)
  app.register_blueprint(dm)
  app.register_blueprint(reports)
  app.register_blueprint(users)
  app.register_blueprint(search)
  app.register_blueprint(social)

  # Initiate services
  # Must come after all entity classes have been declared.
  init_index_service(app)
  init_audit_service(app)
  init_activity_service(app)

  return app


def start_services(app):
  for service in app.extensions.values():
    if hasattr(service, 'start'):
      service.start()


def stop_services(app):
  for service in app.extensions.values():
    if hasattr(service, 'stop'):
      service.stop()


def init_activity_service(app):
  activity_service = ActivityService.instance()
  app.extensions['activity'] = activity_service


def init_audit_service(app):
  audit_service = AuditService.instance()
  app.extensions['audit'] = audit_service


def init_index_service(app):
  index_service = IndexService.instance(app)
  app.extensions['index'] = index_service

