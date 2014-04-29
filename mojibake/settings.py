# -*- coding: utf-8 -*-
import os

VERSION = 1.0

DEBUG = True

POSTS_PER_PAGE = 3

# Assumes the app is located in the same directory
# where this file resides
APP_DIR = os.path.dirname(os.path.abspath(__file__))

def parent_dir(path):
    '''Return the parent of a directory.'''
    return os.path.abspath(os.path.join(path, os.pardir))

FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite']
FLATPAGES_ROOT = os.path.join(APP_DIR, 'content')
FLATPAGES_EXTENSION = '.md'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_DIR, 'app.db')
TEST_DATABASE = 'sqlite:///' + os.path.join(APP_DIR, 'test.db')

LANGUAGES = {
    'en': 'English',
    'ja': u'日本語'
}

SECRET_KEY = 'SecretKeyGoesHere'
