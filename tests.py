# -*- coding: utf-8 -*-

import unittest
import datetime

from mojibake.app import app, db
from mojibake.models import Post, Category, Tag, User
from mojibake.settings import TEST_DATABASE

#TO DO: More work on this on testing!
#http://flask.pocoo.org/docs/testing/


class Tests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_categories(self):
        test_cat = Category(name='Test')
        db.session.add(test_cat)
        db.session.commit()
        self.assertEqual(test_cat.name_ja, None)
        test_cat2 = Category(name='Test2', name_ja='テスト')
        db.session.add(test_cat2)
        db.session.commit()
        assert test_cat2.name_ja != None

    @unittest.expectedFailure
    def test_category_integrity(self):
        test_cat = Category(name='Test')
        db.session.add(test_cat)
        db.session.commit()
        test_cat2 = Category(name='Test')
        db.session.add(test_cat2)
        db.session.commit()

    #def test_posts(self):




if __name__ == '__main__':
    unittest.main()
