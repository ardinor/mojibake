# -*- coding: utf-8 -*-

from flask import Flask
#from flask_flatpages import FlatPages
#from flask_frozen import Freezer
from flask.ext.assets import Environment, Bundle
from flask.ext.sqlalchemy import SQLAlchemy
#from flask.ext.script import Manager
#from flask.ext.migrate import Migrate, MigrateCommand

from moment_js import moment_js
#from manage_db import ManageMetaDB

app = Flask(__name__)
app.config.from_pyfile('settings.py')
#pages = FlatPages(app)
#freezer = Freezer(app)
db = SQLAlchemy(app)
#migrate = Migrate(app, db)

from mojibake import models

#manager = Manager(app)
#manager.add_command('db', MigrateCommand)
#manager.add_command('manage_db', ManageMetaDB(db, pages, models))

app.jinja_env.globals['moment_js'] = moment_js

# This causes an error if you try and run it before the DB is initialised...
app.jinja_env.globals['glbl_categories'] = models.Category.query.order_by('name').all()

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

new_js = Bundle('js/jquery.min.js',
                'js/skel.min.js',
                'js/skel-panels.min.js',
                'js/init.js',
                'js/mojibake.js')
assets.register('new_js', new_js)

ie8_shiv = Bundle('js/html5shiv.js')
assets.register('ie8_shiv', ie8_shiv)

new_css = Bundle('css/skel-noscript.css',
                 'css/style.css',
                 'css/style-wide.css')
assets.register('new_css', new_css)

ie8_css = Bundle('css/ie8.css')
assets.register('ie8_css', ie8_css)

ie9_css = Bundle('css/ie9.css')
assets.register('ie9_css', ie9_css)

#Moment needs to be in the document head apparently
moment = Bundle('js/moment.min.js')
assets.register('js_moment', moment)
