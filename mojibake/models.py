import time
import markdown
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from flask.ext.sqlalchemy import models_committed  #before_models_committed
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, func
from sqlalchemy.exc import InvalidRequestError

from mojibake.app import db, app
from mojibake.settings import SQLALCHEMY_DATABASE_URI

# Many-to-many relationship for Post and Tag
tags = db.Table('tags',
                db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                )


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
            self.body_html = markdown.markdown(body, extensions=['markdown.extensions.codehilite'])
        if body_ja:
            self.body_ja = body_ja
            self.body_ja_html = markdown.markdown(body_ja, extensions=['markdown.extensions.codehilite'])


    def get_tz_offset(self):
        # Returns the timezone offset in hours
        # E.g. AEST (+10) will return 10
        if time.localtime().tm_isdst:
            return (time.altzone * -1) / 3600
        else:
            return (time.timezone * -1) / 3600


    def __before_delete__(self):
        # In here, check to see if the category and/or tags will be orphaned
        # by the delete, if so, delete them too
        # Seems we need to make a new session to perform transactions
        #
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        session = Session()

        if self.category_id:
            category = session.query(Category).filter(Category.id==self.category_id).first()
            #category = Category.query.filter_by(id=self.category_id).first()
            if category:
                if category.posts.count() == 0:
                    #db.session.begin()
                    session.delete(category)
                    #db.session.commit()


        #orphaned_tags = session.query(Tag).join(Post).group_by(Tag.posts). \
        #                    having(func.count(Tag.posts)==0).all()

        tag_list = session.query(Tag).join(tags).group_by(tags.c.tag_id).having(func.count(tags.c.post_id)==0).all()
        #tags = session.query(Tag).all()
        ###orphaned_tags = []
        ###for tag in tags:
        ###    if tag.posts.count() == 0:
        ###        orphaned_tags.append(tag)
        ###for tag in orphaned_tags:
        ###    session.delete(tag)
        # if self.tags:
        #     for tag in self.tags:
        #         if tag.posts.count() == 1:
        #             if tag.posts.first() == self:
        #                 session.delete(tag)
        #                 #db.session.commit()
        try:
            session.commit()
        except InvalidRequestError:
            pass
        session.close()


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

    """
    This IP address table, holds the actual address and the location as found
    from the GeoIP service. Holds links to the other tables, BannedIPs, BreakinAttempts
    and SubnetDetails.
    """

    __tablename__ = 'ipaddr'
    id = db.Column(db.Integer, primary_key=True)
    ip_addr = db.Column(db.String(45), unique=True)
    city_name = db.Column(db.String(255))
    region = db.Column(db.String(255))
    country = db.Column(db.String(255))
    bans = db.relationship('BannedIPs', backref='ip', lazy='dynamic')
    breakins = db.relationship('BreakinAttempts', backref='ip', lazy='dynamic')
    subnet = db.Column(db.Integer, db.ForeignKey('subnetdetails.id'))

    def __init__(self, ip_addr):
        self.ip_addr = ip_addr

    def __repr__(self):
        return '<IP: {}>'.format(self.ip_addr)

    def print_location(self):

        """
        Prints the (rough) location of this IP address. Our GeoIP service
        does not return full details (such as city name) for all IP address,
        this will return as much information as we've been given in a nice format.
        """

        if self.city_name and self.region and self.country:
            return '{}, {}, {}'.format(self.city_name, self.region, self.country)
        elif self.region and self.country:
            return '{}, {}'.format(self.region, self.country)
        elif self.country:
            return '{}'.format(self.country)
        else:
            return '-'

    def get_ip_in_binary(self):
        if self.ip_addr:
            return ' '.join('{:08b}'.format(int(n)) for n in self.ip_addr.split('.'))


class BannedIPs(db.Model):

    """
    The Banned IPs table, holds details about IP addresses that have been
    banned by fail2ban. Details are the date it was banned and a link back
    to the IP address table row for this IP address.
    """

    # Without setting table name we end up with a table named
    # 'banned_i_ps'
    __tablename__ = 'bannedips'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    ipaddr = db.Column(db.Integer, db.ForeignKey('ipaddr.id'))

    def __repr__(self):
        return '<BannedIP: {}>'.format(self.date.strftime('%d-%m-%Y %H:%M:%S'))


class BreakinAttempts(db.Model):

    """
    The Breakin Attempts table. This table holds details of login attempts
    by an IP address, including the username they tried and the date/time.
    Has a link to the IP address table row for the IP address.
    """

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


class SubnetDetails(db.Model):

    """
    The Subnet Details table. This table holds details about common subnets
    as calculated by Scrutiny. The details included are the subnet id, the
    CIDR, the netmask and the number of hosts in the subnet. It also includes
    links back to the IP address table rows that hold IP addresses that are
    members of this subnet.
    """

    __tablename__ = 'subnetdetails'
    id = db.Column(db.Integer, primary_key=True)
    subnet_id = db.Column(db.String(15))
    cidr = db.Column(db.String(3))
    netmask = db.Column(db.String(15))
    number_hosts = db.Column(db.Integer)
    date_added = db.Column(db.DateTime)
    ip_addr = db.relationship('IPAddr', backref=db.backref('subnetdetails'))

    def __init__(self, subnet_id):
        self.subnet_id = subnet_id

    def __repr__(self):
        return '<Subnet:{}>'.format(self.subnet_id)


## Seems before_models_committed doesn't actually do anything as of
## Flask-SQLAlchemy 2.0
# # Not really sure if this is the best place to put this...
# #@before_models_committed.connect_via(app)
# #@models_committed.connect
def on_models_committed(sender, changes):
    for obj, change in changes:
        if change == 'delete' and hasattr(obj, '__before_delete__'):
            obj.__before_delete__()

models_committed.connect(on_models_committed, sender=app)
# #before_models_committed.connect(before_model_commit, sender=app)
