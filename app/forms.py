# login forms and other web forms

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    user = StringField(_l('Username'), validators = [DataRequired()])
    password = StringField(_l('Password'), validators = [DataRequired()])
    remember = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))
