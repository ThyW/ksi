#!/usr/bin/env python3

import devices as devs
from devices import Device
import requests
import json
import urllib.parse as up
import os

from typing import List, Optional


NUM_MOTION_SENSORS: int = 2
NUM_ROOMS: int = 7
PATH = "devices/"
CONFIG_NAME = "config.json"
URL = "https://home_automation.iamroot.eu/"
ROOMS = [
        "kuchyna",
        "kupelna",
        "obyvak",
        "sob_karsob",
        "karlik",
        "zelvicka_julie",
        "los_karlos"
        ]


def create_dirs() -> None:
    if os.path.exists(PATH):
        return
    else:
        os.makedirs(PATH)
        os.makedirs("users/")


def get_device_for_id(id: str, device_list: List[Device]) -> Optional[Device]:
    for each in device_list:
        if each.id == id:
            return each
    return None


def get_devices() -> List[Device]:
    dev_list = []
    for _ in range(NUM_MOTION_SENSORS):
        r = requests.get(f"{URL}newMotionSensor")
        dev = devs.MotionSensor.from_dict(r.json())
        dev_list.append(dev)
        # print(f"MOTION SENSOR: {dev.to_json()}")
        print("[INFO] Motion senser fetched successfully!")
    for _ in range(NUM_ROOMS):
        r = requests.get(f"{URL}newSmartLight")
        j = str(r.json())
        j = j.replace("'", '"')
        j = j.replace("False", "false")
        j = j.replace("True", "true")
        dev = devs.SmartLight.from_json(j)
        dev_list.append(dev)
        print("[INFO] Smart light fetched successfully!")

        r1 = requests.get(f"{URL}newSwitchSensor")
        j = str(r1.json())
        j = j.replace("'", '"')
        j = j.replace("False", "false")
        j = j.replace("True", "true")
        dev1 = devs.SwitchSensor.from_json(j)
        dev_list.append(dev1)
        print("[INFO] Switch sensor fetched successfully!")
    return dev_list


def write_devices(device_list: List[Device]) -> None:
    for each in device_list:
        with open(f"{PATH}{each.id}.json", "w+") as f:
            jsn = each.to_json()
            json.dump(jsn, f)
            f.close()


def create_config(devices_list: List[Device]) -> None:
    config = dict()
    for room in ROOMS:
        config[room] = dict()
        config[room]["motion_sensor"] = None
        config[room]["smart_light"] = None
        config[room]["switch_sensor"] = None
    for each in devices_list:
        if each.type == devs.DeviceType.MOTION_SENSOR:
            room = "kuchyna" if config["kuchyna"]["motion_sensor"] is None\
                    else "obyvak"
            config[room]["motion_sensor"] = each.id
            note = f"{{room: {room}}}"
            requests.post(f"{URL}device/{each.id}notes", data=note)
            each.notes = note
        else:
            for room in config.keys():
                if each.type == devs.DeviceType.SMART_LIGHT:
                    if config[room]["smart_light"] is None:
                        config[room]["smart_light"] = each.id
                        note = f"{{room: {room}}}"
                        requests.post(f"{URL}device/{each.id}notes", data=note)
                        each.notes = note
                        break
                elif each.type == devs.DeviceType.SWITCH_SENSOR:
                    if config[room]["switch_sensor"] is None:
                        config[room]["switch_sensor"] = each.id
                        note = f"{{room: {room}}}"
                        requests.post(f"{URL}device/{each.id}notes", data=note)
                        each.notes = note
                        break
    for room in config:
        if config[room].get("motion_sensor") is not None:
            # if there is a motion sensor:
            # motion sensor trigger -> switch_trigger -> light on
            ms = get_device_for_id(config[room]["motion_sensor"], devices_list)
            ss = get_device_for_id(config[room]["switch_sensor"], devices_list)
            sl = get_device_for_id(config[room]["smart_light"], devices_list)

            if ms and ss and sl:
                ss_quoted_url = up.quote_plus(sl.actions["toggle_state"])
                ms_quoted_url = up.quote_plus(sl.actions["turn_on"])
                ms_new_collector_url = f"{URL}device/{ms.id}\
                                       /report_url?url={ms_quoted_url}"
                ss_new_collector_url = f"{URL}/device/{ss.id}\
                                       /report_url?url={ss_quoted_url}"

                requests.post(ms_new_collector_url)
                requests.post(ss_new_collector_url)

                ms.collector_url = sl.actions["turn_on"]
                ms.actions["change_report_url"] = ms_new_collector_url
                ss.collector_url = sl.actions["toggle_state"]
                ss.actions["change_report_url"] = ss_new_collector_url
        else:
            ss = get_device_for_id(config[room]["switch_sensor"], devices_list)
            sl = get_device_for_id(config[room]["smart_light"], devices_list)

            if ss and sl:
                ss_quoted_url = up.quote_plus(sl.actions["toggle_state"])
                ss_new_collector_url = f"{URL}/device/{ss.id}\
                                       /report_url?url={ss_quoted_url}"

                requests.post(ss_new_collector_url)

                ss.collector_url = sl.actions["toggle_state"]
                ss.actions["change_report_url"] = ss_new_collector_url

    with open(f"{PATH}{CONFIG_NAME}", "w") as f:
        json.dump(config, f)
    write_devices(devices_list)


def setup():
    create_dirs()
    devices = get_devices()
    create_config(devices)


setup()
