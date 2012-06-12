from flaskext.mail import Mail
from flaskext.openid import OpenID
from flask_sqlalchemy import SQLAlchemy
from flaskext.cache import Cache
from flaskext.babel import Babel

# Create helpers
mail = Mail()
db = SQLAlchemy()
babel = Babel()

# Not needed yet
oid = OpenID()
cache = Cache()
