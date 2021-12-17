#!/usr/bin/env python3

from flask import Flask, Response, render_template, session, request, redirect, url_for
import requests
import json
from typing import List
from datetime import datetime
from dataclasses import dataclass

import roommate as rm
import devices as devs

#  import all the necessary data classes.
#  Roomate, Device, more to come


DEVS = "devices/"
DEV_CONFIG = f"{DEVS}config.json"


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
    devices = prepare_devices()
    return render_template('device_info.html', devices=devices)


#  === BACKEND LOGIC ===
@dataclass
class Prepared:
    room: str
    type: str
    state: str
    uptime: str

    @classmethod
    def load(cls, type: str, room: str, file: str) -> "Prepared":
        p: Prepared
        with open(file, "r") as f:
            loaded_json = json.load(f)
        if type == "smart_light":
            dev = devs.SmartLight.from_json(loaded_json)
            state = "ON" if dev.current_state else "OFF"
            p = Prepared(room.capitalize(), dev.type, state, get_time(dev.power_usage))
        elif type == "switch_sensor":
            dev = devs.SwitchSensor.from_json(loaded_json)
            state = "ON" if dev.current_state else "OFF"
            p = Prepared(room.capitalize(), dev.type, state, get_time(dev.power_usage))
        elif type == "motion_sensor":
            dev = devs.MotionSensor.from_json(loaded_json)
            p = Prepared(room.capitalize(), dev.type, "---", "---")
        return p


def prepare_devices() -> List[Prepared]:
    prepped_devices = list()
    with open(DEV_CONFIG, "r") as f:
        d = json.load(f)
        for room in d.keys():
            for type, id in d[room].items():
                if id:
                    prepped_devices.append(Prepared.load(type, room, f"{DEVS}{id}.json"))
    return prepped_devices


def get_time(time: int) -> str:
    min, sec = divmod(time, 60)
    hour, min = divmod(min, 60)
    return "%d:%02d:%02d" % (hour, min, sec)


def main() -> None:
    app.debug = True
    app.secret_key = "very secret secret key"
    app.run()


if __name__ == "__main__":
    main()
