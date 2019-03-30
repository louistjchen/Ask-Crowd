from flask import redirect, url_for, request, session
from werkzeug.security import check_password_hash
from app import webapp

from app.db import *

@webapp.route('/login', methods=['POST'])
def login():

    username = request.form.get('username', "")
    password = request.form.get('password', "")
    session.pop('ret_msg', None)

    # empty input check
    if username == "" or password == "":
        session['ret_msg'] = "Error: All fields are required!"
        return redirect(url_for('main'))

    # input string validation
    for c in username:
        if c not in username_char:
            session['ret_msg'] = "Error: Username must not contain character: " + c
            return redirect(url_for('main'))
    for c in password:
        if c not in password_char:
            session['ret_msg'] = "Error: Password must not contain character: " + c
            return redirect(url_for('main'))

    key = {'username': username}
    item = db_read(USERS, key)

    if item == None:
        session['ret_msg'] = "Error: No such user"
        return redirect(url_for('main'))

    salt = item['salt']
    hashed_password = item['password']

    if check_password_hash(hashed_password, password + salt):
        session['username'] = username
        return redirect(url_for('main'))
    else:
        session['ret_msg'] = "Error: Password wrong"
        return redirect(url_for('main'))
