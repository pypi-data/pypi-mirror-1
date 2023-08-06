# encoding: utf-8
"""
user_manage.py

Created by Chris Miles on 2007-02-07.
Copyright (c) 2007 Chris Miles. All rights reserved.
"""

import sys


def user_add(username=None, email=None, displayname=None, password=None, ask=True):
    from zoner import model
    
    while not username:
        sys.stdout.write('Username: ')
        username = sys.stdin.readline().strip()
    
    while not email:
        sys.stdout.write('E-mail Address: ')
        email = sys.stdin.readline().strip()
    
    while not displayname:
        sys.stdout.write('Display Name: ')
        displayname = sys.stdin.readline().strip()
    
    while not password:
        sys.stdout.write('Password: ')
        password = sys.stdin.readline().strip()
    
    print "\nReady to add user:"
    print "  username:       %s" % username
    print "  email:          %s" % email
    print "  display name:   %s" % displayname
    print "  password:       %s" % password
    
    answer = ''
    while answer.lower() not in ('y', 'n'):
        sys.stdout.write('Add user? [y/N] ')
        answer = sys.stdin.readline().strip()
        if answer == '\n':
            answer = 'n'
    
    if answer == 'y':
        u = model.User(
            user_name       = unicode(username),
            email_address   = unicode(email),
            display_name    = unicode(displayname),
            password        = unicode(password),
        )
        model.session.flush()


def user_delete(username=None, ask=True):
    from zoner import model
    
    raise NotImplementedError("TODO")

