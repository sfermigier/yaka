from flaskext.mail import Mail
from flaskext.openid import OpenID
from flask_sqlalchemy import SQLAlchemy
from flaskext.cache import Cache

# Create helpers
oid = OpenID()
mail = Mail()
db = SQLAlchemy()
cache = Cache()
