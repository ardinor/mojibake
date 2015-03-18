# -*- coding: utf-8 -*-
import os

VERSION = 1.0

PORT = 8000

LOGGER_NAME = 'mojibake'

DEBUG = True

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
    TEST_DATABASE_URI = 'sqlite:///' + os.path.join(APP_DIR, 'test.db')
    # To get a good secret key
    #   print(base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes))
    SECRET_KEY = 'SecretKeyGoesHere'
    # How many times an IP is seen trying to breakin before it is considered
    # 'common'. Common IPs will be listed in the
    COMMON_IP_COUNT = 3
    LOG_DIR = APP_DIR
else:
    import configparser
    credentials_file = '/var/lib/mojibake/.mojibake_settings'
    config = configparser.ConfigParser()
    config.read(credentials_file)
    USERNAME = config.get("credentials", "USERNAME")
    PASSWORD = config.get("credentials", "PASSWORD")
    SECRET_KEY = config.get("credentials", "SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = "mysql+oursql://" + USERNAME + ":" + PASSWORD + "@mojibakedb/mojibake"
    TEST_DATABASE_URI = "mysql+oursql://" + USERNAME + ":" + PASSWORD + "@mojibakedb/mojibake_test"

    # On the prod server the wait-timeout is currently set to 600
    SQLALCHEMY_POOL_RECYCLE = 500
    COMMON_IP_COUNT = 6
