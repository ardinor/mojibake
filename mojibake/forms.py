# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import TextField, BooleanField, PasswordField, \
    TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Length
from flask.ext.babel import gettext


class LoginForm(Form):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class PostForm(Form):
    title = TextField(gettext('Title (en)'), id='post_title', validators=[DataRequired(), Length(max=255)])
    title_ja = TextField(gettext('Title (ja)'), id='post_title_ja', validators=[Length(max=255)])
    slug = TextField('Slug', id='post_slug', validators=[DataRequired(), Length(max=255)])
    body = TextAreaField('Body', id='post_body')
    body_ja = TextAreaField('本文', id='post_body_ja')
    date = DateTimeField(gettext('Published date'), id='post_date', format='%d-%m-%Y')
    category = TextField(gettext('Category'), id='post_category')
    category_ja = TextField(gettext('Category (ja)'), id='post_category_ja')
    tags = TextField(gettext('Tags (en)'), id='post_tags')
    tags_ja = TextField(gettext('Tags (ja)'), id='post_tags_ja')
    published = BooleanField(gettext('Publish'))


class TranslateForm(Form):
    title = TextField('Title')
