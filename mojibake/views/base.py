from flask import Blueprint, abort, g, render_template, request, \
    redirect, flash, url_for, session
from flask.ext.login import login_required, login_user, \
    logout_user, current_user
from flask.ext.babel import gettext

import logging

from urllib.parse import urljoin
from werkzeug.contrib.atom import AtomFeed

from mojibake.models import Post, Tag, Category, User
from mojibake.settings import POSTS_PER_PAGE, LANGUAGES
from mojibake.app import babel, login_manager
from mojibake.forms import LoginForm

base = Blueprint('base', __name__,
    template_folder='templates')

logger = logging.getLogger('mojibake')

def make_external(url):
    return urljoin(request.url_root, url)

@base.route('/')
def home():
    if g.user is not None and g.user.is_authenticated():
        posts = Post.query.order_by(Post.date.desc()).paginate(1, POSTS_PER_PAGE, False)
    else:
        posts = Post.query.filter_by(published=True).order_by(Post.date.desc()).paginate(1, POSTS_PER_PAGE, False)

    return render_template('index.html', posts=posts)


@base.route('/about/')
def about():
    return render_template('about.html')


@base.route('/contact/')
def contact():
    return render_template('contact.html')


@base.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.verify_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                logger.info('Successful login attempt for user %s', user.username)
                flash(gettext("Logged in successfully."), 'success')
                return redirect(request.args.get("next") or url_for("base.home"))
            else:
                logger.info('Invalid password for user %s', user.username)
                flash(gettext("Invalid Login"), 'error')
                redirect(url_for('base.login'))
        else:
            logger.info('Invalid login attempt for user %s', user.username)
            flash(gettext("Invalid Login"), 'error')
            redirect(url_for('base.login'))

    return render_template("login.html", form=form)


@base.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(request.args.get("next") or url_for("base.home"))


@base.route('/language/<language>')
def change_language(language):
    session['language'] = language
    return redirect(request.args.get('next') or url_for('base.home'))


@base.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url, url=request.url_root)
    posts = Post.query.filter_by(published=True).order_by(Post.date.desc()).all()
    for post in posts:
        feed.add(post.title, post.body[:500] + '\n\n....',
                 content_type='html',
                 author='Jordan',
                 url=make_external(url_for('posts.post_item', slug=post.slug)),
                 updated=post.date)
    return feed.get_response(), 200, {'Content-Type': 'application/atom+xml; charset=utf-8'}


@base.route('/translate', methods=['GET', 'POST'])
@login_required
def translate():
    if request.method == 'POST':
        req_dict = request.form.to_dict()
        for i, j in req_dict.items():
            if i[:4] == 'tag_' and j != '':
                tag_name = i[4:len(i)-3]
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    tag.name_ja = j
                    db.session.add(tag)
                    db.session.commit()
            elif i[:4] == 'cat_' and j != '':
                cat_name = i[4:len(i)-3]
                cat = Category.query.filter_by(name=cat_name).first()
                if cat:
                    cat.name_ja = j
                    db.session.add(cat)
                    db.session.commit()

    tags = Tag.query.filter_by(name_ja=None).all()
    cats = Category.query.filter_by(name_ja=None).all()
    posts = Post.query.filter_by(body_ja=None).all()

    return render_template('translate.html', tags=tags, cats=cats,
        posts=posts)
