# -*- coding: utf-8 -*-

from urllib.parse import urljoin
from flask import render_template, abort, request, make_response, url_for, g, \
    session, redirect
#from flask_flatpages import pygments_style_defs
from werkzeug.contrib.atom import AtomFeed
import datetime
import markdown

from mojibake.app import app, db, babel
from mojibake.models import Post, Tag, Category
from mojibake.settings import POSTS_PER_PAGE, LANGUAGES
from mojibake.forms import PostForm


def make_external(url):
    return urljoin(request.url_root, url)


@app.route('/')
def home():

    posts = Post.query.order_by(Post.date.desc()).paginate(1, POSTS_PER_PAGE, False)

    return render_template('index.html', posts=posts)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/contact/')
def contact():
    return render_template('contact.html')


@app.route('/archive/')
def archive():
    posts = Post.query.all()
    years = list(set([post.date.year for post in posts]))

    return render_template('archive.html', years=years)


@app.route('/archive/<year>/')
def archive_year(year):
    year_posts = Post.query.filter("strftime('%Y', date) = :year"). \
            params(year=year).order_by('-date').all()

    if year_posts:
        return render_template('archive_year.html', year=year,
            posts=year_posts)
    else:
        abort(404)


@app.route('/tags/')
def tags():
    tags = Tag.query.order_by('name').all()

    return render_template('tags.html', tags=tags)


@app.route('/bans/')
def bans():

    #just fill it with filler information, this template is made elsewhere

    breakin_attempts = {datetime.datetime(2013, 12, 2, 20, 31, 46): ('95.183.198.46', 'nagios'),
                        datetime.datetime(2013, 12, 5, 20, 56, 46): ('95.183.198.46', 'postgres'),
                        datetime.datetime(2013, 12, 8, 21, 4, 46): ('95.183.198.46', 'igor'),
                        datetime.datetime(2013, 12, 12, 22, 31, 46): ('211.141.113.237', 'ftpuser'),
                        datetime.datetime(2013, 12, 25, 22, 48, 46): ('195.60.215.30', 'oracle')
                        }

    bans = {datetime.datetime(2013, 12, 9, 21, 5, 46): '95.183.198.46',
            datetime.datetime(2013, 12, 2, 21, 10, 46): '211.141.113.237',
            datetime.datetime(2013, 12, 12, 22, 50, 46): '195.60.215.30'}

    ips = {'95.183.198.46': {'country':u'日本', 'region': u'大坂'},
           '211.141.113.237': {'country':'Test', 'region': 'Test Region'},
           '195.60.215.30': {'country':'Test', 'region': 'Test Region'}}

    displayed_time = 'CET'
    time_offset = '+1'

    sorted_bans = sorted(bans.keys())
    sorted_breakins = sorted(breakin_attempts.keys())

    last_month = datetime.datetime.now().replace(day=1) - datetime.timedelta(days=1)

    return render_template('bans.html', displayed_time=displayed_time,
        time_offset=time_offset, last_month=last_month,
        breakin_attempts=breakin_attempts,
        bans=bans, ips=ips, sorted_bans=sorted_bans,
        sorted_breakins=sorted_breakins)


@app.route('/tags/<name>/')
def tag_name(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    return render_template('tag_list.html', tag=tag)


@app.route('/categories/')
def categories():
    categories = Category.query.order_by('name').all()

    return render_template('categories.html', categories=categories)


@app.route('/categories/<name>/')
def category(name):
    category = Category.query.filter_by(name=name).first()

    if category:
        return render_template('category.html', category=category)
    else:
        abort(404)


@app.route('/posts/')
@app.route('/posts/<page>/')
def posts(page=1):

    posts = Post.query.order_by(Post.date.desc()).paginate(int(page), POSTS_PER_PAGE, False)

    if posts:
        return render_template('posts.html', posts=posts)
    else:
        abort(404)


@app.route('/post/<slug>')
def post(slug):

    post = Post.query.filter_by(slug=slug).first()

    if post:
        return render_template('post.html', post=post)
    else:
        abort(404)


@app.route('/post/create', methods=['GET', 'POST'])
#@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():

        cat = None
        if form.category.data:
            cat = Category.query.filter_by(name=form.category.data).first()
            if cat is None:
                cat = Category.query.filter_by(name_ja=form.category.data).first()
                if cat is None:
                    # how to know if it's name or name_ja
                    cat = Category(form.category.data)
                    db.session.add(cat)
                    db.session.commit()

        tags = []
        if form.tags.data:
            for i in form.tags.data.split(';'):
                tag = Tag.query.filter_by(name=i).first()
                if tag:
                    tags.append(tag)
                else:
                    tag = Tag.query.filter_by(name_ja=i).first()
                    if tag:
                        tags.append(tag)
                    else:
                        tag = Tag(i)
                        db.session.add(tag)
                        db.session.commit()
                        tags.append(tag)

        body = form.body.data
        body_ja = form.body_ja.data

        new_post = Post(form.title.data, form.slug.data, cat, tags,
                        date=form.date.data, body=body, body_ja=body_ja)

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('post', slug=form.slug.data))
    return render_template('post_create.html',
                           form=form)

