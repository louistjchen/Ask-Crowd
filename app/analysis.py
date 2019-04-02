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
        temp = []
        temp.append(['name', attr])
        data.append(temp)

    for user in users:
        key = {'username': user}
        user_info = db_read(USERS, key)

        for i, d in enumerate(data):
            vote = None

            if d[0][1] in user_info['attributes']:
                vote = user_info[d[0][1]]
            else:
                vote = "wish not to disclose"
            write = False
            for v in d:
                if v[0] == vote:
                    v[1] = str(int(v[1])+1)
                    write = True
                    break

            if write == False:
                data[i].append([vote, '1'])

    print(data)

    return redirect(url_for('poll_detail', post=post))
