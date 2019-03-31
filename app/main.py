from flask import render_template, session, request ,send_from_directory
from app import webapp
from app.db import *
from app.macro import *
import os

@webapp.route('/', methods=['GET'])
@webapp.route('/index', methods=['GET'])
@webapp.route('/main', methods=['GET'])
# Display an HTML page with links
def main():

    ret_msg = session['ret_msg'] if 'ret_msg' in session else ""
    session.pop('ret_msg', None)
    hidden = "hidden" if ret_msg == "" else "visible"

    if 'username' in session:
        username = session['username']
        polls = db_scan(table=POLLS, fe=None)

        key = {'username': username}
        user = db_read(USERS, key)

        for i, poll in enumerate(polls):
            voted = False
            for vote in user['votes']:
                if poll['timestamp'] == vote[0]:
                    voted = True
                    break
            if voted:
                polls[i]['voted'] = "X"
            else:
                polls[i]['voted'] = ""

        polls = sorted(polls, key=lambda k: k['timestamp'])
        return render_template("profile.html", username=username, ret_msg=ret_msg, hidden=hidden, polls=polls)
    else:
        return render_template("login.html", username="", password="", ret_msg=ret_msg, hidden=hidden)
