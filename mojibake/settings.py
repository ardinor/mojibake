# -*- coding: utf-8 -*-
import os
import configparser

VERSION = 1.0

DEBUG = True

POSTS_PER_PAGE = 3

# Assumes the app is located in the same directory
# where this file resides
APP_DIR = os.path.dirname(os.path.abspath(__file__))

def parent_dir(path):
    '''Return the parent of a directory.'''
    return os.path.abspath(os.path.join(path, os.pardir))

if DEBUG:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_DIR, 'app.db')
    TEST_DATABASE = 'sqlite:///' + os.path.join(APP_DIR, 'test.db')
else:
    config = configparser.ConfigParser()
    config.read("")
    username = config.get("credentials", "username")
    password = config.get("credentials", "password")
    SQLALCHEMY_DATABASE_URI = 'mysql:///' + username + ':' + password + '@localhost/mojibake')

LANGUAGES = {
    'en': 'English',
    'ja': '日本語'
}

#print(base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes))
SECRET_KEY = 'SecretKeyGoesHere'
