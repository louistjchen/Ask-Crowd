from flask import render_template, redirect, url_for, request, session
from app import webapp
from app.db import *
from datetime import *

import time


@webapp.route('/account', methods=['GET'])
def account():

    ret_msg = session['ret_msg'] if 'ret_msg' in session else ""
    hidden = "hidden" if ret_msg == "" else "visible"
    session.pop('ret_msg', None)

    username = session['username']
    key = {'username': username}
    item = db_read(USERS, key)

    for i, it in enumerate(item['polls']):
        key = {'timestamp': it}
        poll = db_read(POLLS, key)
        item['polls'][i] = [it, poll['question']]

    for i, it in enumerate(item['votes']):
        key = {'timestamp': it[0]}
        poll = db_read(POLLS, key)
        item['votes'][i].append(poll['question'])

    return render_template("account.html", username=username, ret_msg=ret_msg,
                           item=item, hidden=hidden)

@webapp.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('ret_msg', None)
    return redirect(url_for('main'))
