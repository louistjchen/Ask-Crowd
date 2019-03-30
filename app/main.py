from flask import render_template, session, request ,send_from_directory
from app import webapp
from app import db
from app import macro
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
        polls = db.db_scan(table=macro.POLLS, fe=None)
        return render_template("profile.html", username=username, ret_msg=ret_msg, hidden=hidden, polls=polls)
    else:
        return render_template("login.html", username="", password="", ret_msg=ret_msg, hidden=hidden)
