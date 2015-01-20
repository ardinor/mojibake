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
    db.session.query(BannedIPs).delete()  # need this?

    sample_ip_data = {
        '192.168.1.1': ['McMurdo', 'Antartica'],
        '10.0.0.1': ['Luxembourg City', 'Luxembourg'],
        '172.16.0.1': ['大阪', '日本'],
        '172.16.0.56': ['熊本県', '日本'],
        '163.12.76.193': ['Düsseldorf', 'Germany'],
        '163.12.76.222': ['Düsseldorf', 'Germany'],
        '74.123.51.130': ['Ljubljana', 'Slovenia'],
        '74.123.51.139': ['Ljubljana', 'Slovenia'],
        '74.123.51.240': ['Ljubljana', 'Slovenia'],
        '74.123.51.251': ['Ljubljana', 'Slovenia'],
    }

    sample_attempts = {
        '192.168.1.1': ['admin', 'admin', 'admin', 'admin'],
        '10.0.0.1': ['oracle', 'nagios', 'aaa'],
        '172.16.0.1': ['aaa', 'aaa', 'aaa'],
        '172.16.0.56': ['qwe', 'qwe', 'qwe'],
        '163.12.76.193': ['wertwasdcw', 'Hanz', 'Hanz', 'Prometheus'],
        '163.12.76.222': ['asdqwqwqq', 'bob'],
        '74.123.51.130': ['abebrabr', 'abebrabr', 'aberbaerb', 'aberbaerb', 'aberbaerb'],
        '74.123.51.139': ['abebrabr', 'abebrabr', 'aberbaerb'],
        '74.123.51.240': ['abebrabr', 'abebrabr', 'aberbaerb'],
        '74.123.51.251': ['abebrabr', 'abebrabr', 'aberbaerb'],
    }

    sample_bans = [
        '192.168.1.1',
    ]

    for i, j in sample_ip_data.items():

        ip_entry = IPAddr(i)
        ip_entry.region = j[0]
        ip_entry.country = j[1]
        db.session.add(ip_entry)
        db.session.commit()

        for user in sample_attempts[i]:
            attempt = BreakinAttempts(date=last_month, user=user)
            attempt.ip = ip_entry
            db.session.add(attempt)
        db.session.commit()

        if i in sample_bans:
            sample_ban = BannedIPs(date=last_month)
            sample_ban.ipaddr = ip_entry.id
            db.session.add(sample_ban)
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
