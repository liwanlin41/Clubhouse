# login forms and other web forms

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    user = StringField(_l('Username'), validators = [DataRequired()])
    password = StringField(_l('Password'), validators = [DataRequired()])
    remember = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

#class CheckinForm(FlaskForm):
    # SelectField is the one that has an entire box with all possible options
    # sample syntax:
    # members = [(id, _l("name"))] as list of tuples
    # first in tuple is the value submitted to the form
    # second in tuple is displayed to user
    # sample_field = SelectField(_l("display name"), choices = members, validators = [DataRequired()])
