from datetime import datetime
from flaskext import babel
from flaskext.babel import gettext as _


def labelize(s):
  return " ".join([ w.capitalize() for w in s.split("_") ])

def filesize(d):
  if d < 1000:
    return "%d B" % d

  if d < 1e4:
    return "%.1f kB" % (d / 1e3)
  if d < 1e6:
    return "%.0f kB" % (d / 1e3)

  if d < 1e7:
    return "%.1f MB" % (d / 1e6)
  if d < 1e9:
    return "%.0f MB" % (d / 1e6)

  if d < 1e10:
    return "%.1f GB" % (d / 1e9)

  return "%.0f GB" % (d / 1e9)

def age(dt, now=None):
  # Fail silently for now XXX
  if not dt:
    return ""

  if not now:
    now = datetime.utcnow()

  age = now - dt
  if age.days == 0:
    if age.seconds < 120:
      age_str = _("a minute ago")
    elif age.seconds < 3600:
      age_str = _("%(num)d minutes ago", num=age.seconds / 60)
    elif age.seconds < 7200:
      age_str = _("an hour ago")
    else:
      age_str = _("%(num)d hours ago", num=age.seconds / 3600)
  else:
    if age.days == 1:
      age_str = _("yesterday")
    elif age.days <= 31:
      age_str = _("%(num)d days ago", num=age.days)
    elif age.days <= 72:
      age_str = _("a month ago")
    elif age.days <= 365:
      age_str = _("%(num)d months ago", num=age.days / 30)
    elif age.days <= 2*365:
      age_str = _("last year")
    else:
      age_str = _("%(num)d years ago", num=age.days / 365)

  return age_str

def date_age(dt, now=None):
  # Fail silently for now XXX
  if not dt:
    return ""
  age_str = age(dt, now)
  return "%s (%s)" % (dt.strftime("%Y-%m-%d %H:%M"), age_str)

def date(value):
  format="EE, d MMMM y"
  return babel.format_datetime(value, format)

def abbrev(s, max_size):
  if len(s) <= max_size:
    return s
  else:
    h = max_size / 2 - 1
    return s[0:h] + "..." + s[-h:]

def init_filters(app):
  app.jinja_env.filters['date_age'] = date_age
  app.jinja_env.filters['age'] = age
  app.jinja_env.filters['date'] = date

  app.jinja_env.filters['abbrev'] = abbrev
  app.jinja_env.filters['filesize'] = filesize
  app.jinja_env.filters['labelize'] = labelize

