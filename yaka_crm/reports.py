from flask import Blueprint
from flask import render_template

from .core.frontend import BreadCrumbs

reports = Blueprint("reports", __name__, url_prefix="/reports")

@reports.route("/")
def home():
  bc = BreadCrumbs()
  bc.add("/", "Home")
  bc.add("/reports", "Reports")
  return render_template("reports/home.html", breadcrumbs=bc)

@reports.route("/report")
def report():
  bc = BreadCrumbs()
  bc.add("/", "Home")
  bc.add("/reports", "Reports")
  bc.add("/reports/report", "Sample Report")
  return render_template("reports/report.html", breadcrumbs=bc)

