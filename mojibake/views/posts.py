from flask import Blueprint, abort, g, render_template, redirect, url_for

from mojibake.main import db
from mojibake.models import Post
from mojibake.forms import PostForm
from mojibake.settings import POSTS_PER_PAGE
from flask.ext.login import login_required

posts = Blueprint('posts', __name__,
    template_folder='templates')

@posts.route('/posts/')
@posts.route('/posts/<page>/')
def post_list(page=1):
    if g.user is not None and g.user.is_authenticated():
        posts = Post.query.order_by(Post.date.desc()).paginate(int(page), POSTS_PER_PAGE, False)
    else:
        posts = Post.query.filter_by(published=True).order_by(Post.date.desc()).paginate(int(page), POSTS_PER_PAGE, False)

    if posts:
        return render_template('posts.html', posts=posts)
    else:
        abort(404)


@posts.route('/post/<slug>')
def post_item(slug):
    if g.user is not None and g.user.is_authenticated():
        post = Post.query.filter_by(slug=slug).first_or_404()
    else:
        post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template('post.html', post=post)


@posts.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():

    #can't make a post without a published date?

    form = PostForm()
    if form.validate_on_submit():

        new_post = Post(form.title.data, form.slug.data)

        new_post.add_category(form.category.data, form.category_ja.data)
        new_post.add_tags(form.tags.data, form.tags_ja.data)
        new_post.add_body(form.body.data, form.body_ja.data)

        new_post.date = form.date.data
        new_post.published = form.published.data
        new_post.title_ja = form.title_ja.data

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('posts.post_item', slug=form.slug.data))
    return render_template('post_create.html',
                           form=form)

@posts.route('/post/<slug>/edit', methods=['GET', 'POST'])
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
        post.date = form.date.data
        post.published = form.published.data
        db.session.commit()

        return redirect(url_for('posts.post_item', slug=form.slug.data))

    return render_template('post_create.html',
                       form=form)


#change this to GET?
@posts.route('/post/<slug>/delete')
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    db.session.delete(post)
    db.session.commit()
    flash(gettext("Deleted."), 'success')

    return redirect(url_for('posts.post_list'))
