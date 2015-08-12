# -*- coding: utf-8 -*-
import argparse
from sqlalchemy.engine.reflection import Inspector

from mojibake.app import db
from mojibake.models import User
from mojibake.settings import VERSION


def create_admin(admin_name, admin_pass):

    admin = User(username=admin_name)
    admin.set_password(admin_pass)
    db.session.add(admin)
    db.session.commit()


def get_admin(admin_name):
    admin = User.query.filter_by(username=admin_name).first()
    if admin:
        return admin
    else:
        return None


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description='Mojibake Setup')

    arg_parser.add_argument('username', help="The admin user's username")
    arg_parser.add_argument('password', help="The admin user's password")

    arg_parser.add_argument('-r', '--reset-pass',
                            action='store_true',
                            default=False,
                            dest='reset_pass',
                            help='Reset the admin password.')

    args = arg_parser.parse_args()

    print('=== Mojibake Setup v{} ==='.format(VERSION))

    if args.reset_pass:
        print('Reset Admin Pass.')
        admin = get_admin(args.username)
        if admin:
            admin.set_password(args.password)
            db.session.add(admin)
            db.session.commit()
        else:
            print('User {} not found.'.format(args.username))

    else:
        # inspector = Inspector.from_engine(db.engine)
        # table_names = inspector.get_table_names()
        # if 'User' not in table_names:
        #     #db.engine.dialect.has_table(db.engine.connect(), 'User')
        #     print('Initial Setup.')
        #     print('This will create all the tables and create a new admin user.')
        db.create_all()
        admin = get_admin(args.username)
        if admin is None:
            create_admin(args.username, args.password)
        else:
            print("Admin already exists, doing nothing...")
    print('Finished')
