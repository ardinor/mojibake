from flask import Blueprint, abort, g, render_template

from mojibake.models import Tag

tag = Blueprint('tag', __name__,
    template_folder='templates')

@tag.route('/tags/')
def tag_list():
    # Shouldn't be able to make tags with no name, but just in case
    tags = Tag.query.filter(Tag.name != None).filter(Tag.name != ''). \
        order_by('name').all()

    if g.user is None or g.user.is_authenticated() == False:
        for i in tags:
            if i.posts.filter_by(published=True).count() == 0:
                tags.remove(i)

    return render_template('tags.html', tags=tags)


@tag.route('/tags/<name>/')
def tag_name(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    if g.user is None or g.user.is_authenticated() == False:
        if tag.posts.filter_by(published=True).count() == 0:
            abort(404)
    return render_template('tag_list.html', tag=tag)
