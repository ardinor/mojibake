from mojibake.app import db

from datetime import datetime
from passlib.hash import pbkdf2_sha256
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
    name = db.Column(db.String(50), unique=True)
    name_ja = db.Column(db.String(50), unique=True)
    #posts = db.relationship('Post', backref='category',
    #                            lazy='dynamic')

    def __init__(self, name, name_ja=None):
        if name:
            self.name = name
        if name_ja:
            self.name_ja = name_ja

    def __repr__(self):
        return '<Category: {}>'.format(self.name)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, index=True)
    # Having unique set here will cause issues if multiple posts
    # don't have a title_ja and are using None
    title_ja = db.Column(db.String(120))
    slug = db.Column(db.String(120), unique=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    body_ja = db.Column(db.Text)
    body_ja_html = db.Column(db.Text)
    date = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    published = db.Column(db.Boolean)
    category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'))
    tags = db.relationship('Tag', secondary=tags,
                                 backref=db.backref('posts',
                                                    lazy='dynamic'))

    def __init__(self, title, slug):
        self.title = title
        self.slug = slug


    def add_category(self, form_cat, form_cat_ja=None):
        cat = Category.query.filter_by(name=form_cat).first()
        if cat is None and form_cat_ja:
            cat = Category.query.filter_by(name_ja=form_cat_ja).first()
            if cat is None:
                cat = Category(form_cat, form_cat_ja)
                db.session.add(cat)
                db.session.commit()
        elif cat is None:
            cat = Category(form_cat)
            db.session.add(cat)
            db.session.commit()
        self.category = cat


    def add_tags(self, form_tags, form_tags_ja=None):
        tags = []
        tags_ja = []
        if form_tags:
            if form_tags_ja:
                tags_ja = form_tags_ja.split(';')
            for index, i in enumerate(form_tags.split(';')):
                tag = Tag.query.filter_by(name=i).first()
                if tag:
                    tags.append(tag)
                    if tag.name_ja is None:
                        if len(tags_ja) >= index+1 and tags_ja != ['']:
                            if tags_ja[index] != 'None':
                                tag.name_ja = tags_ja[index]
                                db.session.add(tag)
                                db.session.commit()
                else:
                    tag = Tag.query.filter_by(name_ja=i).first()
                    if tag:
                        tags.append(tag)
                    else:
                        #this is a bit ugly. maybe do something better with this in the future?
                        if len(tags_ja) >= index+1 and tags_ja != ['']:
                            tag = Tag(i, tags_ja[index])
                        else:
                            tag = Tag(i)

                        db.session.add(tag)
                        db.session.commit()
                        tags.append(tag)
            self.tags = tags


    def add_body(self, body, body_ja=None):
        if body:
            self.body = body
            self.body_html = markdown.markdown(body, extensions=['codehilite'])
        if body_ja:
            self.body_ja = body_ja
            self.body_ja_html = markdown.markdown(body_ja, extensions=['codehilite'])


    def __repr__(self):
        return '<Post: {}>'.format(self.title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    name_ja = db.Column(db.String(50), unique=True)

    def __init__(self, name, name_ja=None):
        if name:
            self.name = name
        if name_ja:
            self.name_ja = name_ja

    def __repr__(self):
        return '<Tag: {}>'.format(self.name)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))

    def __init__(self, username):
        self.username = username

    def set_password(self, password):
        self.password = pbkdf2_sha256.encrypt(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


class IPAddr(db.Model):
    __tablename__ = 'ipaddr'
    id = db.Column(db.Integer, primary_key=True)
    ip_addr = db.Column(db.String(45), unique=True)
    city_name = db.Column(db.String(255))
    region = db.Column(db.String(255))
    country = db.Column(db.String(255))
    bans = db.relationship('BannedIPs', backref='ip', lazy='dynamic')
    breakins = db.relationship('BreakinAttempts', backref='ip', lazy='dynamic')

    def __init__(self, ip_addr):
        self.ip_addr = ip_addr

    def __repr__(self):
        return '<IP: {}>'.format(self.ip_addr)

    def print_location(self):
        if self.city_name and self.region and self.country:
            return '{}, {}, {}'.format(self.city_name, self.region, self.country)
        elif self.region and self.country:
            return '{}, {}'.format(self.region, self.country)
        elif self.country:
            return '{}'.format(self.country)
        else:
            return '-'

class BannedIPs(db.Model):
    # Without setting table name we end up with a table named
    # 'banned_i_ps'
    __tablename__ = 'bannedips'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    ipaddr = db.Column(db.Integer, db.ForeignKey('ipaddr.id'))

    def __repr__(self):
        return '<BannedIP: {}>'.format(self.date.strftime('%d-%m-%Y %H:%M:%S'))


class BreakinAttempts(db.Model):
    __tablename__ = 'breakinattempts'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    # Some programs accept only 8 character user names
    # The max for useradd seems to be 32 though, don't think
    # we'll see attempts with usernames longer than that though
    user = db.Column(db.String(32))
    ipaddr = db.Column(db.Integer, db.ForeignKey('ipaddr.id'))

    def __repr__(self):
        return '<BreakinAttempt: {} on {}>'.format(self.user, self.date.strftime('%d-%m-%Y %H:%M:%S'))

