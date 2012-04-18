import re

from flask.templating import render_template
from flask.blueprints import Blueprint

from .entities import *


#
# View classes
#
class Table(object):
  def __init__(self, viewer, entities):
    self.viewer = viewer
    self.entities = entities

  @property
  def column_names(self):
    return self.viewer.column_names

  def __getitem__(self, item):
    return Line(self.viewer, self.entities[item])


class Line(object):
  def __init__(self, viewer, entity):
    self.viewer = viewer
    self.entity = entity

  @property
  def uid(self):
    return self.entity.uid

  @property
  def url(self):
    return "/crm/accounts/%d" % self.entity.uid

  @property
  def column_names(self):
    return self.viewer.column_names

  def __getitem__(self, item):
    if type(item) == int:
      if item >= len(self.column_names):
        raise IndexError
      name = self.column_names[item]
      return Cell(self.viewer, name, getattr(self.entity, name))
    else:
      cells = []
      for i in range(*item.indices(len(self.column_names))):
        name = self.column_names[i]
        cells += [Cell(self.viewer, name, getattr(self.entity, name))]
        print cells
      return cells


class Cell(object):
  def __init__(self, viewer, name, value):
    self.viewer = viewer
    self.name = name
    self.value = value

  def __str__(self):
    if not self.value:
      return ""
    elif isinstance(self.value, Entity):
      return Markup('<a href="/tab/%s/%d">%s</a>' % (
        self.value.__tab__, self.value.uid, cgi.escape(self.value.display_name)
        ))
    else:
      return str(self.value)


class ListViewer(object):

  _column_names = None

  def __init__(self, *columns):
    self.columns = columns

  @property
  def column_names(self):
    if not self._column_names:
      column_names = []
      for c in self.columns:
        if type(c) == str:
          column_names += [c]
        else:
          column_names += [c.name]
      self._column_names = column_names
    return self._column_names

  def view(self, entities):
    return Table(self, entities)


class SingleView(object):
  def __init__(self, viewer, entity):
    self.viewer = viewer
    self.entity = entity

  @property
  def panels(self):
    return self.viewer.panels

  def get(self, panel, row=None, col=None):
    panel_index = self.viewer.panels.index(panel)
    panel = self.viewer.panels[panel_index]

    if row is None:
      return panel

    row_index = panel.rows.index(row)
    row = panel.rows[row_index]

    if col is None:
      return row

    attr_name = row.cols[col]
    return getattr(self.entity, attr_name)


class SingleViewer(object):
  def __init__(self, *panels):
    self.panels = panels

  def view(self, entity):
    return SingleView(self, entity)


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
  list_viewer = None
  single_viewer = None
  url = None
  name = None
  static_folder = None


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

    return self.blueprint

  @expose("/")
  def list_view(self):
    breadcrumbs = self.crud_app.breadcrumbs + [dict(path="", label=self.label)]
    entities = self.managed_class.query.all()
    table = self.list_viewer.view(entities)
    return render_template('list_view.html', table=table, breadcrumbs=breadcrumbs, module=self)

  @expose("/<int:entity_id>")
  def entity_view(self, entity_id):
    breadcrumbs = self.crud_app.breadcrumbs + [dict(path=self.endpoint, label=self.label)]

    entity = self.managed_class.query.get(entity_id)
    breadcrumbs += [dict(path="", label=entity.display_name)]
    view = self.single_viewer.view(entity)
    return render_template('single_view.html', view=view, breadcrumbs=breadcrumbs, module=self)

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

  list_viewer = ListViewer('name', 'website', 'type', 'industry')

  single_viewer = SingleViewer(
    Panel('Overview',
          Row('name', 'website'),
          Row('office_phone')),
    Panel('More information',
          Row('type', 'industry')),
    )


class Contacts(Module):
  managed_class = Contact

  list_viewer = ListViewer('full_name', 'account', 'job_title', 'department', 'email')

  single_viewer = SingleViewer(
    Panel('Overview',
          Row('full_name'),
          Row('description')),
    Panel('More information',
          Row('department', 'email')),
    )


class Leads(Module):
  managed_class = Lead

  list_viewer = ListViewer('full_name', 'job_title', 'department', 'email')
  single_viewer = SingleViewer(
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email')),
    )


class Opportunities(Module):
  managed_class = Opportunity

  list_viewer = ListViewer('name')

  single_viewer = SingleViewer(
    Panel('Overview',
          Row('first_name', 'last_name')),
    Panel('More information',
          Row('department', 'email')),
    )


class CRM(CRUD):
  modules = [Accounts(), Contacts(), Opportunities(), Leads()]

  url = "/crm"
