from flask import render_template

from mojibake import app, db
from models import User, Post


@app.route('/')
def index(page=1):
    posts = Post.objects.all()
    return render_template('posts/list.html', posts=posts)
