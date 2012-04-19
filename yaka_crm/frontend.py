import cgi
import re
from jinja2._markupsafe import Markup

from flask.templating import render_template
from flask.blueprints import Blueprint

from .entities import *


#
# Helper classes
#
class BreadCrumbs(object):

  def __init__(self, l=()):
    self._bc = []
    for path, label in l:
      self.add(path, label)

  def add(self, path="", label=""):
    if path != "" and not path.startswith("/"):
      previous = self._bc[-1]
      path = previous['path'] + "/" + path
    self._bc.append(dict(path=path, label=label))

  def __getitem__(self, item):
    return self._bc[item]


#
# UI model classes
#
class EntityListModel(object):
  """Wraps a list of entities for presentation by a TableView."""

  # TODO: not used for now

  def __init__(self, entity_list):
    self.entity_list = entity_list


class SingleEntityModel(object):
  """Wraps an entity for presentation by a SingleView."""

  # TODO: not used for now

  def __init__(self, entity):
    self.entity = entity


#
# UI views
#
class TableView(object):
  def __init__(self, columns):
    self.columns = columns

  def render(self, model):
    table = []
    for entity in model:
      table.append(self.render_line(entity))

    return Markup(render_template('render_table.html', table=table, column_names=self.columns))

  def render_line(self, entity):
    line = []
    for column_name in self.columns:
      value = getattr(entity, column_name)
      if column_name == 'name':
        cell = Markup('<a href="%s">%s</a>' % (entity.url, cgi.escape(value)))
      elif isinstance(value, Entity):
        cell = Markup('<a href="%s">%s</a>' % (value.url, cgi.escape(value.name)))
      else:
        cell = str(value)
      line.append(cell)
    return line


class SingleView(object):
  def __init__(self, *panels):
    self.panels = panels

  def render(self, model):
    def get(panel, row=None, col=None):
      return self.get(model, panel, row, col)
    return Markup(render_template('render_single.html', panels=self.panels, get=get))

  def get(self, model, panel, row=None, col=None):
    panel_index = self.panels.index(panel)
    panel = self.panels[panel_index]

    if row is None:
      return panel

    row_index = panel.rows.index(row)
    row = panel.rows[row_index]

    if col is None:
      return row

    attr_name = row.cols[col]
    return getattr(model, attr_name)


#
# Used to describe single entity views.
#
class Panel(object):
  def __init__(self, label=None, *rows):
    self.label = label
    self.rows = rows

  def __iter__(self):
    return iter(self.rows)

  def __getitem__(self, item):
    return self.rows[item]

  def __len__(self):
    return len(self.rows)


class Row(object):
  def __init__(self, *cols):
    self.cols = cols

  def __iter__(self):
    return iter(self.cols)

  def __getitem__(self, item):
    return self.cols[item]

  def __len__(self):
    return len(self.cols)


def expose(url='/', methods=('GET',)):
  """
      Use this decorator to expose views in your view classes.

      `url`
          Relative URL for the view
      `methods`
          Allowed HTTP methods. By default only GET is allowed.
  """
  def wrap(f):
    if not hasattr(f, '_urls'):
      f._urls = []
    f._urls.append((url, methods))
    return f

  return wrap


def labelize(s):
  return " ".join([ w.capitalize() for w in s.split("_") ])


class ModuleMeta(type):
  """
      Module metaclass.

      Does some precalculations (like getting list of view methods from the class) to avoid
      calculating them for each view class instance.
  """
  def __init__(cls, classname, bases, fields):
    type.__init__(cls, classname, bases, fields)

    # Gather exposed views
    cls._urls = []
    cls._default_view = None

    for p in dir(cls):
      attr = getattr(cls, p)

      if hasattr(attr, '_urls'):
        # Collect methods
        for url, methods in attr._urls:
          cls._urls.append((url, p, methods))

          if url == '/':
            cls._default_view = p

        # Wrap views
        #setattr(cls, p, _wrap_view(attr))


