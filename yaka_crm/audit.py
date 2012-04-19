from datetime import datetime

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, UnicodeText, DateTime, Text


class AuditEntry(db.Model):
  """Logs modifications to auditable classes."""

  __tablename__ = 'audit_entry'

  CREATION = 0
  UPDATE   = 1
  DELETION = 2

  uid = Column(Integer, primary_key=True)
  happened_at = Column(DateTime, default=datetime.utcnow)
  type = Column(Integer) # CREATION / UPDATE / DELETION

  entity_id = Column(Integer)
  entity_class = Column(Text)

  user_id = Column(Integer)

  attribute = Column(Text)
  attribute_type = Column(Text)
  old_value = Column(UnicodeText)
  new_value = Column(UnicodeText)

