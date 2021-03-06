"""Static configuration for the application.
"""

from flask import Flask
from flask.globals import g, request
from flask_assets import Environment

from .extensions import mail, db, babel
from .filters import init_filters
from .auth import init_auth
from .services import indexing, audit, activity

# Import entity classes. Don't remove
from .apps.crm.entities import *
from .apps.dm import File, Folder


__all__ = ['create_app']


class Application(Flask):
  def __init__(self, config):
    Flask.__init__(self, __name__)

    # TODO: deal with envvar and pyfile
    self.config.from_object(config)

    # Initialise helpers and services
    db.init_app(self)
    mail.init_app(self)

    # Babel
    babel.init_app(self)
    babel.localeselector(get_locale)

    # Assets (bundles are defined in the templates)
    assets = Environment(self)

    # Initialise filters
    init_filters(self)
    init_auth(self)

    from .apps.crm.frontend import CRM
    crm = CRM(self)

    self.register_blueprints()

    # Must come after all entity classes have been declared.
    self.register_services()

  def register_blueprints(self):
    # Register additional blueprints
    from .apps.main import main
    from .apps.admin import admin
    from .apps.dm import dm
    from .apps.reports import reports
    from .apps.users import users
    from .apps.search import search
    from .apps.social import social
    from .apps.social.restapi import restapi

    self.register_blueprint(main)
    self.register_blueprint(admin)
    self.register_blueprint(dm)
    self.register_blueprint(reports)
    self.register_blueprint(users)
    self.register_blueprint(search)
    self.register_blueprint(social)
    self.register_blueprint(restapi)

  def register_services(self):
    # Initiate services
    self.extensions['indexing'] = indexing.get_service(self)
    self.extensions['audit'] = audit.get_service(self)
    self.extensions['activity'] = activity.get_service(self)

  def start_services(self):
    for service in self.extensions.values():
      if hasattr(service, 'start'):
        service.start()

  def stop_services(self):
    for service in self.extensions.values():
      if hasattr(service, 'stop'):
        service.stop()


def create_app(config):
  return Application(config)


# Additional config for Babel
def get_locale():
  # if a user is logged in, use the locale from the user settings
  user = getattr(g, 'user', None)
  if user is not None:
    locale = user.locale
    if locale:
      return user.locale
  # otherwise try to guess the language from the user accept
  # header the browser transmits.  We support de/fr/en in this
  # example.  The best match wins.
  return request.accept_languages.best_match(['en', 'fr'])


#@babel.timezoneselector
#def get_timezone():
#  user = getattr(g, 'user', None)
#  if user is not None:
#    return user.timezone
