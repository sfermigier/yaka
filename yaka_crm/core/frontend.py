import cgi
import re

from flask import session, redirect, request, g, render_template, flash, Markup, Blueprint

from ..extensions import db
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


def add_to_recent_items(entity=None):
  g.recent_items.insert(0, dict(name=entity.name, url=entity.url))
  s = set()
  l = []
  for item in g.recent_items:
    if item['url'] in s:
      continue
    s.add(item['url'])
    l.append(item)
  if len(l) > 10:
    del l[10:]
  session['recent_items'] = g.recent_items = l


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
    self.init_columns(columns)
    self.name = id(self)

  def init_columns(self, columns):
    # TODO
    self.columns = []
    default_width = 0.99 / len(columns)
    for col in columns:
      if type(col) == str:
        self.columns.append(dict(name=col, width=default_width))
      else:
        self.columns.append(col)

  def render(self, model):
    columns = [ {'name': labelize(col['name']), 'width': col['width']} for col in self.columns ]
    table = []
    for entity in model:
      table.append(self.render_line(entity))

    return Markup(render_template('render_table.html', table=table, columns=columns,
                                  table_name=self.name))

  def render_line(self, entity):
    line = []
    for col in self.columns:
      if type(col) == str:
        column_name = col
      else:
        column_name = col['name']
      value = getattr(entity, column_name)
      if value is None:
        value = ""
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
    # TODO: refactor by passing a model instead
    def get(attr_name):
      return self.get(model, attr_name)
    return Markup(render_template('render_single.html', panels=self.panels, get=get))

  def render_form(self, form, for_new=False):
    return Markup(render_template('render_for_edit.html', form=form, for_new=for_new))

  def get(self, model, attr_name):
    value = getattr(model, attr_name)
    if value is None:
      return ""
    elif isinstance(value, Entity):
      return Markup('<a href="%s">%s</a>' % (value.url, cgi.escape(value.name)))
    else:
      return str(value)

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
  edit_form = None
  url = None
  name = None
  static_folder = None
  related_views = []

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

  #
  # Exposed views
  #
  @expose("/")
  def list_view(self):
    bc = self.bread_crumbs()

    entities = self.managed_class.query.all()

    table_view = TableView(self.list_view_columns)
    rendered_table = table_view.render(entities)

    return render_template('list_view.html', rendered_table=rendered_table, breadcrumbs=bc, module=self)

  @expose("/<int:entity_id>")
  def entity_view(self, entity_id):
    entity = self.managed_class.query.get(entity_id)
    bc = self.bread_crumbs(entity.name)
    add_to_recent_items(entity)

    rendered_entity = self.single_view.render(entity)
    related_views = self.render_related_views(entity)

    return render_template('single_view.html', rendered_entity=rendered_entity,
                           related_views=related_views, breadcrumbs=bc, module=self)

  @expose("/<int:entity_id>/edit")
  def entity_edit(self, entity_id):
    entity = self.managed_class.query.get(entity_id)
    bc = self.bread_crumbs(entity.name)
    add_to_recent_items(entity)

    form = self.edit_form(obj=entity)
    rendered_entity = self.single_view.render_form(form)

    return render_template('single_view.html', rendered_entity=rendered_entity,
                           breadcrumbs=bc, module=self)

  @expose("/<int:entity_id>/edit", methods=['POST'])
  def entity_edit_post(self, entity_id):
    entity = self.managed_class.query.get(entity_id)
    form = self.edit_form(obj=entity)

    if form.validate():
      flash("Entity successfully edited", "success")
      form.populate_obj(entity)
      db.session.commit()
      return redirect("%s/%d" % (self.url, entity_id))
    else:
      flash("Error", "error")
      rendered_entity = self.single_view.render_form(form)
      bc = self.bread_crumbs(entity.name)
      return render_template('single_view.html', rendered_entity=rendered_entity,
                             breadcrumbs=bc, module=self)

  @expose("/new")
  def entity_new(self):
    bc = self.bread_crumbs("New %s" % self.managed_class.__name__)

    form = self.edit_form()
    rendered_entity = self.single_view.render_form(form, for_new=True)

    return render_template('single_view.html', rendered_entity=rendered_entity,
                           breadcrumbs=bc, module=self)

  @expose("/new", methods=['PUT', 'POST'])
  def entity_new_put(self):
    form = self.edit_form()
    entity = self.managed_class()

    if form.validate():
      flash("Entity successfully edited", "success")
      form.populate_obj(entity)
      db.session.add(entity)
      db.session.commit()
      return redirect("%s/%d" % (self.url, entity.uid))
    else:
      flash("Error", "error")
      rendered_entity = self.single_view.render_form(form, for_new=True)
      bc = self.bread_crumbs("New %s" % self.managed_class.__name__)
      return render_template('single_view.html', rendered_entity=rendered_entity,
                             breadcrumbs=bc, module=self)

  @expose("/<int:entity_id>/delete")
  def entity_delete(self, entity_id):
    # TODO: don't really delete, switch state to "deleted"
    entity = self.managed_class.query.get(entity_id)
    db.session.delete(entity)
    db.session.commit()
    flash("Entity deleted", "success")
    return redirect(self.url)

  #
  # Utils
  #
  def is_current(self):
    return request.path.startswith(self.url)

  def bread_crumbs(self, label=None):
    bc = BreadCrumbs()
    bc.add("/", "Home")
    if label:
      bc.add("/crm/" + self.endpoint, self.label)
      bc.add("", label)
    else:
      bc.add("", self.label)
    return bc

  def render_related_views(self, entity):
    rendered = []
    for label, attr_name, column_names in self.related_views:
      view = TableView(column_names)
      related_entities = getattr(entity, attr_name)
      obj = dict(label=label, rendered=view.render(related_entities))
      rendered.append(obj)
    return rendered

  @staticmethod
  def _prettify_name(name):
    """
        Prettify class name by splitting name by capital characters.
        So, 'MySuperClass' will look like 'My Super Class'

        `name`
            String to prettify
    """
    return re.sub(r'(?<=.)([A-Z])', r' \1', name)


class CRUDApp(object):

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

