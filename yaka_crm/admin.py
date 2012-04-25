from flask import Blueprint
from flask import render_template

from .core.frontend import BreadCrumbs

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/")
def admin_home():
  bc = BreadCrumbs()
  bc.add("/", "Home")
  bc.add("/admin", "Admin")
  return render_template("admin.html", breadcrumbs=bc)