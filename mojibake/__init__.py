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
from flask.ext.assets import Environment, Bundle

from moment_js import moment_js

app = Flask(__name__)
app.config.from_object('config')


db = MongoEngine(app)

lm = LoginManager()
lm.setup_app(app)
lm.login_view = 'login'

app.jinja_env.globals['moment_js'] = moment_js

assets = Environment(app)

css = Bundle('vendor/css/bootstrap.min.css',
    'vendor/css/bootstrap-responsive.css',
    'vendor/css/jquery.pnotify.default.css',
    'vendor/css/bootstrap-wysihtml5-0.0.2.css',
    'vendor/css/jquery.tagsinput.css',
    'css/mojibake.css')
assets.register('css_all', css)

js = Bundle('vendor/js/bootstrap-scrollspy.js',
    'vendor/js/jquery-1.9.0.js',
    'vendor/js/jquery.pnotify.min.js',
    'vendor/js/bootstrap.min.js',
    'vendor/js/wysihtml5-0.3.0_rc2.min.js',
    'vendor/js/bootstrap-wysihtml5-0.0.2.min.js',
    'vendor/js/jquery.tagsinput.min.js',
    'vendor/js/moment.min.js',
    'js/mojibake.js')
assets.register('js_all', js)

from mojibake import views
