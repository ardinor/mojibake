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

CELERY_BROKER_URL = 'amqp://localhost'

def parent_dir(path):
    '''Return the parent of a directory.'''
    return os.path.abspath(os.path.join(path, os.pardir))

if DEBUG:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_DIR, 'app.db')
    TEST_DATABASE = 'sqlite:///' + os.path.join(APP_DIR, 'test.db')
    #print(base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes))
    SECRET_KEY = 'SecretKeyGoesHere'
else:
    import configparser
    credentials_file = ''
    config = configparser.ConfigParser()
    config.read(credentials_file)
    username = config.get("credentials", "username")
    password = config.get("credentials", "password")
    SQLALCHEMY_DATABASE_URI = "mysql:///" + username + ":" + password + "@localhost/mojibake"
    SECRET_KEY = config.get("credentials", "secret_key")

    import logging
    from logging.handlers import RotatingFileHandler
    # Set the size limit to 50~mb
    file_handler = RotatingFileHandler('mojibake.log', maxBytes=1024 * 1024 * 50, backupCount=5)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)

### Settings for auth_log_parser ###
HOST_SERVER_NAME = 'defestri'
LOG_DIR = '/var/log/'

# Search string for the usual invalid user login attempts from /var/log/auth.log
# Jun 10 12:40:05 defestri sshd[11019]: Invalid user admin from 61.174.51.217
SEARCH_STRING = '(?P<log_date>^.*) {server} sshd.*Invalid user (?P<user>.*) from (?P<ip_add>\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}})'.format(server=HOST_SERVER_NAME)
# Search string for root login attempts from /var/log/auth.log
# Jun  8 04:31:10 defestri sshd[5013]: User root from 116.10.191.234 not allowed because none of user's groups are listed in AllowGroups
ROOT_NOT_ALLOWED_SEARCH_STRING = '(?P<log_date>^.*) {server} sshd.*User (?P<user>.*) from (?P<ip_add>\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}}) not allowed'.format(server=HOST_SERVER_NAME)
# Search string for fail2ban banning repeat offenders as logged in /var/log/fail2ban.log
# 2014-06-10 12:40:07,363 fail2ban.actions: WARNING [ssh] Ban 61.174.51.217
FAIL2BAN_SEARCH_STRING = '(?P<log_date>^.*) fail2ban.actions: WARNING \[ssh] Ban (?P<ip_add>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

API_URL = 'http://api.ipinfodb.com/v3/ip-city/'
API_KEY = ''
### End auth_log_parser settings ###
