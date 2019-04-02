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

    data = []
    key = {'username': 'ATTRIBUTES'}
    attributes = db_read(USERS, key)['attributes']

    for attr in attributes:
        temp = [['name', attr], [], []]
        data.append(temp)

    for user in users:
        key = {'username': user}
        user_info = db_read(USERS, key)

        print(data)

        for d in data:
            vote = None

            if d[0][1] in user_info['attributes']:
                vote = user_info[d[0][1]]
            else:
                vote = "wish not to disclose"

            write = False
            try:
                print('a')
                index = d[1].index(vote)
                print('b')
                d[2][index] = d[2][index] + 1
            except:
                print('except')
                d[1].append(vote)
                d[2].append(1)

    print(data)

    return render_template("analysis.html", data=data)
