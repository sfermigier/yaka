class Env(dict):

  def __init__(self, label=None, **kw):
    #self.bread_crumbs = self.breadcrumbs = make_bread_crumbs(label=label)
    for key, value in kw.items():
      self[key] = value

  def __setattr__(self, key, value):
    self[key] = value
