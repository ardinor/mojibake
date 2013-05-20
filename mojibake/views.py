from flask import render_template, g, redirect, url_for, \
    flash, request, jsonify
from flask import session
from flask.ext.login import login_required, login_user, \
    logout_user, current_user
from flask.ext.babel import gettext
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from cgi import escape
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
import time

from mojibake import app, lm, babel  # db,
from models import User, Post, Comment
from models import POST_VISIBLE, ROLE_ADMIN, USER_ROLES, COMMENT_APPROVED
from forms import LoginForm, CreateUserForm, PostForm, \
    CommentForm, UserCommentForm
from config import POSTS_PER_PAGE
from config import REGISTRATION, REGISTRATION_OPEN
from config import LANGUAGES


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


@app.route('/post/<slug>', methods=['GET', 'POST'])
def get_post(slug):
    post = Post.objects.get_or_404(slug=slug)

    user = None
    form = None
    if g.user is not None and g.user.is_authenticated:
        try:
            user_id = g.user.id
            user = User.objects(id=user_id)[0]
            form = UserCommentForm()
        except AttributeError:
            pass
    if form is None:
        form = CommentForm()
    if form.validate_on_submit():
        if user:
            #and User.objects(id=g.user.id)[0]:
            comment = Comment(body=escape(form.body.data),
                              user=user,
                              approved=COMMENT_APPROVED,
                              )
            flash(gettext('Comment posted!'), 'success')
        else:
            comment = Comment(body=escape(form.body.data),
                              author=escape(form.author.data),
                              email=escape(form.email.data),
                              )
            flash(gettext('Comment posted and awaiting administrator approval.'), 'success')
        post.comments.append(comment)
        post.save()
        #flash('Comment posted and awaiting administrator approval.', 'success')
        return redirect(url_for('get_post', slug=slug))
    return render_template('posts/detail.html',
                           post=post,
                           slug=slug,
                           form=form,
                           user=user,
                           title=post.title)


@app.route('/post/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.objects.get_or_404(slug=slug)
    form = PostForm(obj=post)
    form.tags.data = ','.join(form.tags.data)
    if form.validate_on_submit():
        #Nasty hack for some reason it tag library puts a comma after
        #every character?
        tags = form.tags.data.replace(',,,', '|')
        tags = tags.replace(',', '')
        tags = tags.replace('|', ',')
        tags = tags.split(',')
        post.title = form.title.data
        post.slug = form.slug.data
        post.body = form.body.data
        post.visible = form.visible.data
        post.tags = tags
        post.save()
        flash(gettext('Post updated!'), 'success')
        return redirect(url_for('get_post', slug=slug))
    return render_template('posts/edit.html',
        form=form,
        title='Edit Post')


@app.route('/post/<slug>/delete', methods=['GET'])
@login_required
def delete_post(slug):
    post = Post.objects.get_or_404(slug=slug)
    user = g.user
    #check if it's the users post or if the user has admin?
    if User.objects(id=user.id)[0] == post.author or User.objects(id=user.id)[0].role == ROLE_ADMIN:
        post.delete()
        flash(gettext('Post deleted!'), 'success')
        return redirect(url_for('index'))
    else:
        flash(gettext('You do not have permission to delete this post.'), 'error')
        return redirect(url_for('get_post', slug=slug))


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    user = g.user
    if form.validate_on_submit():
        tags_list = []
        for i in form.tags.data.split(','):
            tags_list.append(i.strip())
        post = Post(title=form.title.data,
            slug=form.slug.data,
            body=form.body.data,
            visible=form.visible.data,
            author=User.objects(id=user.id)[0],
            tags=tags_list)  # tags not right I think
        post.save()
        user.posts.append(post)
        flash(gettext('Post created!'), 'success')
        return redirect(url_for('get_post', slug=post.slug))
    return render_template('posts/edit.html',
        form=form,
        title=gettext('New Post'))


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


@app.route('/panel')
@app.route('/panel/<int:page>')
@login_required
def panel(page=1):
    user = g.user
    #can't just use user as it is type <class 'werkzeug.local.LocalProxy'>
    #better way of doing this?
    awaiting_comments = {}
    post_awaiting_comments = []
    #paginate comments? what if there's 50 comments?
    author = User.objects(id=user.id)[0]
    for i in Post.objects(author=author).filter(comments__approved=False):
        post_awaiting_comments = post_awaiting_comments + i.get_comments_awaiting()
        awaiting_comments[i] = post_awaiting_comments
        post_awaiting_comments = []
    posts = Post.objects(author=author).paginate(page=page, per_page=POSTS_PER_PAGE)
    #comments = Comments.objects(post=author)
    return render_template('users/panel.html',
        user=user,
        pagination=posts,
        comments=awaiting_comments)


@app.route('/panel/comment/approve')
def approve_comment():
    rqst_ref = request.args.get('ref')
    post = Post.objects.filter(comments___id=rqst_ref)[0]
    if post:
        for i in post.comments:
            if i._id == rqst_ref:
                i.approved = True
                post.save()
                result = True
    else:
        result = False
    return jsonify(result=result)


@app.route('/panel/comment/delete')
def delete_comment():
    rqst_ref = request.args.get('ref')
    post = Post.objects.filter(comments___id=rqst_ref)[0]
    if post:
        for i in post.comments:
            if i._id == rqst_ref:
                post.comments.remove(i)
                post.save()
                result = True
    else:
        result = False
    return jsonify(result=result)


@app.route('/language/<language>')
def change_language(language):
    session['language'] = language
    return redirect(request.args.get('next') or url_for('index'))
    # for key, value in LANGUAGES.iteritems():
    #     if key == language:
    #         #g.user.locale = key
    #         #user = getattr(g, 'user', None)
    #         #user.locale = key
    #         session['language'] = key
    #         #print user.locale
    #         return redirect(request.args.get('next') or url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if request.args.get('username') is not None:
    #     username = request.args.get('username').strip()
    #     password = request.args.get('password').strip()
    #     form = LoginForm(username=username, password=password, remember_me=False)
    #     if form.validate_on_submit():
    #         return jsonify(response='success')
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


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.before_request
def before_request():
    g.user = current_user
    #if getattr(g.user, 'locale', None) is None:
    if 'language' not in session:
        print 'set language'
        session['language'] = request.accept_languages.best_match(LANGUAGES.keys())
        #g.user.locale = request.accept_languages.best_match(LANGUAGES.keys())
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        g.user.save()


@lm.user_loader
def load_user(id):
    #return User.objects.get(id)
    #the above returned MultipleObjectsReturned: 2 items returned, instead of 1
    #the below right or messy?
    return User.objects(id=id)[0]


@babel.localeselector
def get_locale():
    return session['language']
    #return g.user.locale
    #return 'ja'
    #user = getattr(g, 'user', None)
    #if user is not None:  # and getattr(g, 'user.locale', None):
    #    return user.locale
    #user.locale = request.accept_languages.best_match(LANGUAGES.keys())
    #return request.accept_languages.best_match(LANGUAGES.keys())
