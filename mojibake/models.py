import datetime
from flask import url_for
from mojibake import db

ROLE_USER = 0
ROLE_STAFF = 1
ROLE_ADMIN = 2

STATUS_ACTIVE = 0
STATUS_INACTIVE = 1
STATUS_BANNED = 2

POST_VISIBLE = 0
POST_INVISIBLE = 1

COMMENT_AWAITING = 0
COMMENT_APPROVED = 1


class User(db.Document):
    username = db.StringField(max_length=50, required=True)
    email = db.StringField(max_length=255, required=True)
    password = db.StringField(required=True)
    role = db.IntField(default=ROLE_USER)
    status = db.IntField(default=STATUS_ACTIVE)
    posts = db.ReferenceField('Post')


class Post(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow, required=True)
    title = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
    body = db.StringField(required=True)
    visible = db.BooleanField(default=POST_VISIBLE)
    author = db.ReferenceField('User')
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))

    def get_absolute_url(self):
        return url_for('post', kwargs={'slug': self.slug})

    def __unicode__(self):
        return self.title

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


class Comment(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow, required=True)
    body = db.StringField(verbose_name='Comment', required=True)
    author = db.StringField(verbose_name='Name', max_length=50, required=True)
    email = db.StringField(verbose_name='E-mail', required=True)
    approved = db.BooleanField(default=COMMENT_AWAITING)
