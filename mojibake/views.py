# -*- coding: utf-8 -*-

from urllib.parse import urljoin
from flask import render_template, abort, request, make_response, url_for, g, \
    session, redirect, flash
from flask.ext.login import login_required, login_user, \
    logout_user, current_user
from flask.ext.babel import gettext
from werkzeug.contrib.atom import AtomFeed
from passlib.hash import pbkdf2_sha256
import datetime
import markdown

from mojibake.app import app, db, babel, login_manager
from mojibake.models import Post, Tag, Category, User, \
    IPAddr, BreakinAttempts, BannedIPs
from mojibake.settings import POSTS_PER_PAGE, LANGUAGES
from mojibake.forms import PostForm, LoginForm, TranslateForm


def make_external(url):
    return urljoin(request.url_root, url)


@app.route('/')
def home():
    if g.user is not None and g.user.is_authenticated():
        posts = Post.query.order_by(Post.date.desc()).paginate(1, POSTS_PER_PAGE, False)
    else:
        posts = Post.query.filter_by(published=True).order_by(Post.date.desc()).paginate(1, POSTS_PER_PAGE, False)

    return render_template('index.html', posts=posts)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/contact/')
def contact():
    return render_template('contact.html')


@app.route('/archive/')
def archive():
    if g.user is not None and g.user.is_authenticated():
        posts = Post.query.all()
    else:
        posts = Post.query.filter_by(published=True).all()
    years = list(set([post.date.year for post in posts]))

    return render_template('archive.html', years=years)


@app.route('/archive/<year>/')
def archive_year(year):
    if g.user is not None and g.user.is_authenticated():
        year_posts = Post.query.filter("strftime('%Y', date) = :year"). \
            params(year=year).order_by('-date').all()
    else:
        year_posts = Post.query.filter("strftime('%Y', date) = :year"). \
            params(year=year).filter_by(published=True).order_by('-date').all()

    if year_posts:
        return render_template('archive_year.html', year=year,
            posts=year_posts)
    else:
        abort(404)


@app.route('/bans/')
def bans():

    #displayed_time = 'CET'
    #time_offset = '+1'

    last_month = datetime.datetime.now().replace(day=1) - datetime.timedelta(days=1)
    #last_month = datetime.datetime.now()  # for testing

    breakin_attempts = BreakinAttempts.query.filter("strftime('%Y', date) = :year").params(year=last_month.strftime('%Y')). \
        filter("strftime('%m', date) = :month").params(month=last_month.strftime('%m')).order_by('-date').all()
    bans = BannedIPs.query.filter("strftime('%Y', date) = :year").params(year=last_month.strftime('%Y')). \
        filter("strftime('%m', date) = :month").params(month=last_month.strftime('%m')).order_by('-date').all()

    #displayed_time=displayed_time,
    #    time_offset=time_offset,

    return render_template('bans.html', last_month=last_month,
        breakin_attempts=breakin_attempts,
        bans=bans)


@app.route('/tags/')
def tags():
    tags = Tag.query.order_by('name').all()
    if g.user is None or g.user.is_authenticated() == False:
        for i in tags:
            if i.posts.filter_by(published=True).count() == 0:
                tags.remove(i)

    return render_template('tags.html', tags=tags)


@app.route('/tags/<name>/')
def tag_name(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    if g.user is None or g.user.is_authenticated() == False:
        if tag.posts.filter_by(published=True).count() == 0:
            abort(404)
    return render_template('tag_list.html', tag=tag)


@app.route('/categories/')
def categories():
    categories = Category.query.order_by('name').all()
    if g.user is None or g.user.is_authenticated() == False:
        for i in categories:
            if i.posts.filter_by(published=True).count() == 0:
                categories.remove(i)

    return render_template('categories.html', categories=categories)


@app.route('/categories/<name>/')
def category(name):
    category = Category.query.filter_by(name=name).first_or_404()
    if g.user is None or g.user.is_authenticated() == False:
        if category.posts.filter_by(published=True).count() == 0:
            abort(404)
    return render_template('category.html', category=category)


@app.route('/posts/')
@app.route('/posts/<page>/')
def posts(page=1):
    if g.user is not None and g.user.is_authenticated():
        posts = Post.query.order_by(Post.date.desc()).paginate(int(page), POSTS_PER_PAGE, False)
    else:
        posts = Post.query.filter_by(published=True).order_by(Post.date.desc()).paginate(int(page), POSTS_PER_PAGE, False)

    if posts:
        return render_template('posts.html', posts=posts)
    else:
        abort(404)


@app.route('/post/<slug>')
def post(slug):
    if g.user is not None and g.user.is_authenticated():
        post = Post.query.filter_by(slug=slug).first_or_404()
    else:
        post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template('post.html', post=post)


@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():

    #can't make a post without a published date?

    form = PostForm()
    if form.validate_on_submit():

        cat = None
        cat_ja = None
        if form.category.data:
            cat = Category.query.filter_by(name=form.category.data).first()
            if cat is None:
                cat = Category.query.filter_by(name_ja=form.category.data).first()
                if cat is None:
                    if form.category_ja.data:
                        cat_ja = form.category_ja.data
                    cat = Category(form.category.data, cat_ja)
                    db.session.add(cat)
                    db.session.commit()

        tags = []
        tags_ja = []
        if form.tags.data:
            if form.tags_ja.data:
                tags_ja = form.tags_ja.data.split(';')
            for index, i in enumerate(form.tags.data.split(';')):
                tag = Tag.query.filter_by(name=i).first()
                if tag:
                    tags.append(tag)
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

        body = form.body.data
        body_ja = form.body_ja.data

        new_post = Post(form.title.data, form.slug.data, cat, tags,
                        date=form.date.data, body=body, body_ja=body_ja,
                        title_ja=form.title_ja.data, published=form.published.data)

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('post', slug=form.slug.data))
    return render_template('post_create.html',
                           form=form)

