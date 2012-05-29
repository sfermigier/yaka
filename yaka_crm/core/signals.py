from blinker.base import Namespace

signals = Namespace()
entity_created = signals.signal("entity:created")
entity_updated = signals.signal("entity:updated")
entity_deleted = signals.signal("entity:deleted")

activity = signals.signal("activity")
