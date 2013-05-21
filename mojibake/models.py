import datetime
import uuid

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

USER_ROLES = {ROLE_USER: 'User',
              ROLE_STAFF: 'Staff',
              ROLE_ADMIN: 'Admin'}


def return_id():

    """
    Generate a UUID and return it as a string
    """

    _id = uuid.uuid4()
    return str(_id)


class User(db.Document):
    username = db.StringField(max_length=50, required=True, unique=True)
    email = db.StringField(max_length=255, required=True)
    password = db.StringField(required=True)
    role = db.IntField(default=ROLE_USER)
    status = db.IntField(default=STATUS_ACTIVE)
    last_seen = db.DateTimeField()
    posts = db.ListField(db.ReferenceField('Post', dbref=True))
    locale = db.StringField(max_length=5)

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
    #comments = db.ListField(db.ReferenceField('Comment', dbref=True))

    def get_absolute_url(self):
        return url_for('post', kwargs={'slug': self.slug})

    def get_visible_comments(self):
        visible_comments = []
        for i in self.comments:
            if i.approved == True:
                visible_comments.append(i)
        return visible_comments

    def get_comments_awaiting(self):
        awaiting_comments = []
        for i in self.comments:
            if i.approved == False:
                awaiting_comments.append(i)
        return awaiting_comments

    @db.queryset_manager
    def visible_posts(self, queryset):
        return queryset.filter(visible=POST_VISIBLE)

    #Post.objects.filter(comments__approved=False)  # returns all posts with comments awaiting approval

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
    _id = db.StringField(default=return_id)
    created_at = db.DateTimeField(default=datetime.datetime.utcnow, required=True)
    body = db.StringField(verbose_name='Comment', required=True)
    author = db.StringField(verbose_name='Name', max_length=50)
    user = db.ReferenceField(User, dbref=True)
    email = db.StringField(verbose_name='E-mail', max_length=255)
    approved = db.BooleanField(default=COMMENT_AWAITING)
    #post = db.ReferenceField(Post, dbref=True, reverse_delete_rule=db.CASCADE)

    def __repr__(self):
        return '<Comment %r>' % (self.author)


    #def return_post_author(self):
    #    return self.post.author

    #@db.queryset_manager
    #def search_by_author(self, queryset, post):
    #    return queryset.filter(post=post)

#class Tag(db.Document):
    #maybe change this to a Document not EmbeddedDocument?
#    tag = db.StringField()
#    posts = db.ListField(db.ReferenceField(Post, dbref=True))
    #tag = db.ReferenceField(User, dbref=True, reverse_delete_rule=db.CASCADE)

#    def __unicode__(self):
#        return self.tag
