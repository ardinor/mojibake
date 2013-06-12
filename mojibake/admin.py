from flask import Blueprint, g, render_template, \
    request, jsonify

from flask.ext.login import login_required

from models import User, Post
from config import POSTS_PER_PAGE

admin = Blueprint('admin', __name__, template_folder='templates/admin')


@admin.route('/admin')
@admin.route('/admin/<int:page>')
@login_required
def admin_panel(page=1):
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
    return render_template('admin.html',
                           user=user,
                           pagination=posts,
                           comments=awaiting_comments)


@admin.route('/admin/comment/approve')
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


@admin.route('/admin/comment/delete')
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
