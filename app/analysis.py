from flask import render_template, redirect, url_for, request, session
from app import webapp
from app.db import *

@webapp.route('/analysis/<post>/<index>', methods=['GET'])
def analysis(post, index):

    key = {'timestamp': post}
    poll = db_read(POLLS, key)
    users = []
    for user in poll['polls'][int(index)]:
        users.append(user)
    answer = poll['answers'][int(index)]

    data = []
    key = {'username': 'ATTRIBUTES'}
    attributes = db_read(USERS, key)['attributes']

    for attr in attributes:
        temp = [attr, [], []]
        data.append(temp)

    for user in users:
        key = {'username': user}
        user_info = db_read(USERS, key)

        for d in data:
            vote = None

            if d[0] in user_info['attributes']:
                vote = user_info[d[0]]
            else:
                vote = "wish not to disclose"

            write = False
            try:
                index = d[1].index(vote)
                d[2][index] = d[2][index] + 1
            except:
                d[1].append(vote)
                d[2].append(1)

    return render_template("analysis.html", poll=poll, answer=answer, data=data)
