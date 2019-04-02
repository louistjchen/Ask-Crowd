from flask import render_template, session, request ,send_from_directory
from app import webapp
from app.db import *
from app.macro import *
from datetime import *

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

        # prevent username session cache problem
        if user == None:
            return render_template("login.html", username="", password="", ret_msg=ret_msg, hidden=hidden)

        users = db_scan(table=USERS, fe=None)
        num_users = len(users)

        for i, poll in enumerate(polls):
            # retrieve voted
            voted = False
            for vote in user['votes']:
                if poll['timestamp'] == vote[0]:
                    voted = True
                    break
            if voted:
                polls[i]['voted'] = "X"
            else:
                polls[i]['voted'] = ""

            # retrieve participation rate
            num_participate_users = 0
            for vote in poll['polls']:
                num_participate_users = num_participate_users + len(vote)
            participation = num_participate_users * 100 / num_users
            polls[i]['participation'] = int(participation)

            ts_epoch = int(polls[i]['timestamp'])
            ts = datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
            polls[i]['timestamp_'] = ts

        polls = sorted(polls, key=lambda k: k['timestamp'])
        return render_template("profile.html", username=username, ret_msg=ret_msg, hidden=hidden, polls=polls)
    else:
        return render_template("login.html", username="", password="", ret_msg=ret_msg, hidden=hidden)
