from flask import Blueprint, abort, g, render_template, redirect, url_for, \
    flash
from flask.ext.babel import gettext
from datetime import timedelta

from mojibake.main import db
from mojibake.models import Post
from mojibake.forms import PostForm
from mojibake.settings import POSTS_PER_PAGE
from flask.ext.login import login_required

posts = Blueprint('posts', __name__,
    template_folder='templates')

@posts.route('/')
@posts.route('/<int:page>/')
def post_list(page=1):
    if g.user is not None and g.user.is_authenticated():
        posts = Post.query.order_by(Post.date.desc()).paginate(int(page), POSTS_PER_PAGE, False)
    else:
        posts = Post.query.filter_by(published=True).order_by(Post.date.desc()).paginate(int(page), POSTS_PER_PAGE, False)

    if posts:
        return render_template('posts.html', posts=posts)
    else:
        abort(404)


@posts.route('/<slug>')
def post_item(slug):
    if g.user is not None and g.user.is_authenticated():
        post = Post.query.filter_by(slug=slug).first_or_404()
    else:
        post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template('post.html', post=post)


@posts.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():

    #can't make a post without a published date?

    form = PostForm()
    if form.validate_on_submit():

        new_post = Post(form.title.data, form.slug.data)

        new_post.add_category(form.category.data, form.category_ja.data)
        new_post.add_tags(form.tags.data, form.tags_ja.data)
        new_post.add_body(form.body.data, form.body_ja.data)

        if new_post.published:
            published_date = form.date.data - timedelta(hours=new_post.get_tz_offset())
            new_post.date = published_date
        new_post.title_ja = form.title_ja.data

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('posts.post_item', slug=form.slug.data))
    return render_template('post_create.html',
                           form=form)

@posts.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = PostForm(obj=post)
    if form.validate_on_submit():
        # Still if you change the ja category or tag (as in add a translation),
        # the below won't update it
        post.add_category(form.category.data, form.category_ja.data)
        post.add_tags(form.tags.data, form.tags_ja.data)
        post.add_body(form.body.data, form.body_ja.data)

        post.title = form.title.data
        post.title_ja = form.title_ja.data
        post.slug = form.slug.data
        post.published = form.published.data
        if post.published:
            published_date = form.date.data - timedelta(hours=post.get_tz_offset())
            post.date = published_date
        db.session.commit()

        return redirect(url_for('posts.post_item', slug=form.slug.data))

    return render_template('post_create.html',
                       form=form)


@posts.route('/<slug>/delete')
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    cat = post.category
    tags = post.tags
    db.session.delete(post)
    db.session.commit()
    if cat.posts.count() == 0:
        db.session.delete(cat)
        db.session.commit()
    for i in tags:
        if i.posts.count() == 0:
            db.session.delete(i)
            db.session.commit()
    flash(gettext("Deleted."), 'success')

    return redirect(url_for('posts.post_list'))
