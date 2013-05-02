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
    'ja': '日本語'
}
