from flask.ext.wtf import Form, TextField, BooleanField, PasswordField
from flask.ext.wtf import Required


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class CreateForm(Form):
    username = TextField('Username', validators=[Required()])
    email = TextField('E-mail', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    password_verify = PasswordField('Password Again', validators=[Required()])
