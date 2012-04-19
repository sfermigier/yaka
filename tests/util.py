def init_data(db):
  """Initializes DB with some dummy data."""

  from yaka_crm.entities import Contact, Account, User

  account1 = Account(name="Fermi Corp", website="http://fermigier.com/")
  db.session.add(account1)
  db.session.commit()

  contact1 = Contact(first_name="Stefane", last_name="Fermigier", email="sf@example.com")
  contact1.account = account1
  contact2 = Contact(first_name="Paul", last_name="Dupont", email="paul@example.com")
  contact2.account = account1

  user1 = User(first_name="Stefane", last_name="Fermigier", email="sf@example.com")

  db.session.add(contact1)
  db.session.add(contact2)
  db.session.add(user1)
  db.session.commit()
