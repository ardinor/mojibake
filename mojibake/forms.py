# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import TextField, BooleanField, PasswordField, \
    TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Length
from flask.ext.babel import gettext


class LoginForm(Form):
    username = TextField('Username', validators=[DataRequired(gettext('Enter valid username'))])
    password = PasswordField('Password', validators=[DataRequired(gettext('Enter valid password'))])
    remember_me = BooleanField('remember_me', default=False)


class PostForm(Form):
    title = TextField(gettext('Title (en)'), id='post_title', validators=[DataRequired(gettext('Enter a title')), Length(max=255)])
    title_ja = TextField(gettext('Title (ja)'), id='post_title_ja', validators=[Length(max=255)])
    slug = TextField('Slug', id='post_slug', validators=[DataRequired(gettext('Enter a slug')), Length(max=255)])
    body = TextAreaField('Body', id='post_body')
    body_ja = TextAreaField('本文', id='post_body_ja')
    # Doesn't accept no date?
    date = DateTimeField(gettext('Published date'), id='post_date', format='%d-%m-%Y %H:%M')
    category = TextField(gettext('Category'), id='post_category')
    category_ja = TextField(gettext('Category (ja)'), id='post_category_ja')
    tags = TextField(gettext('Tags (en)'), id='post_tags')
    tags_ja = TextField(gettext('Tags (ja)'), id='post_tags_ja')
    published = BooleanField(gettext('Publish'))
