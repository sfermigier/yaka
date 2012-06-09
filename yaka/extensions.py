from flaskext.mail import Mail
from flaskext.openid import OpenID
from flask_sqlalchemy import SQLAlchemy
from flaskext.cache import Cache

# Create helpers
mail = Mail()
db = SQLAlchemy()

# Not needed yet
oid = OpenID()
cache = Cache()
