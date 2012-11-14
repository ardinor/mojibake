from flask import Flask
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config['MONGODB_DB'] = 'mojibake'
app.config['SECRET_KEY'] = 'SecretKeyGoesHere'

db = MongoEngine(app)

from mojibake import views
