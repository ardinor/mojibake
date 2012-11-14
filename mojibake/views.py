from flask import render_template

from mojibake import app, db
from models import User, Post


@app.route('/')
@app.route('/index')
def index(page=1):
    posts = Post.objects.all()
    return render_template('posts/list.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    pass


@app.route('/post/<slug>')
def get_post(slug):
    pass
