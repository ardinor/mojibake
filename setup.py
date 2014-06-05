# -*- coding: utf-8 -*-
import getpass
#from passlib.hash import pbkdf2_sha256

from mojibake.app import db
from mojibake.models import User
from mojibake.settings import VERSION


def get_admin_details():

    admin_name = input('Input Admin User Name: ')
    pprompt = lambda: (getpass.getpass('Input Admin Password: '), getpass.getpass('Retype password: '))

    p1, p2 = pprompt()
    while p1 != p2:
        print('Passwords do match. Try again.')
        p1, p2 = pprompt()

    #admin_pass = pbkdf2_sha256.encrypt(p1)

    return admin_name, p1


def create_admin(admin_name, admin_pass):

    admin = User(username=admin_name)
    admin.set_password(admin_pass)
    db.session.add(admin)
    db.session.commit()


if __name__ == '__main__':

    print('=== Mojibake Setup v{} ==='.format(VERSION))

    db.create_all()

    admin_name, admin_pass = get_admin_details()
    create_admin(admin_name, admin_pass)

    print('Finished')
