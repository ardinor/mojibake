# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from mojibake.app import db
from mojibake.models import Category, Post, Tag, User, \
    IPAddr, BannedIPs, BreakinAttempts

def create_test_monitoring():

    # Since we changed the date monitoring looks for (see monitoring/views.py)
    # Set the date to the Oct 2014 so they show up
    last_month = datetime(2014, 10, 12)

    db.session.query(IPAddr).delete()
    db.session.query(BreakinAttempts).delete()
    ip1 = IPAddr('192.168.1.1')
    ip1.region = 'Test'
    ip1.country = 'Antartica'
    ip2 = IPAddr('10.0.0.1')
    ip2.region = 'Unknown'
    ip2.country = 'Luxembourg'
    ip3 = IPAddr('172.16.0.1')
    ip3.region = '大阪'
    ip3.country = '日本'
    db.session.add(ip1)
    db.session.add(ip2)
    db.session.add(ip3)
    db.session.commit()
    b1 = BreakinAttempts(date=last_month, user='admin')
    b1.ip = ip1
    b2 = BreakinAttempts(date=last_month, user='admin')
    b2.ip = ip1
    b3 = BreakinAttempts(date=last_month, user='admin')
    b3.ip = ip1
    b4 = BreakinAttempts(date=last_month, user='oracle')
    b4.ip = ip2
    b5 = BreakinAttempts(date=last_month, user='aaa')
    b5.ip = ip3
    b6 = BreakinAttempts(date=last_month, user='qwe')
    b6.ip = ip3
    b7 = BreakinAttempts(date=last_month, user='qwe')
    b7.ip = ip3
    b8 = BreakinAttempts(date=last_month, user='qwe')
    b8.ip = ip3
    db.session.add(b1)
    db.session.add(b2)
    db.session.add(b3)
    db.session.add(b4)
    db.session.add(b5)
    db.session.add(b6)
    db.session.add(b7)
    db.session.add(b8)
    db.session.commit()
    ba1 = BannedIPs(date=last_month)
    ba1.ipaddr = ip1.id
    db.session.add(ba1)
    db.session.commit()

def create_test_posts():
    p1 = Post('Test Post', 'test_post')
    p1.add_category('Testing', 'テスト中')
    p1.add_tags('test;experiment', 'テスト;実験')
    p1.add_body('This is a test post.', 'これはテストの書き込みです。')
    p1.published = True
    p1.date = datetime.now() - timedelta(hours=p1.get_tz_offset())
    db.session.add(p1)
    db.session.commit()
    p2 = Post('Another Test Post', 'another_test_post')
    p2.add_category('Testing Another')
    p2.add_tags('test;experiment')
    p2.add_body('This is another test post.')
    db.session.add(p2)
    db.session.commit()

if __name__ == '__main__':
    db.create_all()
    #create_test_posts()
    create_test_monitoring()
