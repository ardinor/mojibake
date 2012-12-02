import datetime
from flask import url_for
from mojibake import db

ROLE_USER = 0
ROLE_STAFF = 1
ROLE_ADMIN = 2

STATUS_ACTIVE = 0
STATUS_INACTIVE = 1
STATUS_BANNED = 2

POST_VISIBLE = True
POST_INVISIBLE = False

COMMENT_AWAITING = False
COMMENT_APPROVED = True


class User(db.Document):
    username = db.StringField(max_length=50, required=True, unique=True)
    email = db.StringField(max_length=255, required=True)
    password = db.StringField(required=True)
    role = db.IntField(default=ROLE_USER)
    status = db.IntField(default=STATUS_ACTIVE)
    last_seen = db.DateTimeField()
    posts = db.ListField(db.ReferenceField('Post', dbref=True))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    #def __unicode__(self):
    #    return self.username

    def __repr__(self):
        return '<User %r>' % (self.username)

    meta = {
        #'allow_inheritance': True,
        'indexes': ['username'],
        'ordering': ['username']
    }


class Post(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow, required=True)
    title = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
    body = db.StringField(required=True)
    visible = db.BooleanField(default=POST_VISIBLE)
    author = db.ReferenceField(User, dbref=True, reverse_delete_rule=db.CASCADE)
    #edited at?
    #tags = db.ListField(db.EmbeddedDocumentField('Tag'))
    tags = db.ListField(db.StringField())
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))

    def get_absolute_url(self):
        return url_for('post', kwargs={'slug': self.slug})

    def get_visible_comments(self):
        visible_comments = []
        for i in self.comments:
            if i.approved == True:
                visible_comments.append(i)
        return visible_comments

    #def __unicode__(self):
    #    return self.title

    def __repr__(self):
        return '<Post %r>' % (self.title)

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at'],
        'cascade': True
    }


class Comment(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow, required=True)
    body = db.StringField(verbose_name='Comment', required=True)
    author = db.StringField(verbose_name='Name', max_length=50, required=True)
    email = db.StringField(verbose_name='E-mail', max_length=255, required=True)
    approved = db.BooleanField(default=COMMENT_AWAITING)

    def __repr__(self):
        return '<Comment %r>' % (self.author)

#class Tag(db.Document):
    #maybe change this to a Document not EmbeddedDocument?
#    tag = db.StringField()
#    posts = db.ListField(db.ReferenceField(Post, dbref=True))
    #tag = db.ReferenceField(User, dbref=True, reverse_delete_rule=db.CASCADE)

#    def __unicode__(self):
#        return self.tag
