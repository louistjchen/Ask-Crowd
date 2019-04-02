from flask import render_template, redirect, url_for, request, session
from app import webapp
from app.db import *
from datetime import *

import time

@webapp.route('/poll/<post>', methods=['GET'])
def poll_detail(post):

    ret_msg = session['ret_msg'] if 'ret_msg' in session else ""
    hidden = "hidden" if ret_msg == "" else "visible"
    session.pop('ret_msg', None)

    username = session['username']
    key = {'timestamp': post}
    item = db_read(POLLS, key)

    if item == None:
        session['ret_msg'] = "Error: Cannot retrieve selected poll."
        return redirect(url_for('main'))

    item['voted'] = []
    for i, poll in enumerate(item['polls']):
        if username in poll:
            item['voted'].append("X")
        else:
            item['voted'].append("")
        item['voted']

        ts_epoch = int(item['timestamp'])
        ts = datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
        item['timestamp_'] = ts

        item['polls'][i] = len(poll)
    length = len(item['polls'])

    return render_template("poll.html", username=username, ret_msg=ret_msg, hidden=hidden,
                           item=item, length=range(length))

@webapp.route('/poll/<post>/<index>', methods=['GET'])
def poll_vote(post, index):

    session.pop('ret_msg', None)
    username = session['username']

    key = {'username': username}
    user = db_read(USERS, key)
    key = {'timestamp': post}
    poll = db_read(POLLS, key)

    if 'votes' not in user:
        user['votes'] = []
    for vote in user['votes']:
        if vote[0] == post:
            session['ret_msg'] = "Error: You have previously voted \"" + poll['answers'][int(vote[1])] + "\" on this poll."
            return redirect(url_for('poll_detail', post=post))

    # update user
    user['votes'].append([post, index])
    db_write(USERS, user)

    # update poll
    poll['polls'][int(index)].append(username)
    db_write(POLLS, poll)

    session['ret_msg'] = "Success: You have successfully voted \"" + poll['answers'][int(index)] + "\"."
    return redirect(url_for('poll_detail', post=post))


@webapp.route('/delete_poll/<post>', methods=['POST'])
def delete_poll(post):

    key = {'timestamp': post}
    poll = db_read(POLLS, key)

    # delete poll from author
    key = {'username': poll['author']}
    user = db_read(USERS, key)
    user['polls'].remove(post)
    db_write(USERS, user)

    # delete poll from users who have voted
    for option in poll['polls']:
        for voter in option:
            key = {'username': voter}
            user = db_read(USERS, key)
            for vote in user['votes']:
                if vote[0] == post:
                    user['votes'].remove(vote)
                    break
            db_write(USERS, user)

    # delete poll
    key = {'timestamp': post}
    db_delete(POLLS, key)

    return redirect(url_for('account'))