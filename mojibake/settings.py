# -*- coding: utf-8 -*-
import os

VERSION = 1.0

DEBUG = True

POSTS_PER_PAGE = 3

# Assumes the app is located in the same directory
# where this file resides
APP_DIR = os.path.dirname(os.path.abspath(__file__))
# Directory to where the site will log to
SITE_LOG_DIR = ''

LANGUAGES = {
    'en': 'English',
    'ja': '日本語'
}

# Celery settings
CELERY_BROKER_URL = 'amqp:guest:guest//localhost'

def parent_dir(path):
    '''Return the parent of a directory.'''
    return os.path.abspath(os.path.join(path, os.pardir))

if DEBUG:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_DIR, 'app.db')
    TEST_DATABASE = 'sqlite:///' + os.path.join(APP_DIR, 'test.db')
    #print(base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes))
    SECRET_KEY = 'SecretKeyGoesHere'
else:
    #from mojibake.main import app
    import configparser
    credentials_file = ''
    #config = configparser.ConfigParser()
    #config.read(credentials_file)
    #username = config.get("credentials", "username")
    #password = config.get("credentials", "password")
    #SQLALCHEMY_DATABASE_URI = "mysql:///" + username + ":" + password + "@localhost/mojibake"
    SQLALCHEMY_DATABASE_URI = "mysql+oursql://jordan@localhost/mojibake"
    #SECRET_KEY = config.get("credentials", "secret_key")
    SECRET_KEY = "Key goes here"

    import logging
    from logging.handlers import RotatingFileHandler
    # Set the size limit to 50~mb
    file_handler = RotatingFileHandler('mojibake.log', maxBytes=1024 * 1024 * 50, backupCount=5)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
    ))
    #app.logger.addHandler(file_handler)
