# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel
from flask.ext.login import LoginManager

from mojibake.moment_js import moment_js
from mojibake.available_languages import available_languages

app = Flask(__name__)
app.config.from_pyfile('settings.py')
db = SQLAlchemy(app)
babel = Babel(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

from mojibake import models

app.jinja_env.globals['moment_js'] = moment_js
app.jinja_env.globals['available_languages'] = available_languages
app.jinja_env.trim_blocks = True
#app.jinja_env.lstrip_blocks = True

assets = Environment(app)
app.config['ASSETS_DEBUG'] = True

# css = Bundle('css/bootstrap.min.css',
#              'css/mojibake.css')
# assets.register('css_all', css)

# js = Bundle('js/jquery-2.0.3.min.js',
#             'js/bootstrap.min.js',
#             'js/mojibake.js',
#             filters='rjsmin', output='gen/packed.js')
# assets.register('js_all', js)

js = Bundle('js/jquery.min.js',
                'js/jquery-ui.custom.js',
                'js/skel.min.js',
                'js/skel-panels.min.js',
                'js/init.js',
                'js/mojibake.js')
assets.register('js', js)

ie8_shiv = Bundle('js/html5shiv.js')
assets.register('ie8_shiv', ie8_shiv)

css = Bundle('css/skel-noscript.css',
             'css/style.css',
             'css/style-wide.css',
             'css/jquery-ui-1.10.4.custom.css',
             'css/zenburn.css')
assets.register('css', css)

ie8_css = Bundle('css/ie8.css')
assets.register('ie8_css', ie8_css)

ie9_css = Bundle('css/ie9.css')
assets.register('ie9_css', ie9_css)

#Moment needs to be in the document head apparently
moment = Bundle('js/moment.min.js')
assets.register('js_moment', moment)

ja_js = Bundle('js/moment-ja.js')
assets.register('ja_js', ja_js)
