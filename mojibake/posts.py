from flask import render_template, g, flash, \
    redirect, url_for, Blueprint
from flask.ext.babel import gettext
from flask.ext.login import login_required

from cgi import escape
import markdown

from models import User, Post, Comment
from forms import PostForm, CommentForm, UserCommentForm
from models import ROLE_ADMIN, COMMENT_APPROVED

posts = Blueprint('posts', __name__, template_folder='templates/posts')


@posts.route('/post/<slug>', methods=['GET', 'POST'])
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
    return render_template('detail.html',
                           post=post,
                           slug=slug,
                           form=form,
                           user=user,
                           title=post.title)


@posts.route('/post/<slug>/edit', methods=['GET', 'POST'])
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
        post.body_html = markdown.markdown(post.body, extensions=['codehilite'])
        post.visible = form.visible.data
        post.tags = tags
        post.save()
        flash(gettext('Post updated!'), 'success')
        return redirect(url_for('get_post', slug=slug))
    return render_template('edit.html',
                           form=form,
                           title='Edit Post')


@posts.route('/post/<slug>/delete', methods=['GET'])
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


@posts.route('/post/new', methods=['GET', 'POST'])
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
                    body_html=markdown.markdown(form.body.data, extensions=['codehilite']),
                    visible=form.visible.data,
                    author=User.objects(id=user.id)[0],
                    tags=tags_list)  # tags not right I think
        post.save()
        user.posts.append(post)
        flash(gettext('Post created!'), 'success')
        return redirect(url_for('get_post', slug=post.slug))
    return render_template('edit.html',
                           form=form,
                           title=gettext('New Post'))
