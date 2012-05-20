from . import app
from datetime import datetime


@app.template_filter('labelize')
def labelize(s):
  return " ".join([ w.capitalize() for w in s.split("_") ])


@app.template_filter('filesize')
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


@app.template_filter('age')
def age(dt, now=None):
  # Fail silently for now XXX
  if not dt:
    return ""

  if not now:
    now = datetime.utcnow()

  age = now - dt
  if age.days == 0:
    if age.seconds < 120:
      age_str = "a minute ago"
    elif age.seconds < 3600:
      age_str = "%d minutes ago" % (age.seconds / 60)
    elif age.seconds < 7200:
      age_str = "an hour ago"
    else:
      age_str = "%d hours ago" % (age.seconds / 3600)
  else:
    if age.days == 1:
      age_str = "yesterday"
    elif age.days <= 31:
      age_str = "%d days ago" % age.days
    elif age.days <= 72:
      age_str = "a month ago"
    elif age.days <= 365:
      age_str = "%d months ago" % (age.days / 30)
    else:
      age_str = "%d years ago" % (age.days / 365)

  return age_str


@app.template_filter('date_age')
def date_age(dt, now=None):
  # Fail silently for now XXX
  if not dt:
    return ""
  age_str = age(dt, now)
  return "%s (%s)" % (dt.strftime("%Y-%m-%d %H:%M"), age_str)


@app.template_filter('abbrev')
def abbrev(s, max_size):
  if len(s) <= max_size:
    return s
  else:
    h = max_size / 2 - 1
    return s[0:h] + "..." + s[-h:]