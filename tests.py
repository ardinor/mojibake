#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import datetime
from sqlalchemy.exc import IntegrityError

from mojibake.app import app, db
from mojibake.models import Post, Category, Tag, User
from mojibake.settings import TEST_DATABASE_URI

#TO DO: More work on this on testing!
#http://flask.pocoo.org/docs/testing/


class Tests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_categories(self):
        test_cat = Category(name='Test')
        db.session.add(test_cat)
        db.session.commit()
        db_test_cat = Category.query.filter(Category.name == 'Test')
        self.assertEqual(db_test_cat.count(), 1)
        db_test_cat = db_test_cat.first()
        self.assertIsNone(test_cat.name_ja)

        test_cat = Category(name='Test2', name_ja='テスト')
        db.session.add(test_cat)
        db.session.commit()
        db_test_cat = Category.query.filter(Category.name == 'Test2')
        self.assertEqual(db_test_cat.count(), 1)
        db_test_cat = db_test_cat.first()
        self.assertIsNotNone(db_test_cat.name_ja)
        self.assertEqual(test_cat.name_ja, 'テスト')

    def test_category_integrity(self):
        test_cat = Category(name='Test')
        db.session.add(test_cat)
        db.session.commit()
        test_cat2 = Category(name='Test')
        db.session.add(test_cat2)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_posts(self):
        test_post = Post('Test Post', 'test_post')
        test_post.add_category('Test')
        test_post.add_tags('tag1;tag2')
        test_post.add_body('This is a **test** post.', 'これはテスト書き込みですね。')
        test_post.title_ja = 'テスト書き込み'
        db.session.add(test_post)
        db.session.commit()

        db_test_post = Post.query.filter(Post.slug == 'test_post').first()
        self.assertIsNotNone(db_test_post)
        self.assertEqual(db_test_post.body_html, '<p>This is a <strong>test</strong> post.</p>')
        self.assertEqual(db_test_post.body_ja_html, '<p>これはテスト書き込みですね。</p>')
        db_cat = db_test_post.category_id
        self.assertIsNotNone(db_cat)
        db_tags = []
        for tag in db_test_post.tags:
            db_tags.append(tag.id)
        self.assertIsNot(len(db_tags), 0)

        db.session.delete(db_test_post)
        db.session.commit()

        # Ensure orphaned categories and tags are deleted
        cat = Category.query.filter(id == db_cat).first()
        self.assertIsNone(cat)

        for tag_id in db_tags:
            tag = Tag.query.filter(id == tag_id).first()
            self.assertIsNone(tag)


if __name__ == '__main__':
    unittest.main()
