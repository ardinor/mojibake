from flask.ext.wtf import Form, TextField, BooleanField, PasswordField
from flask.ext.wtf.html5 import EmailField
from flask.ext.wtf import Required, Length


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class CreateUserForm(Form):
    username = TextField('Username', validators=[Required(), Length(max=50)])
    email = EmailField('E-mail', validators=[Required(), Length(max=255)])
    password = PasswordField('Password', validators=[Required()])
    password_verify = PasswordField('Password Again', validators=[Required()])


class PostForm(Form):
    title = TextField('Title', validators=[Required(), Length(max=255)])
    slug = TextField('Slug', validators=[Required(), Length(max=255)])
    body = TextField('Body', validators=[Required()])
    visible = BooleanField('Visible')
    tags = TextField('Tags')


class CommentForm(Form):
    author = TextField('Author', validators=[Required(), Length(max=50)])
    email = EmailField('E-mail', validators=[Required(), Length(max=255)])
    body = TextField('Comment', validators=[Required()])
