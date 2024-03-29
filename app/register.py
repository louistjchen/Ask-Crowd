from flask import render_template, redirect, url_for, request, session
from werkzeug.security import generate_password_hash
from app import webapp
from app.db import *
import os
import time
import datetime

def get_image_extension(name):
    ret = ""
    for c in reversed(name):
        ret = c + ret
        if c == '.':
            return ret
    return ""

@webapp.route('/register', methods=['GET'])
def register_form():
    start = 1900
    end = 2020

    years = []
    years.append("--Select--")
    for i in range(end-start):
            years.append(start+i)

    occupations =[]
    occupations.append("--Select--")
    occupations.append("Student")
    occupations.append("Politician")
    occupations.append("Engineer")
    occupations.append("Teacher")

    return render_template("register.html", ret_msg="", hidden="hidden", years=years, occupations = occupations)


@webapp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', "")
    password = request.form.get('password', "")
    confirm_password = request.form.get('confirm_password', "")

    # to be modified
    sex = request.form.get('options', "")
    dob = request.form.get('dob', "")
    occupation = request.form.get('occupation', "")

    session.pop('ret_msg', None)

    occupations =[]
    occupations.append("--Select--")
    occupations.append("Student")
    occupations.append("Politician")
    occupations.append("Engineer")
    occupations.append("Teacher")

    start = 1900
    end = 2020

    years = []
    years.append("--Select--")

    for i in range(end - start):
        years.append(start + i)

    # empty input check
    if username == "" or password == "" or confirm_password == "" or sex == "" or dob == "--Select--" or occupation == "--Select--":
        ret_msg = "Error: All fields are required!"
        return render_template("register.html", ret_msg=ret_msg, username=username, password=password,
                               confirm_password=confirm_password, sex=sex, dob=dob, years=years, occupations=occupations,
                               hidden="visible")

    if password != confirm_password:
        ret_msg = "Error: Passwords are not equal"
        return render_template("register.html", ret_msg=ret_msg, username=username, password="", confirm_password="",
                               sex=sex, dob=dob, years=years, occupations=occupations, hidden="visible")

    # input string validation
    for c in username:
        if c not in username_char:
            ret_msg = "Error: Username must not contain character: " + c
            return render_template("register.html", ret_msg=ret_msg, username=username, password="",
                                   confirm_password="", years=years, occupations=occupations,
                                   hidden="visible")
    for c in password:
        if c not in password_char:
            ret_msg = "Error: Password must not contain character: " + c
            return render_template("register.html", ret_msg=ret_msg, username=username, password="",
                                    confirm_password="", years=years, occupations=occupations,
                                    hidden = "visible")

    salt = generate_salt()
    hashed_password = generate_password_hash(password + salt)

    key = {'username': username}
    item = db_read(USERS, key)

    if item != None:
        ret_msg = "Error: Username has been used"
        return render_template("register.html", ret_msg=ret_msg, username="", password="",
                               confirm_password="", years=years, occupations=occupations,
                               hidden="visible")

    if 'profile_image' not in request.files:
        ret_msg = "Error: File is empty "
        return render_template("register.html", ret_msg=ret_msg,hidden="visible")
    file = request.files['profile_image']

    if file.filename == '':
        ret_msg = "Error: Filename is empty"
        return render_template("register.html", ret_msg=ret_msg, username=username, password="",
                               confirm_password="", years=years, occupations=occupations,
                               hidden="visible")

    ext = get_image_extension(file.filename)
    if ext == '':
        ret_msg = "Error: Filename does not have extension"
        return render_template("register.html", ret_msg=ret_msg, username=username, password="",
                               confirm_password="", years=years, occupations=occupations,
                               hidden="visible")

    ts = time.time()
    # file.filename = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S') + file.filename
    file.filename = 'profile_image/' + username + ext

    image_src = upload_file_to_s3(file)

    attributes = ['dob', 'sex', 'occupation']
    item = {'username': username,
            'salt': salt,
            'password': hashed_password,
            'polls': [],
            'votes': [],
            'attributes': attributes,
            'dob': dob,
            'sex': sex,
            'occupation': occupation,
            'profile_image':image_src}
    db_write(USERS, item)

    # record usernmae in the active session
    session['username'] = username
    return redirect(url_for('main'))

@webapp.route('/change_password', methods=['POST'])
def change_password():

    username = session['username']
    password = request.form.get('password', "")
    confirm_password = request.form.get('confirm_password', "")

    key = {'username': username}
    item = db_read(USERS, key)
    session.pop('ret_msg', None)

    # empty input check
    if password == "" or confirm_password == "":
        ret_msg = "Error: All fields are required!"
        return render_template("account.html", ret_msg=ret_msg, username=username, password=password,
                               confirm_password=confirm_password, item=item, hidden="visible")

    if password != confirm_password:
        ret_msg = "Error: Passwords are not equal"
        return render_template("account.html", ret_msg=ret_msg, username=username, password="",
                               confirm_password="", item=item, hidden="visible")

    for c in password:
        if c not in password_char:
            ret_msg = "Error: Password must not contain character: " + c
            return render_template("account.html", ret_msg=ret_msg, username=username, password="",
                                   confirm_password="", item=item, hidden="visible")

    salt = generate_salt()
    hashed_password = generate_password_hash(password + salt)

    item['salt'] = salt
    item['password'] = hashed_password
    db_write(USERS, item)

    session['ret_msg'] = "Success: Password has been changed."
    return redirect(url_for('account'))
