# -*- coding: utf-8 -*-

from wtforms import Form, TextField, PasswordField, validators
from wtforms.validators import required


class LoginForm(Form):
    username = TextField('User name', validators=[required()])
    password = PasswordField('Password', validators=[required()])
