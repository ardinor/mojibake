#! /usr/bin/env python
# mojibake is a simple Flask blog
# Copyright (C) 2012 ardinor
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager

app = Flask(__name__)
app.config['MONGODB_DB'] = 'mojibake'
app.config['SECRET_KEY'] = 'SecretKeyGoesHere'

db = MongoEngine(app)

lm = LoginManager()
lm.setup_app(app)
lm.login_view = 'login'

from mojibake import views
