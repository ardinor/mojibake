from flask import Blueprint, abort, g, render_template

from mojibake.models import Category

category = Blueprint('category', __name__,
                     template_folder='templates')


@category.route('/')
def category_list():
    # Shouldn't be able to create categories with no name, but just in case
    categories = Category.query.filter(Category.name != None). \
        filter(Category.name != '').order_by('name').all()

    if g.user is None or g.user.is_authenticated() == False:
        for i in categories:
            if i.posts.filter_by(published=True).count() == 0:
                categories.remove(i)

    return render_template('categories.html', categories=categories)


@category.route('/<name>/')
def category_item(name):
    category = Category.query.filter_by(name=name).first_or_404()
    if g.user is None or g.user.is_authenticated() == False:
        if category.posts.filter_by(published=True).count() == 0:
            abort(404)
    return render_template('category.html', category=category)
