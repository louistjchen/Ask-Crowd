from flask import render_template, redirect, url_for, request, session
from app import webapp
from flask_mail import Mail, Message
from app.db import *
from datetime import *

# share via email settings
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'ece1778moneyjars@gmail.com',
    "MAIL_PASSWORD": 'ece1778pass'
}

# lambda_url = "http://127.0.0.1:5000"
lambda_url = "https://sny4ch5mqd.execute-api.us-east-1.amazonaws.com/dev"

webapp.config.update(mail_settings)
mail = Mail(webapp)

@webapp.route('/poll/<post>', methods=['GET'])
def poll_detail(post):

    if 'username' not in session:
        return render_template("login.html", username="", password="", ret_msg="", hidden="hidden")

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
    voted = False
    for i, poll in enumerate(item['polls']):
        if username in poll:
            item['voted'].append("X")
            voted = True
        else:
            item['voted'].append("")
        item['voted']

        ts_epoch = int(item['timestamp'])
        # ts = datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
        ts = datetime.fromtimestamp(ts_epoch).strftime('%b %d, %Y')
        item['timestamp_'] = ts

        item['polls'][i] = len(poll)
    length = len(item['polls'])

    suggestions = []
    category = item['category']
    if voted:
        key = {'username': username}
        user = db_read(USERS, key)
        votes = []
        for vote in user['votes']:
            votes.append(vote[0])

        polls = db_scan(POLLS, None)
        polls = sorted(polls, key=lambda k: k['timestamp'])
        for poll in polls:
            if poll['category'] == category and poll['timestamp'] != post and poll['timestamp'] not in votes:
                suggestions.append([poll['timestamp'], poll['question']])

    return render_template("poll.html", username=username, ret_msg=ret_msg, hidden=hidden,
                           item=item, length=range(length), suggestions=suggestions)

@webapp.route('/email/<post>/<email>', methods=['GET'])
def email(post, email):

    url = lambda_url + "/poll/" + post
    subject = "AskCrowd Poll Invitation"
    body = "Hi there,\n\nAskCrowd has sent you an invitation link to complete a suggested poll. Please consider taking a few minutes to complete it!\n\n"
    body = body + "\t\t" + url + "\n\n"
    body = body + "Best regards,\nAskCrowd Team"

    try:
        with webapp.app_context():
            msg = Message(subject=subject,
                          sender=webapp.config.get("MAIL_USERNAME"),
                          recipients=[email],  # replace with your email for testing
                          body=body)
            mail.send(msg)
            session['ret_msg'] = "Success: You have successfully shared this poll to <" + email + ">."
    except:
        session['ret_msg'] = "Error: An error has occurred when sharing this poll. Please validate email."

    return redirect(url_for('poll_detail', post=post))


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
