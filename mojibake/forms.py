# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import TextField, BooleanField, PasswordField, \
    TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class PostForm(Form):
    title = TextField('Title', id='post_title', validators=[DataRequired(), Length(max=255)])
    slug = TextField('Slug', id='post_slug', validators=[DataRequired(), Length(max=255)])
    body = TextAreaField('Body', id='post_body')
    body_ja = TextAreaField('本文', id='post_body_ja')
    #visible = BooleanField('Visible')
    date = DateTimeField('Published date', id='post_date')
    category = TextField('Category', id='post_category')
    tags = TextField('Tags', id='post_tags')
