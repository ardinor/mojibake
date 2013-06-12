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
from flask.ext.babel import Babel
from flask.ext.uploads import configure_uploads, IMAGES, \
    UploadSet, patch_request_class

from moment_js import moment_js
from available_languages import available_languages

from config import VERSION, DEBUG

app = Flask(__name__)
app.config.from_object('config')

db = MongoEngine(app)

lm = LoginManager()
lm.setup_app(app)
lm.login_view = 'login'

app.jinja_env.globals['moment_js'] = moment_js
app.jinja_env.globals['available_languages'] = available_languages

babel = Babel(app)

assets = Environment(app)

css = Bundle('vendor/css/bootstrap.min.css',
             'vendor/css/bootstrap-responsive.css',
             #'vendor/css/jquery.pnotify.default.css',
             #'vendor/css/bootstrap-wysihtml5-0.0.2.css',
             #'vendor/css/jquery.tagsinput.css',
             'css/mojibake.css',
             'css/zenburn.css')
assets.register('css_all', css)

js = Bundle('vendor/js/bootstrap-scrollspy.js',
            'vendor/js/jquery-1.9.0.js',
            'vendor/js/bootstrap.min.js',
            'vendor/js/moment/moment.min.js',
            'js/mojibake.js')
assets.register('js_all', js)

#The below js is only needed by logged in users, as such
#there's no need to load it for people just visiting
user_js = Bundle('vendor/js/wysihtml5-0.3.0_rc2.min.js',
                 #'vendor/js/bootstrap-wysihtml5-0.0.2.min.js',
                 'vendor/js/jquery.tagsinput.min.js',
                 'vendor/js/jquery.pnotify.min.js',
                 'js/mojibake_user.js')
assets.register('user_js', user_js)

ja_js = Bundle('vendor/js/moment/lang/ja.js')
assets.register('ja_js', ja_js)

user_css = Bundle('vendor/css/jquery.pnotify.default.css',
                  #'vendor/css/bootstrap-wysihtml5-0.0.2.css',
                  'vendor/css/jquery.tagsinput.css')
assets.register('user_css', user_css)

atom_icon = Bundle('img/feed.png')
assets.register('atom_icon', atom_icon)

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app, 8 * 1024 * 1024)

if not DEBUG:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/mojibake.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('Mojibake started - Version {}'.format(VERSION))

from mojibake import views
