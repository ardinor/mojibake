# -*- coding: utf-8 -*-

'''Entry point to all things to avoid circular imports.'''
from mojibake.app import app, db, models # celery

from mojibake.views import *

from mojibake.views.archive import archive
from mojibake.views.base import base
from mojibake.views.tags import tag
from mojibake.views.categories import category
from mojibake.views.posts import posts
from mojibake.views.bans import bans
from mojibake.projects.views import projects

app.register_blueprint(base)
app.register_blueprint(archive, url_prefix='/archive')
app.register_blueprint(tag, url_prefix='/tags')
app.register_blueprint(category, url_prefix='/categories')
app.register_blueprint(posts, url_prefix='/posts')
app.register_blueprint(bans, url_prefix='/bans')
app.register_blueprint(projects, url_prefix='/projects')

