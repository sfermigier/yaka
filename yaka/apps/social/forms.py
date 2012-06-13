from flaskext.wtf import Form, HiddenField, IntegerField, Length, RadioField,\
  SelectField, SubmitField, TextField, required

from flaskext.babel import lazy_gettext as _


class GroupForm(Form):

  name = TextField(_("Name"),
                   validators=[required(message=_("Name is required."))])

  description = TextField(_("Description"))
