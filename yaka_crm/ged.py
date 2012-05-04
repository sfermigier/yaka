"""GED (i.e. document management module) for Yaka.

Don't worry, it's just a prototype. Will be refactored later.
"""

from flask import Blueprint, render_template

ged = Blueprint("ged", __name__, url_prefix="/ged")

@ged.route("/")
def home():
  return render_template("ged/test.html", breadcrumbs=[])