@app.route('/post/<slug>/edit', methods=['GET', 'POST'])
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = PostForm(obj=post)
    if form.validate_on_submit():
        cat = None
        if form.category.data:
            cat = Category.query.filter_by(name=form.category.data).first()
            if cat is None:
                cat = Category.query.filter_by(name_ja=form.category.data).first()
                if cat is None:
                    # how to know if it's name or name_ja
                    cat = Category(form.category.data)
                    db.session.add(cat)
                    db.session.commit()

        tags = []
        if form.tags.data:
            for i in form.tags.data.split(';'):
                tag = Tag.query.filter_by(name=i).first()
                if tag:
                    tags.append(tag)
                else:
                    tag = Tag.query.filter_by(name_ja=i).first()
                    if tag:
                        tags.append(tag)
                    else:
                        tag = Tag(i)
                        db.session.add(tag)
                        db.session.commit()
                        tags.append(tag)

        post.title = form.title.data
        post.slug = form.slug.data
        post.category = cat
        post.tags = tags
        post.date = form.date.data
        post.body = form.body.data
        post.body_html = markdown.markdown(form.body.data, extensions=['codehilite'])
        post.body_ja = form.body_ja.data
        post.body_ja_html = markdown.markdown(form.body_ja.data, extensions=['codehilite'])
        db.session.commit()

        return redirect(url_for('post', slug=form.slug.data))

    return render_template('post_create.html',
                       form=form)


@app.route('/language/<language>')
def change_language(language):
    session['language'] = language
    return redirect(request.args.get('next') or url_for('index'))


# @app.route('/pygments.css')
# def pygments_css():
#     return pygments_style_defs('autumn'), 200, {'Content-Type': 'text/css'}


@app.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url, url=request.url_root)
    posts = [page for page in pages if 'date' in page.meta]
    sorted_posts = sorted(posts, reverse=True,
        key=lambda page: page.meta['date'])[:10]
    for post in sorted_posts:
        feed.add(post.meta['title'], unicode(post.body[:500] + '\n\n....'),
                 content_type='html',
                 author='Jordan',
                 url=make_external(post.path),
                 updated=page.meta['date'])
    return feed.get_response(), 200, {'Content-Type': 'application/atom+xml; charset=utf-8'}


#Adapted from http://flask.pocoo.org/snippets/108/
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    map_pages = []
    ten_days_ago=(datetime.datetime.now() - datetime.timedelta(days=10)).date().isoformat()
    for rule in app.url_map.iter_rules():
      if "GET" in rule.methods and len(rule.arguments) == 0:
          map_pages.append([rule.rule,ten_days_ago])

    tags = Tag.query.all()
    for tag in tags:
        url = url_for('tag_name', name=tag.name)
        map_pages.append([url, ten_days_ago])

    categories = Category.query.all()
    for category in categories:
        url = url_for('category', name=category.name)
        map_pages.append([url, ten_days_ago])

    posts = Post.query.all()
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
    g.user = getattr(g, 'user', None)

    if 'language' not in session:
        session['language'] = request.accept_languages.best_match(LANGUAGES.keys())


@babel.localeselector
def get_locale():
    return session['language']
