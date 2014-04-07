import collections
from flask.ext.script import Command
import os

from settings import APP_DIR, FLATPAGES_ROOT, FLATPAGES_EXTENSION
#from models import Post
#from mojibake.models import Post
#from app import manager

class ManageMetaDB(Command):

    def __init__(self, db, pages, models):
        self.db = db
        self.pages = pages
        self.Post = models.Post
        self.Tag = models.Tag
        self.Category = models.Category

    def run(self):

        if os.path.exists(os.path.join(APP_DIR, 'app.db')) is False:
            self.db.create_all()
        posts = [page for page in self.pages if 'date' in page.meta]
        for page in posts:
            db_page = self.Post.query.filter_by(path=page.path).first()
            if db_page is None:
                tags = []
                split_tag = page.meta['tags'].split(', ')
                if isinstance(split_tag, list):
                    for i in split_tag:
                        db_tag = self.Tag.query.filter_by(name=i).first()
                        if db_tag is None:
                            db_tag = self.Tag(name=i)
                            self.db.session.add(db_tag)
                            self.db.session.commit()
                            tags.append(db_tag)
                        else:
                            tags.append(db_tag)
                category = page.meta['category']
                db_cat = self.Category.query.filter_by(name=category).first()
                if db_cat is None:
                    db_cat = self.Category(name=category)
                    self.db.session.add(db_cat)
                    self.db.session.commit()
                db_page = self.Post(title=page.meta['title'], path=page.path,
                               date=page.meta['date'], category_id=db_cat.id,
                               tags=tags)
                self.db.session.add(db_page)
                self.db.session.commit()
            else:
                changed = False
                split_tag = page.meta['tags'].split(', ')
                if db_page.title != page.meta['title']:
                    db_page.title = page.meta['title']
                    changed = True
                if db_page.date != page.meta['date']:
                    db_page.date = page.meta['date']
                    changed = True
                db_tags = []
                for i in db_page.tags:
                    db_tags.append(i.name)
                counter = collections.Counter(split_tag)
                counter.subtract(db_tags)
                if list(counter.elements()):
                    tags = []
                    for i in list(counter.elements()):
                        db_tag = self.Tag.query.filter_by(name=i).first()
                        if db_tag is None:
                            db_tag = self.Tag(name=i)
                            self.db.session.add(db_tag)
                            self.db.session.commit()
                        tags.append(db_tag)
                    if tags:
                        changed = True
                        db_page.tags = tags
                db_cat = self.Category.query.filter_by(name=page.meta['category']).first()
                if db_cat is not None:
                    if db_cat.id != db_page.category_id:
                        db_page.category_id = db_cat.id
                        changed = True
                else:
                    db_cat = self.Category(name=page.meta['category'])
                    self.db.session.add(db_cat)
                    self.db.session.commit()
                    db_page.category_id = db_cat.id
                    changed = True


                if changed:
                    self.db.session.commit()

        posts = self.Post.query.all()
        for i in posts:
            if os.path.exists(os.path.join(FLATPAGES_ROOT, i.path+FLATPAGES_EXTENSION)) is False:
                self.db.session.delete(i)
                self.db.session.commit()

        tags = self.Tag.query.all()
        for i in tags:
            if i.posts.count() == 0:
                self.db.session.delete(i)
                self.db.session.commit()

        categories = self.Category.query.all()
        for i in categories:
            if i.posts.count() == 0:
                self.db.session.delete(i)
                self.db.session.commit()

