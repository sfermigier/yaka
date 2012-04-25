from flaskext.wtf.form import Form
from flaskext.wtf.html5 import DateField
from wtforms.fields.simple import TextField
from wtforms.validators import Length, Email

from .entities import *
from .core.frontend import *


#
# Domain-specific application classes
#

# TODO: generate from View
class AccountEditForm(Form):
  name = TextField("Name", validators=[Length(min=3, max=50)])
  website = TextField("Website")
  office_phone = TextField("Office Phone")

  type = TextField("Type")
  industry = TextField("Industry")

  _groups = [
    ["Main", ['name', 'website', 'office_phone']],
    ["Additional information", ['type', 'industry']],
  ]

class Accounts(Module):
  managed_class = Account

  list_view_columns = [
    dict(name='name', width=25),
    dict(name='website', width=25),
    dict(name='type', width=25),
    dict(name='industry', width=24),
  ]

  single_view = SingleView(
    Panel('Overview',
          Row('name', 'website'),
          Row('office_phone')),
    Panel('More information',
          Row('type', 'industry')),
    )

  edit_form = AccountEditForm

  related_views = [
    ('Contacts', 'contacts', ('name', 'job_title', 'department')),
  ]


class ContactEditForm(Form):
  first_name = TextField("First Name")
  last_name = TextField("Last Name", validators=[Length(min=3, max=50)])
  description = TextField("Description")

  #account = TextField("Description")
  department = TextField("Department")
  email = TextField("email", validators=[Email()])

  _groups = [
    ["Main", ['first_name', 'last_name', 'description']],
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
    Panel('More information',
          Row('department', 'email')
          ),
    )

  edit_form = ContactEditForm


class LeadEditForm(Form):
  first_name = TextField("First Name")
  last_name = TextField("Last Name", validators=[Length(min=3, max=50)])
  description = TextField("Description")

  #account = TextField("Description")
  department = TextField("Department")
  email = TextField("email", validators=[Email()])

  _groups = [
    ["Main", ['first_name', 'last_name', 'description']],
    ["Additional information", ['department', 'email']],
  ]

class Leads(Module):
  managed_class = Lead

  list_view_columns = ('full_name', 'job_title', 'department', 'email')

  single_view = SingleView(
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email')),
    )

  edit_form = LeadEditForm


class OpportunityEditForm(Form):
  name = TextField("Name")
  type = TextField("Last Name")
  close_date = DateField("Close Date")

  _groups = [
    ["Main", ['name', 'type', 'close_date']],
  ]

class Opportunities(Module):
  managed_class = Opportunity

  list_view_columns = ('name',)

  single_view = SingleView(
    Panel('Overview',
          Row('name', 'type'),
          Row('close_date')),
    )

  edit_form = OpportunityEditForm


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
