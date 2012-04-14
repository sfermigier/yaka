from flask import Flask

from flaskext.mail import Mail
from flaskext.openid import OpenID
from flask_sqlalchemy import SQLAlchemy
from flaskext.cache import Cache
from whooshalchemy import IndexService

__all__ = ['oid', 'mail', 'db', 'cache', 'app']

# Create helpers
oid = OpenID()
mail = Mail()
db = SQLAlchemy()
cache = Cache()

# Create app
app = Flask(__name__)

# Initialise helpers and services
db.init_app(app)

index_service = IndexService(app.config)
#index_service.register_class(models.User)
#index_service.register_class(models.Message)

# Register blueprints
#app.register_blueprint(restapi)
