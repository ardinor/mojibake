# -*- coding: utf-8 -*-
import os

VERSION = 1.0

PORT = 8000

DEBUG = True

POSTS_PER_PAGE = 3

# Assumes the app is located in the same directory
# where this file resides
APP_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_DIR = '/opt/mojibake/logs/current'
# Directory to where the site will log to
SITE_LOG_DIR = ''

LANGUAGES = {
    'en': 'English',
    'ja': '日本語'
}

# Celery settings
#CELERY_BROKER_URL = 'amqp:guest:guest//localhost'

def parent_dir(path):
    '''Return the parent of a directory.'''
    return os.path.abspath(os.path.join(path, os.pardir))

if DEBUG:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_DIR, 'app.db')
    TEST_DATABASE = 'sqlite:///' + os.path.join(APP_DIR, 'test.db')
    #print(base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes))
    SECRET_KEY = 'SecretKeyGoesHere'
    # How many times an IP is seen trying to breakin before it is considered
    # 'common'. Common IPs will be listed in the
    COMMON_IP_COUNT = 3
else:
    #from mojibake.main import app
    import configparser
    credentials_file = '/home/mojibake/.mojibake_settings'
    config = configparser.ConfigParser()
    config.read(credentials_file)
    username = config.get("credentials", "username")
    password = config.get("credentials", "password")
    #SQLALCHEMY_DATABASE_URI = "mysql:///" + username + ":" + password + "@localhost/mojibake"
    SQLALCHEMY_DATABASE_URI = "mysql+oursql://" + username + ":" + password + "@localhost/mojibake"
    # On the prod server the wait-timeout is currently set to 600
    SQLALCHEMY_POOL_RECYCLE = 500
    SECRET_KEY = config.get("credentials", "secret_key")
    #SECRET_KEY = "Key goes here"
    COMMON_IP_COUNT = 6

    import logging
    from logging.handlers import TimedRotatingFileHandler
    # Set the size limit to 5~mb
    file_handler = TimedRotatingFileHandler(os.path.join(LOG_DIR, 'mojibake-flask.log'), when="D", backupCount=7)
    file_formatter = logging.Formatter("""
Time: %(asctime)s
Level: %(levelname)s
Method: %(method)s
Path: %(url)s
IP: %(ip)s
Message: %(message)s
-------------
""")

    file_handler.setLevel(logging.WARNING)
    #file_handler.setFormatter(logging.Formatter(
    #'%(asctime)s %(levelname)s: %(message)s '
    #'[in %(pathname)s:%(lineno)d]'
    #))
    file_handler.setFormatter(file_formatter)
    #app.logger.addHandler(file_handler)
