# -*- coding: utf-8 -*-
import getpass
import argparse
#from passlib.hash import pbkdf2_sha256

from mojibake.app import db
from mojibake.models import User
from mojibake.settings import VERSION


def get_pass():

    pprompt = lambda: (getpass.getpass('Input Admin Password: '), getpass.getpass('Retype password: '))

    p1, p2 = pprompt()
    while p1 != p2:
        print('Passwords do match. Try again.')
        p1, p2 = pprompt()

    return p1

def get_admin_details():

    admin_name = input('Input Admin User Name: ')

    p1 = get_pass()

    return admin_name, p1

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

    arg_parser.add_argument('-r', '--reset-pass',
            action='store_true',
            default=False,
            dest='reset_pass',
            help='Reset the admin password.')

    args = arg_parser.parse_args()

    print('=== Mojibake Setup v{} ==='.format(VERSION))

    if args.reset_pass:
        print('Reset Admin Pass.')
        print("If you continue, the site admin's password will be reset.")
        while 1:
            response = input('Do you wish to continue? (y/n) -> ')
            if response.lower() == 'y':
                response = input('Admin username: ')
                if response:
                    admin = get_admin(response)
                    if admin:
                        new_pass = get_pass()
                        admin.set_password(new_pass)
                        db.session.add(admin)
                        db.session.commit()
                    else:
                        print('User {} not found.'.format(response))
                break
            elif response.lower() == 'n':
                break
            else:
                print('Unknown respose: {}'.format(response))

    else:
        print('Initial Setup.')
        print('This will create all the tables and create a new admin user.')
        while 1:
            response = input('Do you wish to continue? (y/n) -> ')
            if response == 'y':
                db.create_all()

                admin_name, admin_pass = get_admin_details()
                create_admin(admin_name, admin_pass)

                break
            elif response == 'n':
                break
            else:
                print('Unknown respose: {}'.format(response))
    print('Finished')
