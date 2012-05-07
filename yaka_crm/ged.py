"""GED (i.e. document management module) for Yaka.

Don't worry, it's just a prototype. Will be refactored later.
"""

from flask import Blueprint, render_template
from sqlalchemy.types import UnicodeText, LargeBinary, Integer

from yaka_crm.core.entities import Entity, Column


ged = Blueprint("ged", __name__, url_prefix="/ged")

#
# Entities and forms
#
class Folder(Entity):
  __tablename__ = 'folder'

  name = Column(UnicodeText)
  parent_id = Column(Integer)


class File(Entity):
  __tablename__ = 'file'

  name = Column(UnicodeText)
  parent_id = Column(Integer)

  text = Column(UnicodeText)
  data = Column(LargeBinary)


#
# Controllers
#

@ged.route("/")
def home():
  return render_template("ged/test.html", breadcrumbs=[])