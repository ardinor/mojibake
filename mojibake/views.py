from flask import render_template, g, redirect, url_for, \
    flash, request, jsonify
from flask import session
from flask.ext.login import login_required, login_user, \
    logout_user, current_user
from flask.ext.babel import gettext
from flask.ext.uploads import UploadNotAllowed
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
import time

from mojibake import app, lm, babel, photos  # db,
from models import User, Post
from models import POST_VISIBLE, USER_ROLES
from forms import LoginForm, CreateUserForm
from config import POSTS_PER_PAGE
from config import REGISTRATION, REGISTRATION_OPEN
from config import LANGUAGES
from posts import posts
from admin import admin

app.register_blueprint(posts)
app.register_blueprint(admin)


def make_external(url):
    return urljoin(request.url_root, url)


@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    start = time.clock()
    #displays posts even if they are not visible at the moment...
    posts = Post.objects(visible=True).paginate(page=page, per_page=POSTS_PER_PAGE)
    recent = Post.objects(visible=True).order_by('-created_at')[:5]
    return render_template('posts/list.html',
                           pagination=posts,
                           recent=recent,
                           taken=time.clock,
                           start=start)


@app.route('/tags')
@app.route('/tags/<tag>')
def tags(tag=None):
    if tag is None:
        tags = Post.objects(visible=True).distinct('tags')
        return render_template('posts/tags.html',
                               tags=tags)
    else:
        posts = Post.objects(tags=tag, visible=POST_VISIBLE)
        return render_template('posts/tag_list.html',
                               posts=posts,
                               tag=tag,
                               title=tag)


@app.route('/profile')
@app.route('/profile/<username>')
def profile(username=None):
    if username is None:
        users = User.objects.all()
        return render_template('users/userlist.html',
                               users=users,
                               roles=USER_ROLES)
    else:
        user = User.objects.get_or_404(username=username)
        return render_template('users/user.html',
                               user=user,
                               roles=USER_ROLES)


@app.route('/language/<language>')
def change_language(language):
    session['language'] = language
    if g.user.is_authenticated():
        g.user.locale = language
        g.user.save()
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('panel'))
    form = LoginForm()
    if form.validate_on_submit():
        logging_in_user = User.objects(username=form.username.data)
        if logging_in_user:
            logging_in_user = logging_in_user[0]
            if pbkdf2_sha256.verify(form.password.data, logging_in_user.password):
                remember_me = False
                if form.remember_me.data:
                    remember_me = True
                login_user(logging_in_user, remember=remember_me)
                return redirect(request.args.get('next') or url_for('panel'))
            else:
                flash(gettext('Invalid login. Please try again.'), 'error')
                redirect(url_for('login'))
        else:
            flash(gettext('Invalid login. Please try again.'), 'error')
            redirect(url_for('login'))
    return render_template('users/login.html',
                           title=gettext('Sign In'),
                           form=form)


@app.route('/loginmodal')
def login_modal():
    form = LoginForm()
    return render_template('users/loginmodal.html',
                           form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create', methods=['GET', 'POST'])
def create():
    if REGISTRATION == REGISTRATION_OPEN:
        form = CreateUserForm()
        if form.validate_on_submit():
            new_user = User(username=form.username.data,
                            email=form.email.data,
                            password=pbkdf2_sha256.encrypt(form.password.data))
            new_user.save()
            return redirect(url_for('panel'))
            #else:
            #    flash('Invalid details. Please try again.')
            #    redirect(url_for('create'))
        return render_template('users/create.html',
                               title=gettext('Create account'),
                               form=form)
    else:
        return render_template('users/closed.html',
                               title=gettext('Registration closed.'))


#Atom feed
#Based on this snippet http://flask.pocoo.org/snippets/10/
@app.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url,
                    url=request.url_root)
    recent_posts = Post.objects(visible=True).order_by('-created_at')[:15]
    for post in recent_posts:
        feed.add(post.title, unicode(post.body),
                 content_type='html',
                 author=post.author.username,
                 url=make_external(post.slug),
                 updated=post.created_at,
                 published=post.created_at)
    return feed.get_response()


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'img' in request.files:
        try:
            uploaded_files = request.files.getlist("img")
            for i in uploaded_files:
                #folder is the slug of the post
                #change the name of the img? name=""
                #If it ends with a dot, the file's extension will be appended to the end
                filename = photos.save(i, folder='g')
                url = photos.url(filename)
                #append filename to post.images list
            flash("Photo saved.")
        except UploadNotAllowed:
            flash("Upload not allowed")
        return redirect(url_for('index'))
    return render_template('posts/upload.html')


@app.errorhandler(404)
def internal_error400(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error500(error):
    return render_template('500.html'), 500


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        session['language'] = g.user.locale
        g.user.last_seen = datetime.utcnow()
        g.user.save()
    if 'language' not in session:
        session['language'] = request.accept_languages.best_match(LANGUAGES.keys())


@lm.user_loader
def load_user(id):
    #return User.objects.get(id)
    #the above returned MultipleObjectsReturned: 2 items returned, instead of 1
    #the below right or messy?
    return User.objects(id=id)[0]


@babel.localeselector
def get_locale():
    return session['language']
