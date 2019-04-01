from flask import render_template, redirect, url_for, request, session
from app import webapp
from app.db import *

import time

@webapp.route('/ask', methods=['GET'])
def ask_form():
    username = session['username']
    return render_template("ask.html", username=username, ret_msg="", hidden="hidden")

@webapp.route('/ask', methods=['POST'])
def ask():
    username = session['username']
    session.pop('ret_msg', None)

    # to be modified as adaptive answer column
    question = request.form.get('question', "")
    answer1 = request.form.get('answer1', "")
    answer2 = request.form.get('answer2', "")

    if question == "" or answer1 == "" or answer2 == "":
        ret_msg = "Error: All fields are required!"
        return render_template("ask.html", ret_msg=ret_msg, username=username,
                               question=question, answer1=answer1, answer2=answer2,
                               hidden="visible")

    ts = int(time.time())
    # check if timestamp exists in POLLS
    key = {'timestamp': str(ts)}
    while db_read(POLLS, key):
        ts = ts + 1
        key['timestamp'] = str(ts)

    item = {'timestamp': str(ts),
            'question': question,
            'author': username,
            'answers': [answer1, answer2],
            'polls': [[], []]}
    db_write(POLLS, item)

    # update user's polls
    key = {'username': username}
    item = db_read(USERS, key)
    if 'polls' not in item:
        item['polls'] = []
    item['polls'].append(str(ts))
    db_write(USERS, item)

    session['ret_msg'] = "Success: Poll is created."
    return redirect(url_for('main'))

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

@webapp.route('/account', methods=['GET'])
def account():

    ret_msg = session['ret_msg'] if 'ret_msg' in session else ""
    hidden = "hidden" if ret_msg == "" else "visible"
    session.pop('ret_msg', None)

    username = session['username']
    key = {'username': username}
    item = db_read(USERS, key)
    return render_template("account.html", username=username, ret_msg=ret_msg,
                           item=item, hidden=hidden)

@webapp.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('ret_msg', None)
    return redirect(url_for('main'))
