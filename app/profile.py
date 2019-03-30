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
    ret_msg = ""

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
    session['ret_msg'] = "Success: Poll is created."
    return redirect(url_for('main'))

@webapp.route('/poll/<id>', methods=['GET'])
def poll_detail(id):
    print(id)
    return redirect(url_for('main'))

@webapp.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('ret_msg', None)
    return redirect(url_for('main'))
