from flask import render_template, g, redirect, url_for, session, flash, request
from flask.ext.login import login_required, login_user, logout_user, current_user
from passlib.hash import pbkdf2_sha256
from datetime import datetime

from mojibake import app, db, lm
from models import User, Post
from forms import LoginForm, CreateForm


@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    posts = Post.objects.all()
    return render_template('posts/list.html', posts=posts)


@app.route('/post/<slug>')
def get_post(slug):
    pass


@app.route('/post/<slug>/edit')
@login_required
def edit_post(slug):
    pass


@app.route('/profile')
@app.route('/profile/<user>')
def profile(user=None):
    pass


@app.route('/panel')
@login_required
def panel():
    pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('panel'))
    form = LoginForm()
    if form.validate_on_submit():
        logging_in_user = User.objects(username=form.username.data)[0]
        if logging_in_user:
            if pbkdf2_sha256.verify(form.password.data, logging_in_user.password):
                remember_me = False
                if form.remember_me.data:
                    remember_me = True
                login_user(logging_in_user, remember_me=remember_me)
                return redirect(request.args.get('next') or url_for('panel'))
            else:
                flash('Invalid login. Please try again.')
                redirect(url_for('login'))
        else:
            flash('Invalid login. Please try again.')
            redirect(url_for('login'))
    return render_template('login.html',
        title='Sign In',
        form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create', methods=['GET', 'POST'])
def create():
    if app.config['REGISTRATION'] == app.config['REGISTRATION_OPEN']:
        form = CreateForm()
        if form.validate_on_submit():
            new_user = User(username=form.username.data,
                email=form.email.data,
                password=pbkdf2_sha256.encrypt(form.password.data))
            new_user.save()
        else:
            flash('Invalid details. Please try again.')
            redirect(url_for('create'))
        return render_template('create.html',
            title='Create account',
            form=form)
    else:
        return render_template('closed.html',
            title='Registration closed.')



@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        g.user.save()


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
