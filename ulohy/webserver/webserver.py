#!/usr/bin/env python3

from flask import Flask, render_template, session, request, redirect, url_for
import requests
import json
from typing import List, Any, Dict, Tuple, Union, Optional
from datetime import datetime, time
from dataclasses import dataclass

import roommate as rm
import devices as devs
from devices import Device

#  import all the necessary data classes.
#  Roomate, Device, more to come


DEVS = "devices/"
DEV_CONFIG = f"{DEVS}config.json"
URL = "https://home_automation.iamroot.eu/"
AMOUNT_PER_MINUTE = 4200/90
SUNRISE_S = time(5, 0, 0)
SUNRISE_E = time(6, 30, 0)
SUNSET_S = time(16, 0, 0)
SUNSET_E = time(17, 30, 0)


app = Flask(__name__, template_folder="templates")


@app.route('/')
def index():
    user = session.get("user") or None
    error = session.get("error") or None
    info = session.get("info") or None
    template = render_template('home.html', user=user, error=error, info=info)
    session.pop("error", None)
    return template


@app.route('/overview')
def overview():
    sync_devices()
    data = costs()
    return render_template('overview.html', cost_data=data)


@app.route('/map')
def my_map():
    sync_devices()
    lights = get_lights()
    return render_template('my_map.html', lights=lights)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            if user := rm.load_roommate(username):
                if user.passwd == password:
                    session["auth"] = "true"
                    session["user"] = username
                    session["userdata"] = user
                    return redirect("/")
                else:
                    session["error"] = "Invalid username or password!"
            return redirect("/")
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        room = request.form.get("room")
        if username and password and room:
            r = rm.Roommate.new(username, password, room)
            rm.save_roommate(r)
            session["info"] = f"New user created: {username}!"
            return redirect('/')
        else:
            session["error"] = "Username or password is missing!"
            return redirect('/')
    return render_template('signup.html')


@app.route('/logout')
def logout():
    if session.get("user"):
        session.pop("user", None)
        session.pop("userdata", None)
        session["auth"] = "false"
        return redirect('/')
    else:
        session["error"] = "You are not logged in!"
        return redirect('/')


@app.route('/buttons', methods=["GET", "POST"])
def buttons():
    if request.method == "GET":
        sync_devices()
        if session.get("auth") == "true":
            available = devices_for(session["userdata"])
            return render_template('buttons.html', available=available)
        else:
            session["error"] = "You are not logged in. Log in first, please!"
            return redirect("/")
    if request.method == "POST":
        for each in request.form:
            s1, s2 = each.split("_")
            device = load_device(s1)
            if s2 == "on":
                requests.post(device.actions["turn_on"])
                device.current_state = True
            if s2 == "off":
                requests.post(device.actions["turn_off"])
                device.current_state = False
            save_device(device)
        available = devices_for(session["userdata"])
        return render_template('buttons.html', available=available)



@app.route('/device_info')
def device_info():
    sync_devices()
    device_list = prepare_devices()
    return render_template('device_info.html', device_list=device_list)


@app.route('/device/<device_id>')
def device(device_id: str):
    device = load_device(device_id)
    if not device:
        return ("Unknown device, code: 400")
    jsn = json.loads(device.to_json())
    jsn["actions"] = "[REDACTED]"
    jsn["collector_url"] = "[REDACTED]"
    return jsn


@app.route('/cron')
def cron() -> None:
    now = datetime.now().time()
    if in_time_range(SUNRISE_S, SUNRISE_E, now):
        manage_lights(AMOUNT_PER_MINUTE, True)
    if in_time_range(SUNSET_S, SUNSET_E, now):
        manage_lights(AMOUNT_PER_MINUTE, False)

#  === BACKEND LOGIC ===
@dataclass
class Prepared:
    room: str
    type: str
    state: str
    temp: str
    uptime: str
    id: str

    @classmethod
    def load(cls, type: str, room: str, file: str) -> "Prepared":
        p: Prepared
        with open(file, "r") as f:
            loaded_json = json.load(f)
        if type == "smart_light":
            dev = devs.SmartLight.from_json(loaded_json)
            state = "ON" if dev.current_state else "OFF"
            p = Prepared(room.capitalize(), dev.type.value, state, f"{str(dev.color_temperature)}K", get_time(dev.power_usage), dev.id)
        elif type == "switch_sensor":
            dev = devs.SwitchSensor.from_json(loaded_json)
            state = "ON" if dev.current_state else "OFF"
            p = Prepared(room.capitalize(), dev.type.value, state, "---", get_time(dev.power_usage), dev.id)
        elif type == "motion_sensor":
            dev = devs.MotionSensor.from_json(loaded_json)
            p = Prepared(room.capitalize(), dev.type.value, "---", "---", "---", dev.id)
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