class Module(object):

  __metaclass__ = ModuleMeta

  endpoint = None
  label = None
  managed_class = None
  list_view = None
  list_view_columns = []
  single_view = None
  url = None
  name = None
  static_folder = None

  _urls = []


  def __init__(self):
    # If endpoint name is not provided, get it from the class name
    if self.endpoint is None:
      self.endpoint = self.__class__.__name__.lower()

    if self.label is None:
      self.label = labelize(self.endpoint)


  def create_blueprint(self, crud_app):
    """
        Create Flask blueprint.
    """
    # Store admin instance
    self.crud_app = crud_app

    # If url is not provided, generate it from endpoint name
    if self.url is None:
      self.url = '%s/%s' % (self.crud_app.url, self.endpoint)
    else:
      if not self.url.startswith('/'):
        self.url = '%s/%s' % (self.crud_app.url, self.url)

    # If name is not provided, use capitalized endpoint name
    if self.name is None:
      self.name = self._prettify_name(self.__class__.__name__)

    # Create blueprint and register rules
    self.blueprint = Blueprint(self.endpoint, __name__,
                               url_prefix=self.url,
                               template_folder='templates',
                               static_folder=self.static_folder)

    for url, name, methods in self._urls:
      self.blueprint.add_url_rule(url,
                                  name,
                                  getattr(self, name),
                                  methods=methods)

    self.managed_class.base_url = self.url

    return self.blueprint

  @expose("/")
  def list_view(self):
    bc = BreadCrumbs()
    bc.add("/", "Home")
    bc.add("", self.label)

    entities = self.managed_class.query.all()

    table_view = TableView(self.list_view_columns)
    rendered_table = table_view.render(entities)

    return render_template('list_view.html', rendered_table=rendered_table, breadcrumbs=bc, module=self)

  @expose("/<int:entity_id>")
  def entity_view(self, entity_id):
    bc = BreadCrumbs()
    bc.add("/", "Home")
    bc.add("/crm/" + self.endpoint, self.label)

    entity = self.managed_class.query.get(entity_id)
    bc.add("", entity.display_name)

    rendered_entity = self.single_view.render(entity)
    print rendered_entity
    return render_template('single_view.html', rendered_entity=rendered_entity, breadcrumbs=bc, module=self)

  @staticmethod
  def _prettify_name(name):
    """
        Prettify class name by splitting name by capital characters.
        So, 'MySuperClass' will look like 'My Super Class'

        `name`
            String to prettify
    """
    return re.sub(r'(?<=.)([A-Z])', r' \1', name)


class CRUD(object):

  def __init__(self, app, modules=None):
    if modules:
      self.modules = modules
    self.app = app

    for module in self.modules:
      self.add_module(module)

  def add_module(self, module):
    self.app.register_blueprint(module.create_blueprint(self))
    #self._add_view_to_menu(view)

  @property
  def breadcrumbs(self):
    return [dict(path='/', label='Home')]


# Specific classes

class Accounts(Module):
  managed_class = Account

  list_view_columns = ('name', 'website', 'type', 'industry')

  single_view = SingleView(
    Panel('Overview',
          Row('name', 'website'),
          Row('office_phone')),
    Panel('More information',
          Row('type', 'industry')),
    )


class Contacts(Module):
  managed_class = Contact

  list_view_columns = ('full_name', 'account', 'job_title', 'department', 'email')

  single_view = SingleView(
    Panel('Overview',
          Row('full_name'),
          Row('description')),
    Panel('More information',
          Row('department', 'email')),
    )


class Leads(Module):
  managed_class = Lead

  list_view_columns = ('full_name', 'job_title', 'department', 'email')

  single_view = SingleView(
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email')),
    )


class Opportunities(Module):
  managed_class = Opportunity

  list_view_columns = ('name',)

  single_view = SingleView(
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email')),
    )


class CRM(CRUD):
  modules = [Accounts(), Contacts(), Opportunities(), Leads()]

  url = "/crm"
