# -*- coding: utf-8 -*-

'''Entry point to all things to avoid circular imports.'''
from mojibake.app import app, db, models, celery
from mojibake.views import *