@app.route('/post/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = PostForm(obj=post)
    if form.validate_on_submit():

        cat = None
        cat_ja = None
        if form.category.data:
            cat = Category.query.filter_by(name=form.category.data).first()
            if cat is None:
                cat = Category.query.filter_by(name_ja=form.category.data).first()
                if cat is None:
                    if form.category_ja.data:
                        cat_ja = form.category_ja.data
                    cat = Category(form.category.data, cat_ja)
                    db.session.add(cat)
                    db.session.commit()

        tags = []
        tags_ja = []
        if form.tags.data:
            if form.tags_ja.data:
                tags_ja = form.tags_ja.data.split(';')
            for index, i in enumerate(form.tags.data.split(';')):
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
                        #this is a bit ugly.. maybe do something better with this in the future?
                        if len(tags_ja) >= index+1 and tags_ja != ['']:
                            tag = Tag(i, tags_ja[index])
                        else:
                            tag = Tag(i)

                        db.session.add(tag)
                        db.session.commit()
                        tags.append(tag)

        post.title = form.title.data
        post.title_ja = form.title_ja.data
        post.slug = form.slug.data
        post.category = cat
        post.tags = tags
        post.date = form.date.data
        post.body = form.body.data
        post.body_html = markdown.markdown(form.body.data, extensions=['codehilite'])
        post.body_ja = form.body_ja.data
        post.body_ja_html = markdown.markdown(form.body_ja.data, extensions=['codehilite'])
        post.published = form.published.data
        db.session.commit()

        return redirect(url_for('post', slug=form.slug.data))

    return render_template('post_create.html',
                       form=form)


#change this to GET?
@app.route('/post/<slug>/delete', methods=['POST'])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    db.session.delete(post)
    return redirect(url_for('posts'))


@app.route('/translate', methods=['GET', 'POST'])
@login_required
def translate():
    form = TranslateForm()
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

    return render_template('translate.html', tags=tags, cats=cats, form=form,
        posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if pbkdf2_sha256.verify(form.password.data, user.password):
                login_user(user, remember=form.remember_me.data)
                flash(gettext("Logged in successfully."), 'success')
                return redirect(request.args.get("next") or url_for("home"))
        else:
            flash(gettext("Invalid Login"), 'error')
            redirect(url_for('login'))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(request.args.get("next") or url_for("home"))


@app.route('/language/<language>')
def change_language(language):
    session['language'] = language
    return redirect(request.args.get('next') or url_for('home'))


@app.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url, url=request.url_root)
    posts = Post.query.filter_by(published=True).order_by(Post.date.desc()).all()
    for post in posts:
        feed.add(post.title, post.body[:500] + '\n\n....',
                 content_type='html',
                 author='Jordan',
                 url=make_external(url_for('post', slug=post.slug)),
                 updated=post.date)
    return feed.get_response(), 200, {'Content-Type': 'application/atom+xml; charset=utf-8'}


#Adapted from http://flask.pocoo.org/snippets/108/
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    hide_views = ['/post/create', '/post/<slug>/edit', '/post/<slug>/delete',
                    '/translate', '/login', '/logout']

    map_pages = []
    ten_days_ago=(datetime.datetime.now() - datetime.timedelta(days=10)).date().isoformat()
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            #kind of a temporary hack, I'd like to find a better way to do this
            if (rule.rule in hide_views) == False:
                map_pages.append([rule.rule,ten_days_ago])

    tags = Tag.query.all()
    for tag in tags:
        if tag.posts.filter_by(published=True).count() > 0:
            url = url_for('tag_name', name=tag.name)
            map_pages.append([url, ten_days_ago])

    categories = Category.query.all()
    for category in categories:
        if category.posts.filter_by(published=True).count() > 0:
            url = url_for('category', name=category.name)
            map_pages.append([url, ten_days_ago])

    posts = Post.query.filter_by(published=True).all()
    for post in posts:
        url = url_for('post', slug=post.slug)
        map_pages.append([url, ten_days_ago])

    sitemap_xml = render_template('sitemap_template.xml', pages=map_pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@app.errorhandler(404)
def internal_error400(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error500(error):
    return render_template('500.html'), 500


@app.before_request
def before_request():
    #g.user = getattr(g, 'user', None)
    g.user = current_user

    if 'language' not in session:
        session['language'] = request.accept_languages.best_match(LANGUAGES.keys())


@babel.localeselector
def get_locale():
    return session['language']


@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=userid).first()
