from flask import render_template, redirect, url_for, request, session
from app import webapp
from app.db import *
from app.classify import *
from datetime import *

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

    answers = []
    polls = []
    empty_list=[]

    answer1 = request.form.get('answer1', "")
    answer2 = request.form.get('answer2', "")
    answers.append(answer1)
    answers.append(answer2)
    polls.append(empty_list)
    polls.append(empty_list)
    answer_name = 3;

    while request.form.get('answer'+str(answer_name), "")!="":
        answers.append(request.form.get('answer'+str(answer_name), ""))
        answer_name +=1
        polls.append(empty_list)

    ts = int(time.time())
    # check if timestamp exists in POLLS
    key = {'timestamp': str(ts)}
    while db_read(POLLS, key):
        ts = ts + 1
        key['timestamp'] = str(ts)

    # classify poll
    category = classify(question)

    item = {'timestamp': str(ts),
            'question': question,
            'author': username,
            'answers': answers,
            'polls': polls,
            'category': category}
    db_write(POLLS, item)

    # update user's polls
    key = {'username': username}
    item = db_read(USERS, key)
    if 'polls' not in item:
        item['polls'] = []
    item['polls'].append(str(ts))
    db_write(USERS, item)

    session['ret_msg'] = "Success: Poll is created."
    return redirect(url_for('poll_detail', post=str(ts)))
