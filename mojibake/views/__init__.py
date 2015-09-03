from flask import render_template, g, session, request, url_for, \
    make_response
from flask.ext.login import current_user

from mojibake.app import app, babel, login_manager
from mojibake.settings import LANGUAGES
from mojibake.models import User, Tag, Category, Post

import datetime


# Adapted from http://flask.pocoo.org/snippets/108/
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    hide_views = ['/posts/create', '/post/<slug>/edit', '/post/<slug>/delete',
                  '/translate', '/login', '/logout', '/sitemap.xml']

    map_pages = []
    ten_days_ago = (datetime.datetime.now() - datetime.timedelta(days=10)).date().isoformat()
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            # kind of a temporary hack, I'd like to find a better way to do this
            if (rule.rule in hide_views) == False:
                map_pages.append([rule.rule, ten_days_ago])

    tags = Tag.query.all()
    for tag in tags:
        if tag.posts.filter_by(published=True).count() > 0:
            url = url_for('tag.tag_name', name=tag.name)
            map_pages.append([url, ten_days_ago])

    categories = Category.query.all()
    for category in categories:
        if category.posts.filter_by(published=True).count() > 0:
            url = url_for('category.category_item', name=category.name)
            map_pages.append([url, ten_days_ago])

    posts = Post.query.filter_by(published=True).all()
    for post in posts:
        url = url_for('posts.post_item', slug=post.slug)
        map_pages.append([url, ten_days_ago])

    sitemap_xml = render_template('sitemap_template.xml', pages=map_pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response

# Scratch that, don't need this
# @app.route('/robots.txt')
# def robots():
#     response = make_response("User-agent: *\nDisallow:")
#     response.headers["Content-Type"] = "text/plain"
#     return response


@app.errorhandler(404)
def internal_error400(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error500(error):
    app.logger.error('500 internal server error - %s', error)
    return render_template('500.html'), 500


@app.before_request
def before_request():
    # g.user = getattr(g, 'user', None)
    g.user = current_user


@babel.localeselector
def get_locale():

    if 'language' not in session:
        session['language'] = request.accept_languages.best_match(LANGUAGES.keys())
    return session['language']


@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=userid).first()


@login_manager.unauthorized_handler
def unauthorised():
    return render_template('unauthorised.html'), 403
