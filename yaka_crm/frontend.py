from flaskext.uploads import UploadSet, IMAGES
from flaskext.wtf.file import FileField, file_allowed
from flaskext.wtf.form import Form
from flaskext.wtf.html5 import DateField, URLField, TelField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.core import SelectField
from wtforms.fields.simple import TextField, TextAreaField
from wtforms.validators import Length, Email, url

from .entities import *
from .core.frontend import *


#
# Domain-specific application classes
#
from yaka_crm.core.forms import Chosen

#
# Select lists choices
#
TYPES = ['', 'Analyst', 'Competitor', 'Customer', 'Integrator', 'Investor',
         'Press', 'Partner', 'Prospect', 'Reseller', 'Other']
INDUSTRIES = ['', "Apparel", "Banking", "Biotechnology", "Chemicals", "Communications",
              "Construction", "Consulting", "Education", "Electronics", "Energy",
              "Engineering", "Entertainment", "Environmental", "Finance", "Government",
              "Healthcare", "Hospitality", "Insurance", "Machinery", "Manufacturing",
              "Media", "Not For Profit", "Recreation", "Retail", "Shipping", "Technology",
              "Telecommunications", "Transportation", "Utilities", "Other"]

#
# Mixins for forms
#
class AddressForm(object):
  address_street = TextField("Street")
  address_city = TextField("City")
  address_state = TextField("State/Region")
  address_country = TextField("Country")


# TODO: generate all the forms automagically
class AccountEditForm(AddressForm, Form):
  name = TextField("Name", validators=[Length(min=3, max=50)])
  website = URLField("Website", validators=[url()])
  office_phone = TelField("Office Phone")

  type = SelectField("Type", choices=[ (x, x) for x in TYPES ])
  industry = SelectField("Industry", choices=[ (x, x) for x in INDUSTRIES ])

  logo = FileField("Logo", validators=[file_allowed(UploadSet("images", IMAGES), "Images only!")])

  _groups = [
    ["Main", ['name', 'website', 'office_phone', 'logo']],
    ["Address", ['address_street', 'address_city', 'address_state', 'address_country']],
    ["Additional information", ['type', 'industry']],
  ]

class Accounts(Module):
  managed_class = Account

  list_view_columns = [
    dict(name='name', width=35),
    dict(name='website', width=25),
    dict(name='type', width=20),
    dict(name='industry', width=14),
  ]

  single_view = SingleView(
    Panel('Overview',
          Row('name', 'website'),
          Row('office_phone')),
    Panel('Address',
          Row('address')),
    Panel('More information',
          Row('type', 'industry')),
    )

  edit_form = AccountEditForm

  related_views = [
    ('Contacts', 'contacts', ('name', 'job_title', 'department')),
    ('Opportunities', 'opportunities', ('name', 'type', 'amount', 'stage')),
  ]


def accounts():
  return Account.query.all()

class ContactEditForm(AddressForm, Form):
  first_name = TextField("First Name")
  last_name = TextField("Last Name", validators=[Length(min=3, max=50)])
  description = TextAreaField("Description")

  account = QuerySelectField("Account", widget=Chosen(), query_factory=accounts, allow_blank=True)

  department = TextField("Department")
  email = TextField("Email", validators=[Email()])

  _groups = [
    ["Main", ['first_name', 'last_name', 'description', 'account']],
    ["Address", ['address_street', 'address_city', 'address_state', 'address_country']],
    ["Additional information", ['department', 'email']],
  ]

class Contacts(Module):
  managed_class = Contact

  list_view_columns = ('name', 'account', 'job_title', 'department', 'email')

  single_view = SingleView(
    Panel('Overview',
          Row('name'),
          Row('description'),
          Row('account'),
          ),
    Panel('Address',
          Row('address')),
    Panel('More information',
          Row('department', 'email')
          ),
    )

  edit_form = ContactEditForm


class OpportunityEditForm(Form):
  name = TextField("Name")
  description = TextAreaField("Description")
  type = TextField("Type")
  stage = TextField("Stage")
  amount = IntegerField("Amount")
  probability = IntegerField("Probability")
  close_date = DateField("Close Date")

  account = QuerySelectField("Account", widget=Chosen(), query_factory=accounts, allow_blank=True)

  _groups = [
    ["Main", ['name', 'description', 'account', 'type', 'stage', 'amount', 'probability', 'close_date']],
  ]

class Opportunities(Module):
  managed_class = Opportunity

  list_view_columns = ('name', 'account', 'type', 'amount', 'stage')

  single_view = SingleView(
    Panel('Overview',
          Row('name', 'type'),
          Row('description'),
          Row('account'),
          Row('stage', 'amount'),
          Row('probability', 'close_date')))

  edit_form = OpportunityEditForm


class LeadEditForm(AddressForm, Form):
  first_name = TextField("First Name")
  last_name = TextField("Last Name", validators=[Length(min=3, max=50)])
  description = TextAreaField("Description")

  #account = TextField("Description")
  department = TextField("Department")
  email = TextField("email", validators=[Email()])

  _groups = [
    ["Main", ['first_name', 'last_name', 'description']],
    ["Address", ['address_street', 'address_city', 'address_state', 'address_country']],
    ["Additional information", ['department', 'email']],
  ]

class Leads(Module):
  managed_class = Lead

  list_view_columns = ('name', 'job_title', 'department', 'email')

  single_view = SingleView(
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('Address',
          Row('address')),
    Panel('More information',
          Row('department', 'email')),
    )

  edit_form = LeadEditForm


class Documents(Module):
  managed_class = Document

  list_view_columns = ('name', 'owner')

  single_view = SingleView(
    Panel('Overview',
          Row('name', 'owner')),
    )


class CRM(CRUDApp):
  modules = [Accounts(), Contacts(), Opportunities(), Leads(), Documents()]

  url = "/crm"
