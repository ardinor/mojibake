from flask import Blueprint, render_template

projects = Blueprint('projects', __name__,
                     template_folder='templates')


@projects.route('/')
def home():
    return render_template('projects/index.html')
