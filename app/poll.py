from flask import render_template, redirect, url_for, request, session
from app import webapp
from flask_mail import Mail, Message
from app.db import *
from datetime import *
import time

import boto3
from botocore.exceptions import ClientError

key = {'name': 'email'}
email_info = db_read(INFO, key)

# share via email settings
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": email_info['username'],
    "MAIL_PASSWORD": email_info['password']
}

# lambda_url = "http://127.0.0.1:5000"
lambda_url = email_info['lambda_url']

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

    if item['allow_comment'] == "on":
        comments = retrieve_comments(post)
        allow_comment_display = "visible"
    else:
        comments = []
        allow_comment_display = "hidden"

    return render_template("poll.html", username=username, ret_msg=ret_msg, hidden=hidden,
                           item=item, length=range(length), suggestions=suggestions, comments=comments, allow_comment_display=allow_comment_display)

@webapp.route('/email/<post>/<email>', methods=['GET'])
def email(post, email):
    URL = lambda_url + "/poll/" + post

    BODY_HTML ='''
        <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
        <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
          <meta http-equiv="Content-Style-Type" content="text/css">
          <title></title>
          <meta name="Generator" content="Cocoa HTML Writer">
          <meta name="CocoaVersion" content="1561.6">
          <style type="text/css">
            p.p1 {margin: 0.0px 0.0px 0.0px 0.0px; text-align: center; line-height: 56.0px; font: 48.0px Menlo; color: #000000; -webkit-text-stroke: #000000; background-color: #ffffff; min-height: 56.0px}
            p.p2 {margin: 0.0px 0.0px 0.0px 0.0px; text-align: center; line-height: 56.0px; font: 48.0px Menlo; color: #000000; -webkit-text-stroke: #000000; background-color: #ffffff}
            p.p3 {margin: 0.0px 0.0px 0.0px 0.0px; text-align: center; line-height: 14.0px; font: 12.0px Menlo; color: #000000; -webkit-text-stroke: #000000}
            p.p4 {margin: 0.0px 0.0px 0.0px 0.0px; text-align: center; line-height: 16.0px; font: 14.0px Menlo; color: #000000; -webkit-text-stroke: #000000; background-color: #ffffff}
            p.p5 {margin: 0.0px 0.0px 0.0px 0.0px; text-align: center; line-height: 16.0px; font: 14.0px Menlo; color: #0433ff; -webkit-text-stroke: #0433ff; background-color: #ffffff}
            span.s1 {font-kerning: none}
          </style>
        </head>
        <body>
        <p class="p1"><span class="s1"><b></b></span><br></p>
        <p class="p1"><span class="s1"><b></b></span><br></p>
        <p class="p1"><span class="s1"><b></b></span><br></p>
        <p class="p2"><span class="s1"><b>AskCrowd</b></span></p>
        <p class="p3"><span class="s1"><br>
        </span></p>
        <p class="p4"><span class="s1">Hi there, AskCrowd has sent you an invitation link to complete a suggested poll.<span class="Apple-converted-space"> </span></span></p>
        <p class="p4"><span class="s1">Please consider taking a few minutes to complete it!</span></p>
        <p class="p3"><span class="s1"><br>
        </span></p>
        <p class="p5"><span class="s1">
        '''+URL+'''
        </span></p>
        <p class="p3"><span class="s1"><br>
        </span></p>
        <p class="p4"><span class="s1">Best regards</span></p>
        <p class="p4"><span class="s1">AskCrowd Team</span></p>
        </body>
        </html>

        
    '''
    SENDER = "ece1778moneyjars@gmail.com"

    RECIPIENT = email

    AWS_REGION = "us-east-1"

    SUBJECT = "AskCrowd Poll Invitation"

    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    }
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
        )
    except ClientError as e:
        session['ret_msg'] = e.response['Error']['Message']
    else:
        session['ret_msg'] = "Success: You have successfully shared this poll to <" + email + ">."

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
    db_delete(COMMENTS, key)

    return redirect(url_for('account'))

@webapp.route('/comment_poll/<post>/<comment>', methods=['GET'])
def comment_poll(post, comment):

    username = session['username']
    key = {'timestamp': post}
    comments = db_read(COMMENTS, key)

    if comments == None:
        comments = {'timestamp': post,
                   'comments': []}

    key = {'username': username}
    user = db_read(USERS, key)
    profile_image = user['profile_image']

    ts = int(time.time())
    comment_item = {'username': username,
                    'comment': comment,
                    'timestamp': ts,
                    'profile_image':profile_image}
    comments['comments'].append(comment_item)
    db_write(COMMENTS, comments)
    return redirect(url_for('poll_detail', post=post))

def retrieve_comments(post):

    key = {'timestamp': post}
    comments = db_read(COMMENTS, key)
    if comments == None:
        comments = []
    else:
        comments  =   comments['comments']
        for comment in comments:
            ts_epoch = int(comment['timestamp'])
            ts = datetime.fromtimestamp(ts_epoch).strftime('%H:%M:%S on %b %d, %Y')
            comment['timestamp_'] = ts
        # comments = sorted(comments, key=lambda k: k['timestamp'])

    return comments
