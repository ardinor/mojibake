from mojibake.app import db

from datetime import datetime
import markdown

tags = db.Table('tags',
                 db.Column('post_id',
                    db.Integer,
                    db.ForeignKey('post.id')),
                 db.Column('tag_id',
                    db.Integer,
                    db.ForeignKey('tag.id')))


class ValidationError(Exception):

    def __init__(self, message, error=None):
        Exception.__init__(self, message)
        self.errors = error


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    name_ja = db.Column(db.String(50))
    #posts = db.relationship('Post', backref='category',
    #                            lazy='dynamic')

    def __init__(self, name, name_ja=None):
        self.name = name
        if name_ja:
            self.name_ja = name_ja
        else:
            self.name_ja = name

    def __repr__(self):
        return '<Category: {}>'.format(self.name)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, index=True)
    slug = db.Column(db.String(120), unique=True)
    #path = db.Column(db.String(240), index=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    body_ja = db.Column(db.Text)
    body_ja_html = db.Column(db.Text)
    #body_html?
    date = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'))
    tags = db.relationship('Tag', secondary=tags,
                                 backref=db.backref('posts',
                                                    lazy='dynamic'))

    def __init__(self, title, slug, category, tags, date=None, body=None, body_ja=None):
        self.title = title
        self.slug = slug  #check slug is unique

        if body is None and body_ja is None:
            raise ValidationError("Both body and body_ja cannot be empty!")

        if body:
            self.body = body
            self.body_html = markdown.markdown(body, extensions=['codehilite'])
        if body_ja:
            self.body_ja = body_ja
            self.body_ja_html = markdown.markdown(body_ja, extensions=['codehilite'])
        if date is None:
            date = datetime.utcnow()
        self.date = date
        self.category = category
        self.tags = tags


    def __repr__(self):
        return '<Post: {}>'.format(self.title)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    name_ja = db.Column(db.String(50))

    def __init__(self, name, name_ja=None):
        self.name = name
        if name_ja:
            self.name_ja = name_ja
        else:
            self.name_ja = name

    def __repr__(self):
        return '<Tag: {}>'.format(self.name)


