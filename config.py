# -*- coding: utf-8 -*-

VERSION = 1.0

DEBUG = True

REGISTRATION_OPEN = 1
REGISTRATION_CLOSED = 0

REGISTRATION = REGISTRATION_OPEN

CSRF_ENABLED = True

SECRET_KEY = 'SecretKeyGoesHere'

MONGODB_DB = 'mojibake'

POSTS_PER_PAGE = 2  # 5

LANGUAGES = {
    'en': 'English',
    'ja': u'日本語'
}

#Set this better
UPLOADED_PHOTOS_DEST = 'C:/git/mojibake/mojibake/static/img/upload'
