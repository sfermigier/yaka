
class ProductionConfig(object):
  DEBUG = False
  TESTING = False
  CSRF_ENABLED = False
  SQLALCHEMY_DATABASE_URI = "sqlite:///yaka.db"
  SQLALCHEMY_ECHO = False
  SECRET_KEY = "tototiti"
  SALT = "retwis"
  WHOOSH_BASE = "whoosh"


class DebugConfig(ProductionConfig):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = "sqlite:///yaka.db"
  SQLALCHEMY_ECHO = False
  DEBUG_TB_INTERCEPT_REDIRECTS = False
