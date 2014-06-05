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
    name = db.Column(db.String(50), unique=True)
    name_ja = db.Column(db.String(50), unique=True)
    #posts = db.relationship('Post', backref='category',
    #                            lazy='dynamic')

    def __init__(self, name, name_ja=None):
        self.name = name
        if name_ja:
            self.name_ja = name_ja

    def __repr__(self):
        return '<Category: {}>'.format(self.name)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, index=True)
    title_ja = db.Column(db.String(120), unique=True)
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

    def __init__(self, title, slug, category, tags, date=None, body=None, body_ja=None, title_ja=None, published=False):

        self.title = title

        if title_ja:
            self.title_ja = title_ja
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
        self.published = published


    def __repr__(self):
        return '<Post: {}>'.format(self.title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    name_ja = db.Column(db.String(50), unique=True)

    def __init__(self, name, name_ja=None):
        self.name = name
        if name_ja:
            self.name_ja = name_ja

    def __repr__(self):
        return '<Tag: {}>'.format(self.name)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))

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
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    # Some programs accept only 8 character user names
    # The max for useradd seems to be 32 though, don't think
    # we'll see attempts with usernames longer than that though
    user = db.Column(db.String(32))
    ipaddr = db.Column(db.Integer, db.ForeignKey('ipaddr.id'))

    def __repr__(self):
        return '<BreakinAttempt: {} on {}>'.format(self.user, self.date.strftime('%d-%m-%Y %H:%M:%S'))

