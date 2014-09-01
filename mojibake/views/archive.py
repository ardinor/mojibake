from flask import Blueprint, abort, g, render_template
from sqlalchemy.sql import func

from mojibake.models import Post

archive = Blueprint('archive', __name__,
    template_folder='templates')

@archive.route('/')
def archive_list():
    if g.user is not None and g.user.is_authenticated():
        posts = Post.query.filter(Post.date != None).all()
    else:
        posts = Post.query.filter_by(published=True).filter(Post.date != None).all()
    years = list(set([post.date.year for post in posts]))

    return render_template('archive.html', years=years)


@archive.route('/<year>/')
def archive_year(year):
    if g.user is not None and g.user.is_authenticated():
        #year_posts = Post.query.filter("strftime('%Y', date) = :year"). \
        #    params(year=year).order_by('-date').all()
        year_posts = Post.query.filter(func.YEAR(Post.date) == year). \
            params(year=year).order_by('-date').all()
    else:
        #year_posts = Post.query.filter("strftime('%Y', date) = :year"). \
        #    params(year=year).filter_by(published=True).order_by('-date').all()
        year_posts = Post.query.filter(func.YEAR(Post.date) == year). \
            params(year=year).filter_by(published=True).order_by('-date').all()

    if year_posts:
        return render_template('archive_year.html', year=year,
            posts=year_posts)
    else:
        abort(404)
