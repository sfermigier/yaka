from datetime import datetime, timedelta
from flask import g, session, redirect, request

from yaka.core.subjects import User
from yaka.apps.crm.frontend import CRM
from yaka.extensions import db


# TODO: split method, it's doing too much.

def init_auth(app):

  @app.before_request
  def before_request():
    # TODO remove when tests pass
    if app.config.get("NO_LOGIN", False):
      g.user = User.query.all()[0]

    else:
      user_id = session.get("user_id")
      if user_id:
        try:
          user = User.query.get(user_id)
          g.user = user
        except:
          return redirect("/login", code=401)
          #abort(401, "Must authenticate")
      elif request.path == '/login' or request.path.startswith("/static/"):
        g.user = None
      else:
        return redirect("/login", code=401)
        #abort(401, "Must authenticate")

    # Update last_active every 60 seconds only.
    if g.user and (datetime.utcnow() - g.user.last_active > timedelta(0, 60)):
      g.user.last_active = datetime.utcnow()
      db.session.add(g.user)
      db.session.commit()

    g.modules = CRM.modules
    g.recent_items = session.get('recent_items', [])
