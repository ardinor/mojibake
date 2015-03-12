# -*- coding: utf-8 -*-
import os

VERSION = 1.0

PORT = 8000

LOGGER_NAME = 'mojibake'

DEBUG = False

POSTS_PER_PAGE = 3

# Assumes the app is located in the same directory
# where this file resides
APP_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_DIR = '/opt/mojibake/logs/current'

LANGUAGES = {
    'en': 'English',
    'ja': '日本語'
}

def parent_dir(path):
    '''Return the parent of a directory.'''
    return os.path.abspath(os.path.join(path, os.pardir))

if DEBUG:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_DIR, 'app.db')
    TEST_DATABASE = 'sqlite:///' + os.path.join(APP_DIR, 'test.db')
    # To get a good secret key
    #   print(base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes))
    SECRET_KEY = 'SecretKeyGoesHere'
    # How many times an IP is seen trying to breakin before it is considered
    # 'common'. Common IPs will be listed in the
    COMMON_IP_COUNT = 3
    LOG_DIR = APP_DIR
else:
    USERNAME = 'username'
    PASSWORD = 'password'
    #SQLALCHEMY_DATABASE_URI = "mysql:///" + username + ":" + password + "@localhost/mojibake"
    SQLALCHEMY_DATABASE_URI = "mysql+oursql://" + username + ":" + password + "@localhost/mojibake"
    # On the prod server the wait-timeout is currently set to 600
    SQLALCHEMY_POOL_RECYCLE = 500
    SECRET_KEY = 'SecretKeyGoesHere'
    COMMON_IP_COUNT = 6
