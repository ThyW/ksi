#!/usr/bin/env python3

from flask import Flask, Response, render_template, session, request, redirect, url_for
import requests
import json
from typing import Union

import roommate as rm

#  import all the necessary data classes.
#  Roomate, Device, more to come


app = Flask(__name__, template_folder="templates")


@app.route('/')
def index() -> str:
    user = session.get("user") or None
    error = session.get("error") or None
    info = session.get("info") or None
    template = render_template('home.html', user=user, error=error, info=info)
    return template


@app.route('/overview')
def overview() -> str:
    return render_template('overview.html')


@app.route('/login', methods=['GET', 'POST'])
def login() -> str:
    if request.method == "POST":
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")
        if user := rm.load_roommate(username):
                session["auth"] = "true"
                session["user"] = username
                session["userdata"] = user
                return redirect("/")
        session["error"] = "Invalid username or password!"
        return redirect("/")
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup() -> str:
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            r = rm.Roommate.new(username, password)
            rm.save_roommate(r)
            session["info"] = f"New user created: {username}!"
            return redirect('/')
        else:
            session["error"] = "Username or password is missing!"
            return redirect('/')
    return render_template('signup.html')


@app.route('/logout')
def logout() -> str:
    if session.get("user"):
        session.pop("user", None)
        session.pop("userdata", None)
        session["auth"] = "false"
        return redirect('/')
    else:
        session["error"] = "You are not logged in!"
        return redirect('/')


@app.route('/buttons')
def buttons() -> str:
    return render_template('buttons.html')


@app.route('/device_info')
def device_info() -> str:
    return render_template('device_info.html')


def main() -> None:
    app.debug = True
    app.secret_key = "very secret secret key"
    app.run()


if __name__ == "__main__":
    main()