def get_lights() -> Dict[str, Prepared]:
    ret = dict()
    with open(DEV_CONFIG, "r") as f:
        d = json.load(f)
        for room in d.keys():
            id = d[room]["smart_light"]
            ret[room] = Prepared.load("smart_light", room, f"{DEVS}{id}.json")
    return ret


def get_time(time: int) -> str:
    min, sec = divmod(time, 60)
    hour, min = divmod(min, 60)
    return "%d:%02d:%02d" % (hour, min, sec)


def load_device(id: str, config=None) -> Optional[Device]:
    fname = f"{DEVS}{id}.json"
    if not config:
        with open(DEV_CONFIG, "r") as f:
            config = json.load(f)
    for room in config.keys():
        if config[room]["motion_sensor"] == id:
            with open(fname, "r") as f2:
                d = devs.MotionSensor.from_json(json.load(f2))
                return d
        if config[room]["switch_sensor"] == id:
            with open(fname, "r") as f2:
                d = devs.SwitchSensor.from_json(json.load(f2))
                return d
        if config[room]["smart_light"] == id:
            with open(fname, "r") as f2:
                d = devs.SmartLight.from_json(json.load(f2))
                return d
    return None


def save_device(device: Device):
    with open(f"{DEVS}{device.id}.json", "w") as f:
        json.dump(device.to_json(), f)


def sync_devices():
    with open(DEV_CONFIG) as f:
        config = json.load(f)
    for room in config.keys():
        for each in config[room]:
            id = config[room][each]
            if id != None:
                path = f"{DEVS}{id}.json"
                device_json = requests.get(f"{URL}device/{id}").json()
                j = str(device_json)
                j = j.replace("'", '"')
                j = j.replace("True", "true")
                j = j.replace("False", "false")
                with open(f"{path}", "w") as f2:
                    json.dump(j, f2)


def devices_for(user: rm.Roommate) -> Dict[str, Tuple[bool, Device]]:
    with open(DEV_CONFIG, "r") as f:
        dct = json.load(f)
    available_rooms = []
    return_list = dict()

    for room in dct.keys():
        if room == "kuchyna" or room == "kupelna" or room == "obyvak":
            available_rooms.append(room)
        elif room == user["room"]:
            available_rooms.append(room)

    for room in available_rooms:
        device_id = dct[room]["smart_light"]
        device = load_device(device_id, config=dct)
        return_list[room] = (True, device)

    diff = list(set(dct.keys()) - set(available_rooms))

    for room in diff:
        device_id = dct[room]["smart_light"]
        device = load_device(device_id, config=dct)
        return_list[room] = (False, device)

    return return_list


def in_time_range(start, end, now) -> bool:
        if start <= end:
            return start <= now <= end
        else:
            return start <= now or now <= end


def manage_lights(step: float, increase: bool):
    with open(DEV_CONFIG, "r") as f:
        config = json.load(f)
    for room in config.keys():
        for each in config[room]:
            if each == "smart_light":
                id = config[room][each]
                fname = f"{DEVS}{id}.json"
                with open(fname, "r") as f2:
                    if increase:
                        dev = devs.SmartLight.from_json(json.load(f2))
                        dev.color_temperature += int(step) if dev.color_temperature < 6500 else 0
                        requests.get(f"{URL}device/{id}/color_temperature/{dev.color_temperature}")
                    else:
                        dev = devs.SmartLight.from_json(json.load(f2))
                        dev.color_temperature -= int(step) if dev.color_temperature > 2300 else 0
                        requests.get(f"{URL}device/{id}/color_temperature/{dev.color_temperature}")


def costs() -> Dict[str, float]:
    ret = dict()
    with open(DEV_CONFIG, "r") as f:
        config = json.load(f)
    devices = dict()
    for room in config.keys():
        switch_id = config[room]["switch_sensor"]
        light_id = config[room]["smart_light"]
        switch = load_device(switch_id)
        light = load_device(light_id)
        devices[room] = list()

        devices[room].append(switch)
        devices[room].append(light)
    sum_all = 0
    for each in devices.keys():
        sum_all += sum([x.power_usage for x in devices[each]])
    people = ["sob_karsob", "karlik", "zelvicka_julie", "los_karlos"]
    sum_people = sum(x[z].power_usage for z in range(2) 
                     for a, x in devices.items() if a in people)
    for each in people:
        energy = int(sum([x.power_usage for x in devices[each]]))
        bill = energy / sum_people * 100
        print(sum_all, energy)
        ret[each] = round(bill, 2)

    sorted_dict = dict(sorted(ret.items(), key=lambda x:x[1], reverse=True))
    print(sorted_dict)
    d = dict()

    for key, value in sorted_dict.items():
        key = key.replace("_", " ")
        keys = key.split(" ")
        key = ""
        for each in keys:
            key += " "
            key += each.capitalize() 
        d[key] = value
    return d


def main() -> None:
    app.debug = True
    app.secret_key = "very secret secret key"
    app.run()


if __name__ == "__main__":
    main()
