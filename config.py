# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

VERSION = 1.0

DEBUG = True

CSRF_ENABLED = True

SECRET_KEY = 'SecretKeyGoesHere'



POSTS_PER_PAGE = 2  # 5

LANGUAGES = {
    'en': 'English',
    'ja': u'日本語'
}

#Set this better
UPLOADED_PHOTOS_DEST = 'C:/git/mojibake/mojibake/static/img/upload'
#UPLOADED_FILES_URL = need to set up the url

UPLOAD_FOLDER = 'C:/git/mojibake/mojibake/static/img/upload'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', '.svg'])
