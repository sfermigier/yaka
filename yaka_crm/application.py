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


class Application(Flask):
  def __init__(self, config):
    Flask.__init__(self, __name__)

    # TODO: deal with envvar and pyfile
    self.config.from_object(config)

    # Initialise helpers and services
    db.init_app(self)
    mail.init_app(self)

    # Initialise filters
    init_filters(self)
    init_auth(self)

    from .frontend import CRM
    crm = CRM(self)

    # Register additional blueprints
    from .views import main
    from .apps.admin import admin
    from .apps.dm import dm
    from .apps.reports import reports
    from .apps.users import users
    from .apps.search import search
    from .apps.social import social

    self.register_blueprint(main)
    self.register_blueprint(admin)
    self.register_blueprint(dm)
    self.register_blueprint(reports)
    self.register_blueprint(users)
    self.register_blueprint(search)
    self.register_blueprint(social)

    # Initiate services
    # Must come after all entity classes have been declared.
    self.init_index_service()
    self.init_audit_service()
    self.init_activity_service()

  def start_services(self):
    for service in self.extensions.values():
      if hasattr(service, 'start'):
        service.start()

  def stop_services(self):
    for service in self.extensions.values():
      if hasattr(service, 'stop'):
        service.stop()
  
  def init_activity_service(self):
    activity_service = ActivityService.instance()
    self.extensions['activity'] = activity_service
  
  def init_audit_service(self):
    audit_service = AuditService.instance()
    self.extensions['audit'] = audit_service

  def init_index_service(self):
    index_service = IndexService.instance(self)
    self.extensions['index'] = index_service


def create_app(config):
  return Application(config)
