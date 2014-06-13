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

app.register_blueprint(base)
app.register_blueprint(archive)
app.register_blueprint(tag)
app.register_blueprint(category)
app.register_blueprint(posts)
app.register_blueprint(bans)

