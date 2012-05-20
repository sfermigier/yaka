import csv
import mimetypes
from random import choice
import os.path
import datetime

from flask import g

from yaka_crm.entities import Contact, Account, Opportunity, Lead, User
from yaka_crm.apps.dm import File


def init_data(db):
  """Initializes DB with some dummy data."""

  account1 = Account(name="Fermi Corp", website="http://fermigier.com/")
  db.session.add(account1)
  db.session.commit()

  contact1 = Contact(first_name="Stefane", last_name="Fermigier", email="sf@example.com")
  contact1.account = account1
  contact2 = Contact(first_name="Paul", last_name="Dupont", email="paul@example.com")

  user1 = User(first_name="Stefane", last_name="Fermigier", email="sf@example.com", password="admin")
  photo_path = os.path.join(os.path.dirname(__file__), "dummy_files", "mugshot.jpg")
  user1.photo = open(photo_path).read()

  db.session.add(contact1)
  db.session.add(contact2)
  db.session.add(user1)
  db.session.commit()


class DataLoader(object):

  def __init__(self, db):
    self.db = db
    self.accounts_map = {}
    self.users = []

  def load_data(self):
    self.load_users()
    self.db.session.commit()

    self.load_accounts()
    self.load_contacts()
    self.load_opportunities()
    self.load_leads()

    self.load_files("dummy_files")
    self.load_files("extra_files")

    self.db.session.commit()

  def load_users(self):
    reader = self.get_reader("Users.csv")
    for line in reader:
      d = {}
      for col in ['first_name', 'last_name', 'email', 'password', 'job_title']:
        d[col] = line[col]

      user = User(**d)
      photo_path = os.path.join(os.path.dirname(__file__),
                                "user_photos",
                                d['last_name'].lower() + ".jpg")
      user.photo = open(photo_path).read()
      self.db.session.add(user)
      self.users.append(user)

  def load_accounts(self):
    reader = self.get_reader("Accounts.csv")
    for line in reader:
      g.user = choice(self.users)
      d = {}
      for col in ['Name', 'Website', 'Office Phone', 'Type', 'Industry']:
        d[col.lower().replace(" ", "_")] = line[col]
      for k in ['Street', 'City', 'State', 'Country']:
        d["address_" + k.lower()] = line["Billing %s" % k]
      if d['website'] and not d['website'].startswith("http://"):
        d['website'] = "http://" + d['website']
      account = Account(**d)
      self.db.session.add(account)
      self.accounts_map[line['Name']] = account

  def load_contacts(self):
    reader = self.get_reader("Contacts.csv")
    for line in reader:
      g.user = choice(self.users)
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
    for line in reader:
      g.user = choice(self.users)
      d = {}
      for col in ['Name', 'Description', 'Type']:
        d[col.lower().replace(" ", "_")] = line[col]
      d['stage'] = line['Sales Stage']
      d['amount'] = line['Opportunity Amount'][3:]
      d['close_date'] = self.parse_date(line['Expected Close Date'])
      d['probability'] = line['Probability (%)']
      opportunity = Opportunity(**d)

      account = self.accounts_map.get(line['Account Name'])
      if not account:
        print "Skipping account", line['Account Name']
        continue
      opportunity.account = account

      self.db.session.add(opportunity)

  def load_leads(self):
    reader = self.get_reader("Leads.csv")
    for line in reader:
      g.user = choice(self.users)
      d = {}
      d['email'] = line['Email Address']
      d['job_title'] = line['Title']
      for col in ['First Name', 'Last Name', 'Department', 'Account Name']:
        d[col.lower().replace(" ", "_")] = line[col]

      for k in ['Street', 'City', 'State', 'Country']:
        d["address_" + k.lower()] = line["Primary Address %s" % k]
      lead = Lead(**d)
      self.db.session.add(lead)

  def load_files(self, directory):
    dir_path = os.path.join(os.path.dirname(__file__), directory)
    if not os.path.isdir(dir_path):
      print "Skipping non-existing dir", directory
      return

    file_names = os.listdir(dir_path)
    for fn in file_names:
      if fn.startswith("."):
        continue

      print fn

      g.user = choice(self.users)
      path = os.path.join(dir_path, fn)
      name = unicode(fn, errors="replace")
      data = open(path).read()
      mime_type = mimetypes.guess_type(fn)[0]

      f = File(name, data, mime_type)
      self.db.session.add(f)


# Utilities
  @staticmethod
  def get_reader(filename):
    path = os.path.join(os.path.dirname(__file__), "dummy_data", filename)
    return csv.DictReader(open(path))

  @staticmethod
  def parse_date(str):
    day = int(str[0:2])
    month = int(str[3:5])
    year = int(str[6:10])
    return datetime.date(year, month, day)


def load_data(db):
  loader = DataLoader(db)
  loader.load_data()
