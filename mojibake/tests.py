import unittest
import datetime

from main import app, db
from main.models import Post, Category

class Tests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['']
        app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_metadb_build(self):
        test_cat = Category(name='Test')
        test_cat2 = Category(name='Test Posts')
        db.session.add(test_cat)
        db.session.add(test_cat2)
        db.session.commit()
        test_post = Post(title='One', path='',
                         date=datetime.datetime.now(),
                         categories=[test_cat, test_cat2])
        test_post2 = Post(title='Two', path='',
                          date=datetime.datetime.now(),
                          categories=[test_cat])
        db.session.add(test_post)
        db.session.add(test_post2)
        db.session.commit()




if __name__ == '__main__':
    unittest.main()
