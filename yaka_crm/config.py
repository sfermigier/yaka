
class ProductionConfig(object):
  DEBUG = False
  DEBUG_TB_INTERCEPT_REDIRECTS = False
  TESTING = False
  CSRF_ENABLED = True

  SQLALCHEMY_DATABASE_URI = "sqlite:///yaka-crm.db"
  SQLALCHEMY_ECHO = False

  SECRET_KEY = "tototiti"
  SALT = "yaka"
  WHOOSH_BASE = "whoosh"


class DebugConfig(ProductionConfig):
  DEBUG = True
  SQLALCHEMY_ECHO = True
  DEBUG_TB_INTERCEPT_REDIRECTS = True


class TestConfig(DebugConfig):
  TESTING = True
  SQLALCHEMY_DATABASE_URI = "sqlite://"
  SQLALCHEMY_ECHO = False
