import csv
from pprint import pprint
import os.path
import time
import sys
from yaka_crm.entities import Contact, Account, User, Opportunity

def init_data(db):
  """Initializes DB with some dummy data."""

  from yaka_crm.entities import Contact, Account, User

  account1 = Account(name="Fermi Corp", website="http://fermigier.com/")
  db.session.add(account1)
  db.session.commit()

  contact1 = Contact(first_name="Stefane", last_name="Fermigier", email="sf@example.com")
  contact1.account = account1
  contact2 = Contact(first_name="Paul", last_name="Dupont", email="paul@example.com")

  user1 = User(first_name="Stefane", last_name="Fermigier", email="sf@example.com")

  db.session.add(contact1)
  db.session.add(contact2)
  db.session.add(user1)
  db.session.commit()


class DataLoader(object):

  def __init__(self, db):
    self.db = db
    self.accounts_map = {}

  def load_data(self):
    self.load_accounts()
    self.load_contacts()
    self.db.session.commit()

  def load_accounts(self):
    reader = self.get_reader("Accounts.csv")
    for line in reader:
      d = {}
      for col in ['Name', 'Website', 'Office Phone', 'Type', 'Industry']:
        d[col.lower().replace(" ", "_")] = line[col]
      for k in ['Street', 'City', 'State', 'Country']:
        d["address_" + k.lower()] = line["Billing %s" % k]
      account = Account(**d)
      self.db.session.add(account)
      self.accounts_map[line['Name']] = account

  def load_contacts(self):
    reader = self.get_reader("Contacts.csv")
    for line in reader:
      d = {}
      d['email'] = line['Email Address']
      d['job_title'] = line['Title']
      for col in ['First Name', 'Last Name', 'Department']:
        d[col.lower().replace(" ", "_")] = line[col]

      for k in ['Street', 'City', 'State', 'Country']:
        d["address_" + k.lower()] = line["Primary Address %s" % k]

      contact = Contact(**d)
      account = self.accounts_map.get(line['Account Name'])
      if account:
        contact.account = account
      self.db.session.add(contact)

  def load_opportunities(self):
    reader = self.get_reader("Opportunities.csv")
    for d in reader:
      contact = Opportunity(
        first_name=d['First Name'], last_name=d['Last Name'], email=d['Email Address'])
      self.db.session.add(contact)

  @staticmethod
  def get_reader(filename):
    path = os.path.join(os.path.dirname(__file__), "dummy_data", filename)
    return csv.DictReader(open(path))


def load_data(db):
  loader = DataLoader(db)
  loader.load_data()