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
    category_num = request.args.get('category_num')
    search = request.args.get('search')

    if not category_num:
        category_num = 0

    categories = ['All', 'Business & Finance', 'Health Care', 'Science & Health', 'Politics & Policy', 'Criminal Justice']
    category = categories[int(category_num)]


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
            session.pop('username', None)
            session.pop('ret_msg', None)
            return render_template("login.html", username="", password="", ret_msg=ret_msg, hidden=hidden)

        users = db_scan(table=USERS, fe=None)
        num_users = len(users)-1

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
            # ts = datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
            ts = datetime.fromtimestamp(ts_epoch).strftime('%b %d, %Y')
            polls[i]['timestamp_'] = ts

        polls = sorted(polls, key=lambda k: k['timestamp'])

        voted_polls = []
        left_polls = []
        for i in range(len(polls)):
            if search == None or searched(polls[i]['question'], search ):
                if polls[i]['category'] == category or category == "All" or category == None:
                    if polls[i]['voted'] == "X":
                        voted_polls.append(polls[i])
                    else:
                        left_polls.append(polls[i])


        return render_template("profile.html", username=username, ret_msg=ret_msg, hidden=hidden, voted_polls=voted_polls, left_polls=left_polls, category_num = int(category_num))
    else:
        return render_template("login.html", username="", password="", ret_msg=ret_msg, hidden=hidden)

def searched(question, search):
    num_of_finds = 0

    words = question.split('?')[0].split(' ')
    search_keywords = search.split(' ')
    threshold = len(search_keywords)/2 if len(search_keywords) >=3 else len(search_keywords)

    for i in range(len(words)):
        for j in range(len(search_keywords)):
            if search_keywords[j].upper() == words[i].upper():
                num_of_finds+=1
                if num_of_finds >= threshold:
                    return True
    return False